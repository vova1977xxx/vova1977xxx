import json,time,os,urllib.request,xml.etree.ElementTree as ET
OUT="/srv/memory/news/items.json"
SOURCES=[("BBC World","https://feeds.bbci.co.uk/news/world/rss.xml"),("Ukrainska Pravda","https://www.pravda.com.ua/rss/")]
def fetch(url,timeout=20):
 req=urllib.request.Request(url,headers={"User-Agent":"gemivas-news-worker/1.0"})
 with urllib.request.urlopen(req,timeout=timeout) as r:
  return r.read()
items=[]
now=int(time.time())
for source,url in SOURCES:
 try:
  raw=fetch(url)
  root=ET.fromstring(raw)
  for it in root.findall(".//item")[:10]:
   title=(it.findtext("title") or "").strip()
   link=(it.findtext("link") or "").strip()
   if not title or not link: continue
   items.append({"id":link[-60:],"title":title,"url":link,"source":source,"ts":now})
 except Exception: pass
seen=set(); uniq=[]
for it in items:
 if it["url"] in seen: continue
 seen.add(it["url"]); uniq.append(it)
os.makedirs(os.path.dirname(OUT),exist_ok=True)
tmp=OUT+".tmp"
open(tmp,"w",encoding="utf-8").write(json.dumps({"items":uniq[:50]},ensure_ascii=False))
os.replace(tmp,OUT)
print("OK news items:",len(uniq[:50]))
