import os, json, subprocess, pathlib, time

FSM_DIR = "/srv/memory/fsm/items"

def load_items():
    for f in pathlib.Path(FSM_DIR).glob("*.json"):
        try:
            with open(f) as fh:
                yield f, json.load(fh)
        except:
            continue

def save_item(path, data):
    tmp = str(path) + ".tmp"
    with open(tmp, "w") as fh:
        json.dump(data, fh)
    os.replace(tmp, path)

def probe_video(path):
    cmd = [
        "ffprobe","-v","error",
        "-select_streams","v:0",
        "-show_entries","stream=width,height",
        "-show_entries","format=duration",
        "-of","json", path
    ]
    try:
        out = subprocess.check_output(cmd)
        meta = json.loads(out)
        w = meta["streams"][0]["width"]
        h = meta["streams"][0]["height"]
        d = float(meta["format"]["duration"])
        return w, h, d
    except:
        return None

def main():
    for path, item in load_items():
        if item.get("state") != "downloaded":
            continue

        vpath = item.get("download_path")
        if not vpath or not os.path.exists(vpath):
            item["state"] = "dropped"
            item["error"] = "missing file"
            save_item(path, item)
            continue

        res = probe_video(vpath)
        if not res:
            item["state"] = "dropped"
            item["error"] = "ffprobe fail"
            save_item(path, item)
            continue

        w, h, dur = res
        item["width"] = w
        item["height"] = h
        item["duration"] = dur
        item["aspect_ratio"] = round(w/h, 3) if h else None
        item["state"] = "probed"
        item["probed_at"] = int(time.time())
        save_item(path, item)

if __name__ == "__main__":
    main()
