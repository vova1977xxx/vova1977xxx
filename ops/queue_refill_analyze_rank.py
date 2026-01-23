import sqlite3,json,redis,sys
arg=(sys.argv[1].strip() if len(sys.argv)>1 else "")
lim=int(arg) if arg.isdigit() else 200
db="/srv/gemivas_platform/data/gemivas.db"
r=redis.Redis(host="127.0.0.1",port=6379,decode_responses=True)
con=sqlite3.connect(db)
cur=con.cursor()
cur.execute("select id from videos where pipeline_status in ('published','analyzed') limit ?",(lim,))
ids=[x[0] for x in cur.fetchall()]
for vid in ids:
 r.rpush("q:tasks",json.dumps({"id":f"an-{vid}","type":"analyze","payload":{"id":str(vid)},"try":0}))
 r.rpush("q:tasks",json.dumps({"id":f"rk-{vid}","type":"rank","payload":{"id":str(vid)},"try":0}))
print("enqueued",len(ids),"pairs")
