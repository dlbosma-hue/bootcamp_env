import hashlib
import json
import re
import time
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

from bs4 import BeautifulSoup
from jobspy import scrape_jobs
from playwright.sync_api import sync_playwright

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

# Regex patterns — at least one must match for the title to pass.
# Designed to accept PM/AI/Consulting titles while rejecting pure engineering roles.
_TITLE_PATTERNS = [
    r"\bproduct\s+manager\b",
    r"\bproduct\s+owner\b",
    r"\bproduktmanager\b",
    r"\bprogramm?(?:e)?\s+manager\b",
    r"\bhead\s+of\s+product\b",
    r"\blead\b.{0,20}\bproduct\b|\bproduct\b.{0,20}\blead\b",
    r"\bprincipal\s+product\b",
    r"\bstaff\s+product\b",
    r"\bai\s+(?:product|strategy|consultant|manager|berater|advisor|lead|architect)\b",
    r"\bki[\s-](?:berater|produktmanager|strateg|consultant|manager|experte)\b",
    r"\bml\s+(?:product|platform)\s+manager\b",
    r"\btechnical\s+product\b",
    r"\bdigital\s+product\b",
    r"\bplatform\s+(?:product\s+)?manager\b",
    r"(?:ai|ki|digital|automation|tech)\s+consultant\b",
    r"\bconsultant\b.{0,30}(?:\bai\b|\bki\b|\bdigital\b|\bautomation\b|\bproduct\b)",
    r"\bprompt\s+engin",
    r"\bagentic\b",
    r"\bllm\b.{0,30}(?:manager|product|lead|consultant)",
]

_COMPILED = [re.compile(p, re.IGNORECASE) for p in _TITLE_PATTERNS]


def _job_id(title: str, company: str, url: str) -> str:
    raw = f"{title.lower().strip()}|{company.lower().strip()}|{url.strip()}"
    return hashlib.md5(raw.encode()).hexdigest()


def _is_excluded(title: str) -> bool:
    t = title.lower()
    return any(term in t for term in EXCLUDE_TERMS)


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
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(_scrape_one_term, t, sites, location, extra_kwargs): t for t in terms}
        for future in as_completed(futures):
            for job in future.result():
                if job["url"] not in seen_urls:
                    seen_urls.add(job["url"])
                    all_jobs.append(job)
    return all_jobs


def _fetch_linkedin_sequential(terms: list[str], location: str) -> list[dict]:
    """LinkedIn rate-limits aggressively — run sequentially with a pause."""
    seen_urls: set[str] = set()
    all_jobs: list[dict] = []
    for term in terms:
        for job in _scrape_one_term(term, ["linkedin"], location, {}):
            if job["url"] not in seen_urls:
                seen_urls.add(job["url"])
                all_jobs.append(job)
        time.sleep(3)
    return all_jobs


# ── Playwright helpers ────────────────────────────────────────────────────────

def _parse_jsonld_jobs(html: str, fallback_url: str, source: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    jobs = []
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
            job_url = item.get("url", fallback_url)
            description = item.get("description", "")
            if title and job_url:
                jobs.append(_make_job(title, company, "Berlin", job_url, description, source))
    return jobs


# ── Xing scraper (Playwright) ────────────────────────────────────────────────
# Job cards render client-side. Selectors confirmed from live DOM inspection:
#   card:    [data-testid="job-search-result"]
#   title:   [data-testid="job-teaser-list-title"]
#   company: [class*="Company"]  (CSS-module class, substring match is stable)
#   link:    a[href]  (relative path, prefix https://www.xing.com)

def _fetch_xing(terms: list[str]) -> list[dict]:
    jobs: list[dict] = []
    seen_urls: set[str] = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"],
        )
        ctx = browser.new_context(
            user_agent=_HEADERS["User-Agent"],
            extra_http_headers={"Accept-Language": "de-DE,de;q=0.9"},
        )
        ctx.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        page = ctx.new_page()

        for term in terms:
            url = (
                f"https://www.xing.com/jobs/search"
                f"?keywords={urllib.parse.quote(term)}&location=Berlin&radius=30"
            )
            try:
                page.goto(url, wait_until="networkidle", timeout=35000)
                try:
                    page.wait_for_selector("[data-testid='job-search-result']", timeout=10000)
                except Exception:
                    pass
                html = page.content()
                soup = BeautifulSoup(html, "lxml")

                for card in soup.select("[data-testid='job-search-result']"):
                    title_el   = card.select_one("[data-testid='job-teaser-list-title']")
                    link_el    = card.select_one("a[href]")
                    company_el = card.select_one("[class*='Company']")

                    title   = title_el.get_text(strip=True)  if title_el   else ""
                    company = company_el.get_text(strip=True) if company_el else "Unknown"
                    href    = link_el["href"] if link_el else ""
                    job_url = href if href.startswith("http") else f"https://www.xing.com{href}"

                    if not title or not job_url:
                        continue
                    if _is_excluded(title) or not _passes_title_filter(title):
                        continue
                    if job_url in seen_urls:
                        continue
                    seen_urls.add(job_url)
                    jobs.append(_make_job(title, company, "Berlin", job_url, "", "xing"))

            except Exception as e:
                print(f"  [xing] '{term}': {e}")

        browser.close()
    return jobs


