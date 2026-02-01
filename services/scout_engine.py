import requests, re, hashlib, pathlib, json, time

FSM_DIR="/srv/memory/fsm/items"
CONF="/srv/gemivas-platform/config/scout_sources.txt"
pathlib.Path(FSM_DIR).mkdir(parents=True, exist_ok=True)

def uid(u): return hashlib.sha1(u.encode()).hexdigest()[:16]

def add(url):
    vid=uid(url)
    p=pathlib.Path(FSM_DIR)/f"{vid}.json"
    if p.exists(): return 0
    json.dump({"id":vid,"state":"scouted","src":url,"found_at":int(time.time())},open(p,"w"))
    return 1

new=0
for site in open(CONF):
    site=site.strip()

    # якщо це вже mp4 → додаємо
    if site.endswith((".mp4",".webm",".m3u8")):
        new+=add(site)
        continue

    # інакше — це сторінка
    try:
        r=requests.get(site,timeout=10).text
        links=re.findall(r'https?://[^\s"<>]+?\.(?:mp4|webm|m3u8)', r)
        for l in links[:20]:
            new+=add(l)
    except:
        pass

print("SCOUT OK new=",new)
