import json, re, hashlib
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]
KEYWORDS=["civil engineering","concrete","cement","cementitious","green cement","low carbon","low-carbon","3d printing","additive manufacturing","construction materials","smart infrastructure","research fellow","research scientist","assistant professor","associate professor","faculty"]
PROFILE=["green cement","low-carbon concrete","cementitious","3d printing","additive manufacturing","self-healing","self-sensing","smart infrastructure"]
def load(p): return json.loads((ROOT/p).read_text())
def save(p,x): (ROOT/p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+"\n")
jobs=load("data/jobs.json"); sources=load("sources.json"); known={j["url"] for j in jobs}; found=0
headers={"User-Agent":"Mozilla/5.0 CareerPortalMonitor/1.0"}
for s in sources:
    try:
        r=requests.get(s["url"],headers=headers,timeout=25); r.raise_for_status(); soup=BeautifulSoup(r.text,"html.parser")
        for a in soup.select("a[href]"):
            title=" ".join(a.get_text(" ",strip=True).split()); url=urljoin(s["url"],a["href"]); text=(title+" "+url).lower()
            if len(title)<8 or not any(k in text for k in KEYWORDS) or url in known: continue
            score=65+min(30,5*sum(k in text for k in PROFILE)); status="Review Needed"
            jobs.append({"id":hashlib.sha1(url.encode()).hexdigest()[:12],"country":s["country"],"institution":s["institution"],"title":title[:160],"type":s["type"],"status":status,"score":score,"isNew":True,"areas":[k for k in PROFILE if k in text][:4] or ["Civil engineering"],"summary":"Automatically discovered from an official institutional source. Review the source page before applying.","match":[k for k in PROFILE if k in text][:4] or ["Civil engineering"],"url":url,"last_seen":datetime.now(timezone.utc).date().isoformat()}); known.add(url); found+=1
    except Exception as e: print(f"SOURCE ERROR {s['url']}: {e}")
# New flag expires after 21 days when dates are parseable
now=datetime.now(timezone.utc).date()
for j in jobs:
    try: j["isNew"]=(now-datetime.fromisoformat(j.get("last_seen","")).date()).days<=21
    except Exception: pass
save("data/jobs.json",jobs)
tpe=datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M Asia/Taipei")
save("data/update-meta.json",{"last_updated":tpe,"sources_checked":len(sources),"new_links_found":found})
print(f"Checked {len(sources)} sources; added {found} candidate links; total {len(jobs)}")
