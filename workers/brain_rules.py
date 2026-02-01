import json,hashlib
RULES=json.load(open("/srv/memory/brain_rules.json"))
SEEN="/srv/memory/brain_seen.txt"

def is_duplicate(src):
    h=hashlib.md5(src.encode()).hexdigest()
    if not os.path.exists(SEEN): open(SEEN,"w").write("")
    s=set(open(SEEN).read().splitlines())
    if h in s: return True
    open(SEEN,"a").write(h+"\n")
    return False

def allow(item):
    if item.get("score",0) < RULES["min_score"]: return False
    if RULES["drop_if_duplicate"] and is_duplicate(item.get("src","")): return False
    return True
