import os,json,pathlib,time,subprocess,requests

FSM_DIR="/srv/memory/fsm/items"
OLLAMA_URL="http://127.0.0.1:11434/api/chat"
MODEL="llama3.1:8b-instruct-q4_K_M"

def load_items():
    for f in pathlib.Path(FSM_DIR).glob("*.json"):
        try: yield f,json.load(open(f))
        except: continue

def save_item(p,d):
    t=str(p)+".tmp"; json.dump(d,open(t,"w")); os.replace(t,p)
def ai_score(meta):
    prompt=f"Video duration {meta.get('duration')} sec. Is this short-form engaging content? Score 0-1."
    try:
        r=requests.post(OLLAMA_URL,json={"model":MODEL,"prompt":prompt,"stream":False},timeout=10)
        txt=r.json().get("response","0").strip()
        return float(txt.split()[0])
    except:
        return 0.5
def main():
    for path,item in load_items():
        if item.get("state")!="probed": continue
        vpath=item.get("download_path")
        if not vpath or not os.path.exists(vpath):
            item["state"]="dropped"; save_item(path,item); continue
        score=ai_score(item)
        item["ai_score"]=score
        item["content_features"]=item.get("content_features",{})
        item["content_features"]["ai_score"]=score
        item["state"]="analyzed"
        item["analyzed_at"]=int(time.time())
        save_item(path,item)

if __name__=="__main__": main()
