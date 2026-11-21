from flask import Flask, render_template, request, jsonify
from pathlib import Path
import threading, uuid, subprocess, shutil, re, os, time, webbrowser, urllib.request
import yt_dlp

app=Flask(__name__)
@app.route("/favicon.ico")
def favicon():
    return app.send_static_file("favicon.ico")

OUT=Path.home()/"Downloads"/"Download"
OUT.mkdir(parents=True,exist_ok=True)
jobs={}
lock=threading.Lock()

def to_seconds(raw):
    raw=(raw or "").strip()
    if not re.fullmatch(r"(?:\d+(?:\.\d+)?|\d{1,2}:\d{2}(?:\:\d{2}(?:\.\d+)?)?)", raw):
        raise ValueError("Timestamp gunakan detik, MM:SS, atau HH:MM:SS.")
    if ":" not in raw: return float(raw)
    p=[float(x) for x in raw.split(":")]
    return p[0]*60+p[1] if len(p)==2 else p[0]*3600+p[1]*60+p[2]

def stamp(sec):
    h=int(sec//3600); m=int((sec%3600)//60); s=sec%60
    return f"{h:02d}:{m:02d}:{s:06.3f}"

def hook_for(jobid):
    def hook(d):
        with lock:
            j=jobs.get(jobid)
            if not j: return
            if d.get("status")=="downloading":
                total=d.get("total_bytes") or d.get("total_bytes_estimate") or 0
                done=d.get("downloaded_bytes",0)
                j["progress"]=round(100*done/total,1) if total else j.get("progress",0)
                j["status"]="Downloading"
                j["speed"]=d.get("_speed_str","")
                j["eta"]=d.get("_eta_str","")
            elif d.get("status")=="finished":
                j["progress"]=99
                j["status"]="Finalizing file"
    return hook

def run_job(jobid,url,start,end):
    duration=end-start
    options={
        "format":"bestvideo+bestaudio/best",
        "outtmpl":str(OUT/"%(title).150s [%(id)s].%(ext)s"),
        "merge_output_format":"mp4",
        # Python API must use download_ranges callback, not CLI download_sections string.
        "download_ranges": yt_dlp.utils.download_range_func([], [[start,end]]),
        "force_keyframes_at_cuts": True,
        "noplaylist": True,
        "progress_hooks":[hook_for(jobid)],
        "retries":3,
        "fragment_retries":3,
        "quiet":True,
        "no_warnings":True,
    }
    try:
        with lock:
            jobs[jobid].update(status="Preparing",message="Resolving formats and requested segment…",progress=0)
        with yt_dlp.YoutubeDL(options) as ydl:
            info=ydl.extract_info(url,download=True)
            # Resolve actual final filename after merger/post-processing.
            guessed=Path(ydl.prepare_filename(info))
            candidates=[]
            video_id=info.get("id","")
            if video_id:
                candidates=list(OUT.glob(f"*[{video_id}]*"))
            if guessed.exists(): candidates.append(guessed)
            # merged MP4 commonly uses the base path with .mp4 extension
            mp4_guess=guessed.with_suffix(".mp4")
            if mp4_guess.exists(): candidates.append(mp4_guess)
            candidates=[p for p in candidates if p.is_file() and p.stat().st_size>0]
            if not candidates:
                raise RuntimeError("File hasil tidak ditemukan setelah post-processing.")
            final_path=max(set(candidates),key=lambda p:p.stat().st_mtime)
        # Verify actual segment length using ffprobe if available. Do not claim success for full video.
        actual=None
        if shutil.which("ffprobe"):
            probe=subprocess.run(
                ["ffprobe","-v","error","-show_entries","format=duration",
                 "-of","default=noprint_wrappers=1:nokey=1",str(final_path)],
                capture_output=True,text=True,timeout=25
            )
            if probe.returncode==0:
                try: actual=float(probe.stdout.strip())
                except (ValueError,TypeError): actual=None
        if actual is not None and actual>duration+2:
            # Keep the suspicious file for debugging, but mark failure rather than success.
            raise RuntimeError(f"Segment verification failed: target {duration:.1f}s, output {actual:.1f}s. File retained for inspection.")
        with lock:
            jobs[jobid].update(
                status="Completed",progress=100,output=str(final_path),
                message=f"Segment download complete · target {duration:.1f}s"+
                        (f" · verified {actual:.1f}s" if actual is not None else "")
            )
    except Exception as ex:
        with lock:
            jobs[jobid].update(status="Error",progress=0,message=str(ex))

@app.route("/")
def home(): return render_template("index.html")

@app.post("/api/download")
def download():
    data=request.get_json(force=True)
    url=(data.get("url") or "").strip()
    if not re.match(r"^https?://(www\.)?(youtube\.com|youtu\.be)/",url):
        return jsonify(error="Masukkan link YouTube yang valid."),400
    if not shutil.which("ffmpeg"):
        return jsonify(error="FFmpeg tidak ditemukan. Install FFmpeg, lalu pastikan ffmpeg.exe ada di PATH."),400
    if not shutil.which("ffprobe"):
        return jsonify(error="FFprobe tidak ditemukan (biasanya ikut FFmpeg). Pastikan ffprobe.exe ada di PATH untuk verifikasi durasi."),400
    try:
        start=to_seconds(data.get("start"))
        end=to_seconds(data.get("end"))
        if start<0 or end<=start: raise ValueError("End harus lebih besar dari Start.")
    except Exception as e: return jsonify(error=str(e)),400
    jid=uuid.uuid4().hex[:10]
    with lock: jobs[jid]={"id":jid,"status":"Queued","progress":0,"speed":"","eta":"","message":"Waiting…","output":None}
    threading.Thread(target=run_job,args=(jid,url,start,end),daemon=True).start()
    return jsonify(id=jid)

@app.get("/api/status/<jid>")
def status(jid):
    with lock:
        if jid not in jobs: return jsonify(error="Job not found"),404
        return jsonify(jobs[jid])

@app.post("/api/show-folder")
def show_folder():
    try:
        if os.name=="nt": subprocess.Popen(["explorer",str(OUT)])
        elif shutil.which("open"): subprocess.Popen(["open",str(OUT)])
        elif shutil.which("xdg-open"): subprocess.Popen(["xdg-open",str(OUT)])
        return jsonify(ok=True)
    except Exception as e: return jsonify(error=str(e)),500

def open_browser_when_ready():
    url="http://127.0.0.1:5050"
    for _ in range(50):
        try:
            urllib.request.urlopen(url,timeout=0.5)
            webbrowser.open(url)
            return
        except Exception:
            time.sleep(0.25)

if __name__=="__main__":
    threading.Thread(target=open_browser_when_ready,daemon=True).start()
    app.run(host="127.0.0.1",port=5050,debug=False)
