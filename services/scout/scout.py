import os, json, time, re, hashlib, pathlib, urllib.request, urllib.parse, ssl
import xml.etree.ElementTree as ET

CFG="/srv/gemivas-platform/config/scout_sources.json"
FSM_DIR="/srv/memory/fsm/items"
SEEN="/srv/memory/scout/seen_urls.txt"
LOG="/srv/memory/events/scout.log"

def log(s):
    ts=time.strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG,"a",encoding="utf-8") as f:
        f.write(f"[{ts}] {s}\n")

def load_cfg():
    return json.load(open(CFG,"r",encoding="utf-8"))

def sha1(s): return hashlib.sha1(s.encode("utf-8")).hexdigest()

def load_seen():
    if not os.path.exists(SEEN): return set()
    try:
        with open(SEEN,"r",encoding="utf-8") as f:
            return set(x.strip() for x in f if x.strip())
    except:
        return set()

def remember(h):
    with open(SEEN,"a",encoding="utf-8") as f:
        f.write(h+"\n")

def fetch(url, ua, timeout):
    ctx=ssl.create_default_context()
    req=urllib.request.Request(url, headers={"User-Agent": ua})
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
        ct=r.headers.get("Content-Type","")
        data=r.read(2_000_000)  # cap
    return ct, data

def norm_url(u):
    u=u.strip()
    u=u.replace("&amp;","&")
    return u

def extract_video_urls(text, allow_ext):
    urls=set()
    for ext in allow_ext:
        # mp4/webm direct
        if ext in ("mp4","webm"):
            pat=re.compile(r'https?://[^\s\'"<>]+?\.'+re.escape(ext)+r'(?:\?[^\s\'"<>]+)?', re.I)
            urls.update(pat.findall(text))
        # m3u8 playlists
        if ext=="m3u8":
            pat=re.compile(r'https?://[^\s\'"<>]+?\.m3u8(?:\?[^\s\'"<>]+)?', re.I)
            urls.update(pat.findall(text))
    return [norm_url(u) for u in urls]

def rss_urls(xml_bytes):
    out=[]
    try:
        root=ET.fromstring(xml_bytes)
    except:
        return out
    # RSS items: <item><link>... ; also media:content url=""
    for it in root.findall(".//item"):
        lk=it.findtext("link") or ""
        if lk: out.append(lk.strip())
        for mc in it.findall(".//{*}content"):
            u=mc.attrib.get("url","")
            if u: out.append(u.strip())
        for en in it.findall(".//enclosure"):
            u=en.attrib.get("url","")
            if u: out.append(u.strip())
    # Atom <entry><link href="">
    for lk in root.findall(".//{*}link"):
        u=lk.attrib.get("href","")
        if u: out.append(u.strip())
    return out

def write_fsm(src, topic, source_type):
    hid=sha1(src)[:12]
    p=pathlib.Path(FSM_DIR)/f"scout-{hid}.json"
    if p.exists(): return False
    obj={
        "id": f"scout-{hid}",
        "state": "scouted",
        "src": src,
        "topic": topic,
        "source_type": source_type,
        "ts": int(time.time())
    }
    tmp=str(p)+".tmp"
    with open(tmp,"w",encoding="utf-8") as f:
        json.dump(obj,f,ensure_ascii=False)
    os.replace(tmp,p)
    return True

def main():
    os.makedirs(FSM_DIR, exist_ok=True)
    cfg=load_cfg()
    ua=cfg.get("user_agent","GEMIVAS-Scout/1.0")
    timeout=int(cfg.get("timeout_sec",15))
    allow_ext=cfg.get("allow_ext",["mp4","webm","m3u8"])
    max_new=int(cfg.get("max_new_per_run",100))

    seen=load_seen()
    new_cnt=0

    # 1) RSS per topic
    topics=cfg.get("topics",{})
    for topic, feeds in topics.items():
        for feed in feeds:
            try:
                ct,data=fetch(feed,ua,timeout)
                links=rss_urls(data)
                # parse links pages too (light)
                for u in links[:60]:
                    if new_cnt>=max_new: break
                    h=sha1(u)
                    if h in seen: continue
                    # if direct video -> accept
                    if any(u.lower().split("?")[0].endswith("."+e) for e in allow_ext):
                        if write_fsm(u,topic,"rss"):
                            remember(h); seen.add(h); new_cnt+=1
                        continue
                    # else try fetch page and extract direct videos
                    try:
                        _,html=fetch(u,ua,timeout)
                        txt=html.decode("utf-8","ignore")
                        vids=extract_video_urls(txt,allow_ext)
                        for v in vids:
                            if new_cnt>=max_new: break
                            hv=sha1(v)
                            if hv in seen: continue
                            if write_fsm(v,topic,"rss_page"):
                                remember(hv); seen.add(hv); new_cnt+=1
                    except:
                        remember(h); seen.add(h)
            except:
                continue

    # 2) Seed pages (broad)
    for page in cfg.get("seed_pages",[]):
        if new_cnt>=max_new: break
        try:
            _,html=fetch(page,ua,timeout)
            txt=html.decode("utf-8","ignore")
            vids=extract_video_urls(txt,allow_ext)
            for v in vids:
                if new_cnt>=max_new: break
                hv=sha1(v)
                if hv in seen: continue
                if write_fsm(v,"wow","seed_page"):
                    remember(hv); seen.add(hv); new_cnt+=1
        except:
            continue

    log(f"new={new_cnt} max={max_new}")
    print(f"SCOUT OK new={new_cnt}")

if __name__=="__main__":
    main()
