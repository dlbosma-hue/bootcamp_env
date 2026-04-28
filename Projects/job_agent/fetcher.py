import hashlib
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

import feedparser
from jobspy import scrape_jobs

from config import (
    DISTANCE_KM,
    EXCLUDE_TERMS,
    JOBWARE_RSS_TEMPLATE,
    LOCATION,
    MAX_HOURS_OLD,
    RESULTS_PER_TERM,
    SEARCH_TERMS,
    SECONDARY_TERMS,
    STEPSTONE_RSS_TEMPLATE,
)

_TITLE_MUST_INCLUDE = [
    "it", "cto", "cio", "tech", "digital", "infrastructure", "infra",
    "architect", "netzwerk", "network", "cloud", "devops", "security",
    "projektmanager", "project manager", "projektleiter", "pmo",
    "leiter", "leitung", "director", "head of", "abteilungsleiter",
    "gruppenleiter", "manager", "consultant", "berater", "governance",
    "itil", "service management", "itsm",
]


def _job_id(title: str, company: str, url: str) -> str:
    raw = f"{title.lower().strip()}|{company.lower().strip()}|{url.strip()}"
    return hashlib.md5(raw.encode()).hexdigest()


def _is_excluded(title: str) -> bool:
    return any(term in title.lower() for term in EXCLUDE_TERMS)


def _passes_title_filter(title: str) -> bool:
    return any(term in title.lower() for term in _TITLE_MUST_INCLUDE)


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
        url = str(row.get("job_url", ""))
        title = str(row.get("title", ""))
        company = str(row.get("company", ""))
        if not title or not company:
            continue
        if _is_excluded(title) or not _passes_title_filter(title):
            continue
        jobs.append({
            "id": _job_id(title, company, url),
            "title": title,
            "company": company,
            "location": str(row.get("location", "")),
            "url": url,
            "description": str(row.get("description", ""))[:3000],
            "source": str(row.get("site", sites[0])),
        })
    return jobs


def _fetch_jobspy_parallel(terms: list[str], sites: list[str], location: str, extra_kwargs: dict = {}) -> list[dict]:
    all_jobs: list[dict] = []
    seen_urls: set[str] = set()

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(_scrape_one_term, t, sites, location, extra_kwargs): t for t in terms}
        for future in as_completed(futures):
            for job in future.result():
                if job["url"] not in seen_urls:
                    seen_urls.add(job["url"])
                    all_jobs.append(job)

    return all_jobs


def _fetch_rss(terms: list[str], url_template: str, source_name: str, path_encode: bool = False) -> list[dict]:
    jobs = []
    seen_urls: set[str] = set()
    cutoff = datetime.now(timezone.utc).timestamp() - (MAX_HOURS_OLD * 3600)

    for term in terms:
        encoded = term.replace(" ", "-") if path_encode else urllib.parse.quote(term)
        url = url_template.format(keyword=encoded)
        try:
            feed = feedparser.parse(url)
            if not feed.entries:
                print(f"  [{source_name}] No entries for '{term}' — URL may need adjustment")
                continue
        except Exception as e:
            print(f"  [{source_name}] Error: {e}")
            continue

        for entry in feed.entries:
            title = entry.get("title", "")
            link = entry.get("link", "")
            summary = entry.get("summary", "")
            company = entry.get("author", "") or entry.get("source", {}).get("title", "Unknown")

            published = entry.get("published_parsed")
            if published:
                pub_ts = datetime(*published[:6], tzinfo=timezone.utc).timestamp()
                if pub_ts < cutoff:
                    continue

            if not title or not link:
                continue
            if _is_excluded(title) or not _passes_title_filter(title):
                continue
            if link in seen_urls:
                continue

            seen_urls.add(link)
            jobs.append({
                "id": _job_id(title, company, link),
                "title": title,
                "company": company,
                "location": "Berlin",
                "url": link,
                "description": summary[:3000],
                "source": source_name,
            })

    return jobs


def fetch_all_jobs() -> list[dict]:
    all_jobs: list[dict] = []
    all_terms = SEARCH_TERMS + SECONDARY_TERMS

    # all 3 jobspy sources run in parallel threads
    def _run(label, fn, *args, **kwargs):
        print(f"[fetcher] {label}...")
        result = fn(*args, **kwargs)
        print(f"  → {len(result)} jobs")
        return result

    with ThreadPoolExecutor(max_workers=3) as pool:
        f_linkedin = pool.submit(_run, "LinkedIn",     _fetch_jobspy_parallel, all_terms,   ["linkedin"], LOCATION)
        f_indeed   = pool.submit(_run, "Indeed.de",   _fetch_jobspy_parallel, all_terms,   ["indeed"],   "Berlin", {"country_indeed": "germany"})
        f_google   = pool.submit(_run, "Google Jobs", _fetch_jobspy_parallel, SEARCH_TERMS, ["google"],  "Berlin, Germany")

        all_jobs += f_linkedin.result()
        all_jobs += f_indeed.result()
        all_jobs += f_google.result()

    print("[fetcher] Stepstone RSS...")
    stepstone = _fetch_rss(SEARCH_TERMS, STEPSTONE_RSS_TEMPLATE, "stepstone", path_encode=True)
    print(f"  → {len(stepstone)} jobs")
    all_jobs += stepstone

    print("[fetcher] Jobware RSS...")
    jobware = _fetch_rss(SEARCH_TERMS, JOBWARE_RSS_TEMPLATE, "jobware", path_encode=False)
    print(f"  → {len(jobware)} jobs")
    all_jobs += jobware

    # deduplicate across all sources
    seen_ids: set[str] = set()
    unique = []
    for job in all_jobs:
        if job["id"] not in seen_ids:
            seen_ids.add(job["id"])
            unique.append(job)

    print(f"[fetcher] Total unique jobs after dedup: {len(unique)}")
    return unique
