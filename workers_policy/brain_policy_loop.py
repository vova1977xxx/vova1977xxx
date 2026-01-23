#!/usr/bin/env python3
import os
import sys
import time
import json
import subprocess
from datetime import datetime, timezone

REPO = "/srv/gemivas-platform"
OPS_FORCE_REFILL = f"{REPO}/ops/force_refill.sh"

REDIS_HOST = os.getenv("GEMIVAS_REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.getenv("GEMIVAS_REDIS_PORT", "6379"))

MIN_PUBLISHED = int(os.getenv("GEMIVAS_MIN_PUBLISHED", "120"))
MAX_QUEUE_TASKS = int(os.getenv("GEMIVAS_MAX_QUEUE_TASKS", "200"))
REFILL_MIN_TASKS = int(os.getenv("GEMIVAS_REFILL_MIN_TASKS", "20"))
REFILL_COOLDOWN_SEC = int(os.getenv("GEMIVAS_REFILL_COOLDOWN_SEC", "3300"))
REFILL_MAX_PUBLISHED = int(os.getenv("GEMIVAS_REFILL_MAX_PUBLISHED", "240"))

 
def log_event(kind, ref_id, msg, data=None):
    try:
        payload = "{}"
        if data is not None:
            payload = json.dumps(data, ensure_ascii=False)
        cmd = ["python3", "/srv/gemivas-platform/scripts/log_event.py", str(kind), str(ref_id), str(msg), payload]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, text=True, timeout=10)
    except Exception:
        pass


def sh(cmd, timeout=30):
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=timeout)
    return r.returncode, r.stdout.strip()

def log(msg):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    print(f"[brain-policy] {ts}Z {msg}")

def get_published_count():
    # /srv/web/feed/videos/YYYY/MM/*.mp4
    cmd = ["bash", "-lc", "find /srv/web/feed/videos -type f -name '*.mp4' 2>/dev/null | wc -l"]
    code, out = sh(cmd)
    if code != 0:
        return None
    try:
        return int(out.strip())
    except:
        return None

def redis_llen(key):
    cmd = ["redis-cli", "-h", REDIS_HOST, "-p", str(REDIS_PORT), "LLEN", key]
    code, out = sh(cmd, timeout=10)
    if code != 0:
        return None
    out = out.strip()
    try:
        return int(out)
    except:
        return None

def get_queue_state():
    tasks = redis_llen("q:tasks")
    dlq   = redis_llen("q:dlq")
    return tasks, dlq
def redis_lpop(key):
    code, out = sh(["redis-cli", "-h", REDIS_HOST, "-p", str(REDIS_PORT), "LPOP", key], timeout=10)
    if code != 0:
        return None
    out = out.strip()
    if out == "" or out.lower() == "(nil)":
        return None
    return out


DOCTOR_COOLDOWN_SEC = int(os.getenv("GEMIVAS_DOCTOR_COOLDOWN_SEC", "1800"))
OPS_DOCTOR = f"{REPO}/ops/doctor.sh"

def redis_get(key):
    code, out = sh(["redis-cli", "-h", REDIS_HOST, "-p", str(REDIS_PORT), "GET", key], timeout=10)
    if code != 0:
        return None
    out = out.strip()
    if out == "" or out.lower() == "(nil)":
        return None
    return out

def redis_set(key, val, ex=None):
    cmd = ["redis-cli", "-h", REDIS_HOST, "-p", str(REDIS_PORT), "SET", key, str(val)]
    if ex is not None:
        cmd += ["EX", str(int(ex))]
    sh(cmd, timeout=10)

def maybe_run_doctor(reason, dlq_count):
    now = int(time.time())
    last = redis_get("policy:last_doctor_ts")
    try:
        last = int(last) if last is not None else 0
    except:
        last = 0

    if now - last < DOCTOR_COOLDOWN_SEC:
        log(f"SKIP doctor: cooldown active ({now-last}s < {DOCTOR_COOLDOWN_SEC}s)")
        log_event("brain_policy","decision","skip doctor cooldown",{"dlq":dlq_count,"cooldown_sec":DOCTOR_COOLDOWN_SEC})
        return 0

    if not os.path.exists(OPS_DOCTOR):
        log("ERROR: missing ops/doctor.sh")
        log_event("brain_policy","decision","doctor missing",{"path":OPS_DOCTOR})
        return 3

    redis_set("policy:last_doctor_ts", now, ex=86400)
    log(f"ACTION: DLQ={dlq_count} => run doctor ({reason})")
    log_event("brain_policy","decision","run doctor",{"reason":reason,"dlq":dlq_count})

    code, out = sh(["bash", "-lc", OPS_DOCTOR], timeout=600)
    log(f"doctor rc={code}")
    if out:
        print(out)
    return code

