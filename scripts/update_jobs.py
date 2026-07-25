import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
ENGLISH_KEYWORDS = [
    "civil engineering", "concrete", "cement", "cementitious", "green cement",
    "low carbon", "low-carbon", "3d printing", "additive manufacturing",
    "construction materials", "smart infrastructure", "research fellow",
    "research scientist", "engineer", "faculty"
]
CHINESE_KEYWORDS = [
    "土木", "營建", "混凝土", "水泥", "膠結材料", "綠色材料", "低碳",
    "淨零", "3d列印", "積層製造", "研究員", "研發", "工程師", "教師"
]
PROFILE_TERMS = ENGLISH_KEYWORDS[1:10] + CHINESE_KEYWORDS[2:10]
LOCATION_SCORES = {
    "Taiwan": 100, "Singapore": 92, "Hong Kong": 84,
    "Japan": 76, "South Korea": 68, "Other Asia": 45
}


def load(path):
    return json.loads((ROOT / path).read_text())


def save(path, value):
    (ROOT / path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def dimensions(source, text):
    relevant = sum(term in text for term in PROFILE_TERMS)
    technical = min(96, 64 + relevant * 5)
    base = {
        "location": LOCATION_SCORES.get(source["country"], 45),
        "technical": technical,
        "skills": min(94, 62 + relevant * 5),
        "level": 76,
        "language": 88 if source["country"] == "Taiwan" else 100,
        "company": 82,
    }
    academic = dict(base)
    industry = dict(base)
    if source["category"] == "Academic":
        academic["level"], academic["company"] = 90, 92
        industry["technical"], industry["level"] = max(55, technical - 16), 64
    elif source["category"] == "Industry":
        industry["level"], industry["company"] = 88, 92
        academic["technical"], academic["level"] = max(55, technical - 16), 64
    else:
        academic["company"], industry["company"] = 88, 90
    return {"academic": academic, "industry": industry}


jobs = load("data/jobs.json")
sources = load("sources.json")
known = {job["url"] for job in jobs}
found = 0
new_jobs = []
headers = {"User-Agent": "Mozilla/5.0 CareerPortalMonitor/2.0"}

for source in sources:
    try:
        response = requests.get(source["url"], headers=headers, timeout=25)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        for anchor in soup.select("a[href]"):
            title = " ".join(anchor.get_text(" ", strip=True).split())
            url = urljoin(source["url"], anchor["href"])
            text = (title + " " + url).lower()
            keywords = ENGLISH_KEYWORDS + (CHINESE_KEYWORDS if source["country"] == "Taiwan" else [])
            if len(title) < 8 or not any(term in text for term in keywords) or url in known:
                continue
            language = "zh-Hant" if any("\u4e00" <= char <= "\u9fff" for char in title) else "en"
            matching_terms = [term for term in PROFILE_TERMS if term in text][:4]
            discovered_job = {
                "id": hashlib.sha1(url.encode()).hexdigest()[:12],
                "country": source["country"],
                "location": source["country"],
                "institution": source["institution"],
                "title": title[:180],
                "language": language,
                "category": source["category"],
                "description": "Automatically discovered from this official source. Verify details and availability on the linked posting.",
                "englishSummary": "Official-source candidate. Review the linked posting for full requirements." if language == "zh-Hant" else "",
                "skills": matching_terms or ["Civil engineering"],
                "searchTerms": matching_terms,
                "firstSeen": datetime.now(timezone.utc).date().isoformat(),
                "url": url,
                "scores": dimensions(source, text)
            }
            jobs.append(discovered_job)
            new_jobs.append(discovered_job)
            known.add(url)
            found += 1
    except Exception as error:
        print(f"SOURCE ERROR {source['url']}: {error}")

save("data/jobs.json", jobs)
save(".new-jobs.json", new_jobs)
taipei_time = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M Asia/Taipei")
save("data/update-meta.json", {
    "last_updated": taipei_time,
    "sources_checked": len(sources),
    "new_links_found": found
})
print(f"Checked {len(sources)} sources; added {found} candidate links; total {len(jobs)}")