# ── Stepstone scraper (Playwright) ───────────────────────────────────────────
# Search results page has job cards with data-at attributes.
# Each card has title, company, and a link — no JSON-LD on the listing page.
# URL format: /jobs/?q={term}&l=Berlin (old /jobs/{slug}/in-berlin.html is 410 Gone)

def _fetch_stepstone(terms: list[str]) -> list[dict]:
    jobs: list[dict] = []
    seen_urls: set[str] = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(user_agent=_HEADERS["User-Agent"])
        page = ctx.new_page()

        for term in terms:
            url = f"https://www.stepstone.de/jobs/?q={urllib.parse.quote(term)}&l=Berlin&radius=30"
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
                try:
                    page.wait_for_selector("[data-at='job-item']", timeout=10000)
                except Exception:
                    pass
                html = page.content()
                soup = BeautifulSoup(html, "lxml")

                for card in soup.select("[data-at='job-item']"):
                    title_el = card.select_one("[data-at='job-item-title']")
                    company_el = card.select_one("[data-at='job-item-company-name']")
                    link_el = card.select_one("a[href]")

                    title = title_el.get_text(strip=True) if title_el else ""
                    company = company_el.get_text(strip=True) if company_el else "Unknown"
                    href = link_el["href"] if link_el else ""
                    job_url = href if href.startswith("http") else f"https://www.stepstone.de{href}"

                    if not title or not job_url:
                        continue
                    if _is_excluded(title) or not _passes_title_filter(title):
                        continue
                    if job_url in seen_urls:
                        continue
                    seen_urls.add(job_url)
                    jobs.append(_make_job(title, company, "Berlin", job_url, "", "stepstone"))

            except Exception as e:
                print(f"  [stepstone] '{term}': {e}")

        browser.close()
    return jobs


# ── Jobware scraper (Playwright API interception) ────────────────────────────
# Jobware blocks direct requests (403). Load the page via Playwright and
# intercept the internal xnfwe API response which carries the job listings.

_JOBWARE_BASE = "https://www.jobware.de/"
_JW_REMOTE_TYPES = {"homeoffice option", "home office", "remote"}


def _parse_jobware_response(data: dict, seen_ids: set) -> list[dict]:
    jobs = []
    for item in data.get("data", []):
        title = item.get("title", "")
        company = item.get("advertiser", {}).get("name", "Unknown")
        location = item.get("location", "")
        job_url = item.get("url", "")
        if job_url and not job_url.startswith("http"):
            job_url = _JOBWARE_BASE + job_url
        description = item.get("task", "")
        job_id = str(item.get("id", ""))

        jobtypes = {jt.get("name", "").lower() for jt in item.get("jobtypes", [])}
        is_remote = bool(jobtypes & _JW_REMOTE_TYPES)

        if not is_remote and "berlin" not in location.lower():
            continue
        if not title or not job_url:
            continue
        if _is_excluded(title) or not _passes_title_filter(title):
            continue
        if job_id in seen_ids:
            continue
        seen_ids.add(job_id)
        jobs.append(_make_job(title, company, location, job_url, description, "jobware"))
    return jobs


def _fetch_jobware(terms: list[str]) -> list[dict]:
    jobs: list[dict] = []
    seen_ids: set[str] = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"],
        )
        ctx = browser.new_context(
            user_agent=_HEADERS["User-Agent"],
            extra_http_headers={"Accept-Language": "de-DE,de;q=0.9"},
        )
        ctx.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        page = ctx.new_page()

        for term in terms:
            captured: list[dict] = []

            def on_response(response, _captured=captured):
                if "xnfwe" in response.url and response.status == 200:
                    try:
                        _captured.append(response.json())
                    except Exception:
                        pass

            page.on("response", on_response)
            search_url = (
                f"https://www.jobware.de/jobsuche"
                f"?jw_jobname={urllib.parse.quote(term)}&jw_location=Berlin&jw_radius=50"
            )
            try:
                page.goto(search_url, wait_until="networkidle", timeout=35000)
            except Exception as e:
                print(f"  [jobware] '{term}': {e}")
                page.remove_listener("response", on_response)
                continue

            for data in captured:
                jobs.extend(_parse_jobware_response(data, seen_ids))

            page.remove_listener("response", on_response)

        browser.close()

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

    # LinkedIn: sequential with pauses (rate-limit sensitive), primary terms only
    # Indeed: parallel, all terms
    with ThreadPoolExecutor(max_workers=1) as pool:
        f_linkedin = pool.submit(_run, "LinkedIn",  _fetch_linkedin_sequential, SEARCH_TERMS, LOCATION)
        f_indeed   = pool.submit(_run, "Indeed.de", _fetch_jobspy_parallel, all_terms, ["indeed"], "Berlin", {"country_indeed": "germany"})
        all_jobs += f_linkedin.result()
        all_jobs += f_indeed.result()

    all_jobs += _run("Xing",      _fetch_xing,      SEARCH_TERMS)
    all_jobs += _run("Stepstone", _fetch_stepstone, SEARCH_TERMS)
    all_jobs += _run("Jobware",   _fetch_jobware,   SEARCH_TERMS)

    seen_ids: set[str] = set()
    unique = [j for j in all_jobs if not (seen_ids.add(j["id"]) if j["id"] not in seen_ids else True)]  # type: ignore

    print(f"[fetcher] Total unique jobs after dedup: {len(unique)}")
    return unique
