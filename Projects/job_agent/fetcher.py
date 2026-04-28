import hashlib
import json
import re
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup
from jobspy import scrape_jobs

from config import (
    DISTANCE_KM,
    EXCLUDE_TERMS,
    LOCATION,
    MAX_HOURS_OLD,
    RESULTS_PER_TERM,
    SEARCH_TERMS,
    SECONDARY_TERMS,
)

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

# Regex patterns — each must match for the title to pass
# Designed to avoid false positives like "Bar Manager", "Refrigeration Technician", "Tax Manager"
_TITLE_PATTERNS = [
    r"\bit\b",                          # whole word "IT"
    r"\bcto\b", r"\bcio\b", r"\bpmo\b",
    r"head of (it|tech|infrastr|cloud|security|digital|netzwerk|network)",
    r"it[-\s](manager|leiter|direktor|director|consultant|berater|leitung"
    r"|sicherheit|security|infrastruktur|infrastructure|operations"
    r"|service|projekt|portfolio|strateg|governance|architekt|architect)",
    r"(abteilungsleiter|gruppenleiter|teamleiter).{0,20}\bit\b",
    r"\bit\b.{0,20}(abteilungsleiter|gruppenleiter|teamleiter)",
    r"projektleiter|projektmanager",
    r"enterprise\s+architect|solution\s+architect|software\s+architekt"
    r"|cloud\s+architect|security\s+architect|it[-\s]architekt",
    r"devops.*(manager|lead|leiter|director)",
    r"cybersecurity|cyber\s+security",
    r"digital\s+transformat|digitalisierung|digitali[sz]ation",
    r"\bitil\b|\bitsm\b",
    r"iso\s*27001",
    r"netzwerk.*(manager|leiter|architekt)|network.*(manager|architect|lead)",
    r"cloud.*(manager|leiter|architekt|infrastructure)",
    r"infrastructure.*(manager|director|lead|head)",
]

_COMPILED = [re.compile(p, re.IGNORECASE) for p in _TITLE_PATTERNS]


def _job_id(title: str, company: str, url: str) -> str:
    raw = f"{title.lower().strip()}|{company.lower().strip()}|{url.strip()}"
    return hashlib.md5(raw.encode()).hexdigest()


def _is_excluded(title: str) -> bool:
    return any(term in title.lower() for term in EXCLUDE_TERMS)


def _passes_title_filter(title: str) -> bool:
    return any(p.search(title) for p in _COMPILED)


def _make_job(title, company, location, url, description, source) -> dict:
    return {
        "id": _job_id(title, company, url),
        "title": title,
        "company": company,
        "location": location,
        "url": url,
        "description": description[:3000],
        "source": source,
    }


# ── jobspy (LinkedIn + Indeed) ────────────────────────────────────────────────

def _scrape_one_term(term: str, sites: list[str], location: str, extra_kwargs: dict) -> list[dict]:
    try:
        df = scrape_jobs(
            site_name=sites,
            search_term=term,
            location=location,
            distance=DISTANCE_KM,
            results_wanted=RESULTS_PER_TERM,
            hours_old=MAX_HOURS_OLD,
            linkedin_fetch_description=True,
            **extra_kwargs,
        )
    except Exception as e:
        print(f"  [warn] '{term}' on {sites}: {e}")
        return []

    jobs = []
    for _, row in df.iterrows():
        title = str(row.get("title", ""))
        company = str(row.get("company", ""))
        url = str(row.get("job_url", ""))
        if not title or not company:
            continue
        if _is_excluded(title) or not _passes_title_filter(title):
            continue
        jobs.append(_make_job(
            title, company,
            str(row.get("location", "")),
            url,
            str(row.get("description", "")),
            str(row.get("site", sites[0])),
        ))
    return jobs


def _fetch_jobspy_parallel(terms: list[str], sites: list[str], location: str, extra_kwargs: dict = {}) -> list[dict]:
    seen_urls: set[str] = set()
    all_jobs: list[dict] = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(_scrape_one_term, t, sites, location, extra_kwargs): t for t in terms}
        for future in as_completed(futures):
            for job in future.result():
                if job["url"] not in seen_urls:
                    seen_urls.add(job["url"])
                    all_jobs.append(job)
    return all_jobs


# ── Stepstone scraper ─────────────────────────────────────────────────────────

