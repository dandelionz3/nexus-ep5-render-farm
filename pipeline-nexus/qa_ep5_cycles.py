#!/usr/bin/env python3
"""QA varian Cycles 16:9 NEXUS ZERO Episode 5 — 2 file out/ (pola qa_ep4_cycles.py).
Cek per file: durasi 60.000 dtk, 24 fps, 1440 frame, resolusi, decode
video+audio 0 error, loudnorm ~-16 LUFS, blackdetect 0, faststart (moov
sebelum mdat). Frame t=1,0 (judul S1) + t=59,5 (end card) diekstrak ke
out/qa/ dengan sufiks -cycles untuk dicek visual. Caption ASS dicek terbaca.
"""
import json
import os
import re
import subprocess
import sys

OUT = os.path.expanduser("~/workspace/shorts/nexus-zero-ep5/out")
FILES = {
    "nexus-ep5-cycles-full-16x9.mp4": (1920, 1080),
    "nexus-ep5-cycles-lite-16x9.mp4": (1280, 720),
}
ASS_TITLES = ["WE CAME BACK.", "WHAT STILL GLOWS?",
              "THE FIRST KAIRO NEVER LEFT.", "TO BE CONTINUED"]


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def probe(path):
    r = run(["ffprobe", "-v", "quiet", "-print_format", "json",
             "-show_format", "-show_streams", path])
    return json.loads(r.stdout)


def main():
    problems = []
    ass = os.path.join(OUT, "nexus-ep5-16x9.ass")
    if not os.path.exists(ass):
        problems.append("ASS hilang: nexus-ep5-16x9.ass")
    else:
        text = open(ass, encoding="utf-8", errors="replace").read()
        print(f"nexus-ep5-16x9.ass: {os.path.getsize(ass)} byte, "
              f"{text.count('Dialogue:')} Dialogue")
        for title in ASS_TITLES:
            if title not in text:
                problems.append(f"ASS: judul tidak terbaca: {title!r}")
            else:
                print(f"  caption OK: {title!r}")
    for name, (ew, eh) in FILES.items():
        p = os.path.join(OUT, name)
        if not os.path.exists(p):
            problems.append(f"file hilang: {name}")
            continue
        sz = os.path.getsize(p)
        d = probe(p)
        v = [s for s in d["streams"] if s["codec_type"] == "video"][0]
        a = [s for s in d["streams"] if s["codec_type"] == "audio"][0]
        dur = float(d["format"]["duration"])
        fps = eval(v["r_frame_rate"])
        nframes = int(v["nb_frames"])
        w, h = int(v["width"]), int(v["height"])
        print(f"{name}: {sz} byte, {w}x{h}, {dur:.3f} dtk, {fps:.2f} fps, "
              f"{nframes} frame, v={v['codec_name']} a={a['codec_name']}")
        if abs(dur - 60.0) > 0.05:
            problems.append(f"{name}: durasi {dur}")
        if abs(fps - 24) > 0.01:
            problems.append(f"{name}: fps {fps}")
        if nframes != 1440:
            problems.append(f"{name}: frame {nframes}")
        if (w, h) != (ew, eh):
            problems.append(f"{name}: resolusi {w}x{h} != {ew}x{eh}")
        r = run(["ffmpeg", "-v", "error", "-i", p, "-map", "0:v", "-map", "0:a",
                 "-f", "null", "-"])
        if r.returncode != 0 or r.stderr.strip():
            problems.append(f"{name}: decode error rc={r.returncode}: {r.stderr.strip()[:200]}")
        r = run(["ffmpeg", "-i", p, "-af", "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json",
                 "-f", "null", "-"])
        meas = None
        m = re.search(r"\{\s*\n\s*\"input_i\"[^}]*\}", r.stderr)
        if m:
            meas = json.loads(m.group(0))
        if meas:
            print(f"  loudnorm: I={meas['input_i']} TP={meas['input_tp']} "
                  f"LRA={meas['input_lra']} thr={meas['input_thresh']}")
            if abs(float(meas["input_i"]) + 16) > 1.0:
                problems.append(f"{name}: loudnorm I={meas['input_i']}")
        else:
            problems.append(f"{name}: loudnorm tidak terbaca")
        r = run(["ffmpeg", "-v", "info", "-i", p, "-vf",
                 "blackdetect=d=0.1:pic_th=0.98:pix_th=0.10",
                 "-an", "-f", "null", "-"])
        blacks = [l for l in r.stderr.splitlines() if "blackdetect" in l and "black_start" in l]
        print(f"  blackdetect: {len(blacks)} segmen")
        if blacks:
            problems.append(f"{name}: blackdetect {len(blacks)}: {blacks[:3]}")
        with open(p, "rb") as f:
            head = f.read(64)
        moov_pos = head.find(b"moov")
        mdat_pos = head.find(b"mdat")
        fast = moov_pos != -1 and (mdat_pos == -1 or moov_pos < mdat_pos)
        print(f"  faststart: {'YA' if fast else 'TIDAK'} (moov@{moov_pos} mdat@{mdat_pos})")
        if not fast:
            problems.append(f"{name}: moov tidak di depan")
    qa = os.path.join(OUT, "qa")
    os.makedirs(qa, exist_ok=True)
    full = os.path.join(OUT, "nexus-ep5-cycles-full-16x9.mp4")
    if os.path.exists(full):
        for t, tag in (("1.0", "t1-judul-S1-cycles"), ("59.5", "t595-endcard-cycles")):
            out = os.path.join(qa, f"{tag}.png")
            run(["ffmpeg", "-v", "error", "-y", "-ss", t, "-i", full,
                 "-frames:v", "1", out])
            print(f"frame {tag}: {out} ({os.path.getsize(out)} byte)")
    print("\nPROBLEMS:" if problems else "\nQA LOLOS — TIDAK ADA MASALAH")
    for p in problems:
        print("  -", p)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