def run_force_refill():
    if not os.path.exists(OPS_FORCE_REFILL):
        log(f"ERROR: missing {OPS_FORCE_REFILL}")
        return 3
    code, out = sh(["bash", "-lc", OPS_FORCE_REFILL], timeout=120)
    log(f"force_refill rc={code}")
    if out:
        print(out)
    return code


def maybe_refill_queue(tasks, published):
    now = int(time.time())
    last = redis_get("policy:last_refill_ts")
    try:
        last = int(last) if last is not None else 0
    except:
        last = 0

    if now - last < REFILL_COOLDOWN_SEC:
        log(f"SKIP refill: cooldown active ({now-last}s < {REFILL_COOLDOWN_SEC}s)")
        log_event("brain_policy","decision","skip refill cooldown",{"q_tasks":tasks,"published":published,"cooldown_sec":REFILL_COOLDOWN_SEC})
        return 0

    redis_set("policy:last_refill_ts", now, ex=86400)
    log(f"ACTION: q:tasks={tasks} <= REFILL_MIN_TASKS={REFILL_MIN_TASKS} => force_refill")
    log_event("brain_policy","decision","refill_low_queue",{"q_tasks":tasks,"refill_min":REFILL_MIN_TASKS,"published":published})
    return run_force_refill()


def main():
    log("policy loop start")
    log_event("brain_policy","start","policy loop started")

    published = get_published_count()
    tasks, dlq = get_queue_state()

    log(f"state published={published} q:tasks={tasks} q:dlq={dlq} min_published={MIN_PUBLISHED}")
    log_event("brain_policy","state","policy state",{"published":published,"q_tasks":tasks,"q_dlq":dlq,"min_published":MIN_PUBLISHED})

    if tasks is None or dlq is None:
        log("ERROR: redis not reachable or invalid response")
        log_event("brain_policy","decision","redis down")
        return 2

    if dlq > 0:
        log(f"WARNING: DLQ has items: {dlq}")
        log_event("brain_policy","warning","dlq nonzero",{"q_dlq":dlq})
        item = redis_lpop("q:dlq")
        log_event("brain_policy","dlq_drain","dlq item drained",{"item":item})

        return maybe_run_doctor("dlq_nonzero", dlq)


    if tasks > MAX_QUEUE_TASKS:
        log(f"SKIP: queue too large tasks={tasks} > {MAX_QUEUE_TASKS}")
        log_event("brain_policy","decision","skip overload",{"q_tasks":tasks,"max":MAX_QUEUE_TASKS})
        return 0

    if published is None:
        log("ERROR: cannot compute published count")
        log_event("brain_policy","decision","published count error")
        return 4


    # queue low => refill (smart)

    # do not refill if we already have plenty published
    if published is not None and published > REFILL_MAX_PUBLISHED:
        log(f"SKIP refill: published={published} > REFILL_MAX_PUBLISHED={REFILL_MAX_PUBLISHED}")
        log_event("brain_policy","decision","skip refill too_many_published",{"published":published,"max":REFILL_MAX_PUBLISHED,"q_tasks":tasks})
        return 0

    if tasks <= REFILL_MIN_TASKS:
        return maybe_refill_queue(tasks, published)


    if published < MIN_PUBLISHED:
        log(f"ACTION: published({published}) < MIN_PUBLISHED({MIN_PUBLISHED}) => force_refill")
        log_event("brain_policy","decision","refill",{"published":published,"min_published":MIN_PUBLISHED})
        return run_force_refill()

    log("OK: no action needed")
    log_event("brain_policy","decision","ok")
    return 0

if __name__ == "__main__":
    sys.exit(main())