def _fetch_stepstone(terms: list[str]) -> list[dict]:
    jobs: list[dict] = []
    seen_urls: set[str] = set()

    for term in terms:
        slug = term.replace(" ", "-").lower()
        url = f"https://www.stepstone.de/jobs/{urllib.parse.quote(slug)}/in-berlin.html"
        try:
            resp = requests.get(url, headers=_HEADERS, timeout=15)
            soup = BeautifulSoup(resp.text, "html.parser")

            # Stepstone embeds structured JSON-LD job data in <script> tags
            for script in soup.find_all("script", type="application/ld+json"):
                try:
                    data = json.loads(script.string or "")
                except Exception:
                    continue

                items = data if isinstance(data, list) else [data]
                for item in items:
                    if item.get("@type") != "JobPosting":
                        continue
                    title = item.get("title", "")
                    org = item.get("hiringOrganization", {})
                    company = org.get("name", "Unknown") if isinstance(org, dict) else "Unknown"
                    job_url = item.get("url", url)
                    description = item.get("description", "")
                    location = "Berlin"

                    if not title or not job_url:
                        continue
                    if _is_excluded(title) or not _passes_title_filter(title):
                        continue
                    if job_url in seen_urls:
                        continue
                    seen_urls.add(job_url)
                    jobs.append(_make_job(title, company, location, job_url, description, "stepstone"))

        except Exception as e:
            print(f"  [stepstone] Error for '{term}': {e}")

    return jobs


# ── Jobware scraper ───────────────────────────────────────────────────────────

def _fetch_jobware(terms: list[str]) -> list[dict]:
    jobs: list[dict] = []
    seen_urls: set[str] = set()

    for term in terms:
        url = (
            f"https://www.jobware.de/suche/stellen/"
            f"?was={urllib.parse.quote(term)}&wo=Berlin&umkreis=30"
        )
        try:
            resp = requests.get(url, headers=_HEADERS, timeout=15)
            soup = BeautifulSoup(resp.text, "html.parser")

            for article in soup.find_all("article", class_=re.compile(r"job")):
                title_el = article.find(["h2", "h3", "a"])
                title = title_el.get_text(strip=True) if title_el else ""
                link_el = article.find("a", href=True)
                job_url = link_el["href"] if link_el else ""
                if job_url and not job_url.startswith("http"):
                    job_url = "https://www.jobware.de" + job_url
                company_el = article.find(class_=re.compile(r"company|employer|arbeitgeber", re.I))
                company = company_el.get_text(strip=True) if company_el else "Unknown"

                if not title or not job_url:
                    continue
                if _is_excluded(title) or not _passes_title_filter(title):
                    continue
                if job_url in seen_urls:
                    continue
                seen_urls.add(job_url)
                jobs.append(_make_job(title, company, "Berlin", job_url, "", "jobware"))

        except Exception as e:
            print(f"  [jobware] Error for '{term}': {e}")

    return jobs


# ── orchestrator ──────────────────────────────────────────────────────────────

def fetch_all_jobs() -> list[dict]:
    all_jobs: list[dict] = []
    all_terms = SEARCH_TERMS + SECONDARY_TERMS

    def _run(label, fn, *args, **kwargs):
        print(f"[fetcher] {label}...")
        result = fn(*args, **kwargs)
        print(f"  → {len(result)} jobs")
        return result

    # LinkedIn + Indeed run in parallel
    with ThreadPoolExecutor(max_workers=2) as pool:
        f_linkedin = pool.submit(_run, "LinkedIn",   _fetch_jobspy_parallel, all_terms, ["linkedin"], LOCATION)
        f_indeed   = pool.submit(_run, "Indeed.de",  _fetch_jobspy_parallel, all_terms, ["indeed"],   "Berlin", {"country_indeed": "germany"})
        all_jobs += f_linkedin.result()
        all_jobs += f_indeed.result()

    # Stepstone + Jobware scrapers (sequential — polite to their servers)
    all_jobs += _run("Stepstone", _fetch_stepstone, SEARCH_TERMS)
    all_jobs += _run("Jobware",   _fetch_jobware,   SEARCH_TERMS)

    # deduplicate
    seen_ids: set[str] = set()
    unique = [j for j in all_jobs if not (seen_ids.add(j["id"]) if j["id"] not in seen_ids else True)]  # type: ignore

    print(f"[fetcher] Total unique jobs after dedup: {len(unique)}")
    return unique
