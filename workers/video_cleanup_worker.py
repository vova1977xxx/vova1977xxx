import os,json,glob,time

MEM="/srv/memory/feed/index.json"

ROOT="/srv/web/feed/videos"  # published storage (DO NOT DELETE)
TMP="/srv/downloads"          # temp downloads
TMP_TTL_H=24                  # delete only tmp older than TTL

MAX_KEEP=200                  # keep index entries (not files)

def load():
    try:
        return json.load(open(MEM,"r",encoding="utf-8"))
    except:
        return {"items":[]}

def save(j):
    tmp=MEM+".tmp"
    open(tmp,"w",encoding="utf-8").write(json.dumps(j,ensure_ascii=False))
    os.replace(tmp,MEM)

def cleanup_tmp():
    try:
        now=time.time()
        for f in glob.glob(TMP+"/*.mp4"):
            try:
                if os.path.getmtime(f) < now-(TMP_TTL_H*3600):
                    os.unlink(f)
            except:
                pass
    except:
        pass

def main():
    j=load()
    items=j.get("items",[])

    # remove broken index entries ONLY (do not delete ROOT files)
    ok=[]
    for it in items:
        url=(it.get("url","") or "").strip()
        if url.startswith("/feed/videos/"):
            p=os.path.join(ROOT,url.replace("/feed/videos/",""))
            if os.path.exists(p):
                ok.append(it)
        else:
            ok.append(it)

    # SAFE: cleanup only tmp downloads
    cleanup_tmp()

    # trim index only (never delete published files)
    j["items"]=ok[:MAX_KEEP]
    save(j)

    print("OK cleanup index:",len(j["items"]))

if __name__=="__main__":
    main()
