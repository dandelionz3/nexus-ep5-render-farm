#!/usr/bin/env python3
"""QA final NEXUS ZERO Episode 5 — 4 file out/ (pola QA Ep 4).
Cek per file: durasi 60.000 dtk, 24 fps, 1440 frame, resolusi, decode
video+audio 0 error, loudnorm ~-16 LUFS, blackdetect 0, faststart (moov
sebelum mdat). Frame t=1,0 (judul S1) + t=59,5 (end card) diekstrak ke
out/qa/ untuk dicek visual. Caption ASS dicek terbaca: judul S1
"WE CAME BACK." + S3 "WHAT STILL GLOWS?" + end card f1380-1439
"THE FIRST KAIRO NEVER LEFT." / "TO BE CONTINUED — EPISODE 6".
"""
import json
import os
import re
import subprocess
import sys

OUT = os.path.expanduser("~/workspace/shorts/nexus-zero-ep5/out")
FILES = {
    "nexus-ep5-full-9x16.mp4": (1080, 1920),
    "nexus-ep5-lite-9x16.mp4": (720, 1280),
    "nexus-ep5-full-16x9.mp4": (1920, 1080),
    "nexus-ep5-lite-16x9.mp4": (1280, 720),
}
ASS_TITLES = ["WE CAME BACK.", "WHAT STILL GLOWS?",
              "THE FIRST KAIRO NEVER LEFT.", "TO BE CONTINUED"]


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r


def probe(path):
    r = run(["ffprobe", "-v", "quiet", "-print_format", "json",
             "-show_format", "-show_streams", path])
    return json.loads(r.stdout)


def main():
    problems = []
    # caption ASS terbaca: file ada + berisi judul S1/S3 + end card
    for ass in ("nexus-ep5-9x16.ass", "nexus-ep5-16x9.ass"):
        p = os.path.join(OUT, ass)
        if not os.path.exists(p):
            problems.append(f"ASS hilang: {ass}")
            continue
        text = open(p, encoding="utf-8", errors="replace").read()
        print(f"{ass}: {os.path.getsize(p)} byte, "
              f"{text.count('Dialogue:')} Dialogue")
        for title in ASS_TITLES:
            if title not in text:
                problems.append(f"{ass}: judul tidak terbaca: {title!r}")
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
        # decode 0 error
        r = run(["ffmpeg", "-v", "error", "-i", p, "-map", "0:v", "-map", "0:a",
                 "-f", "null", "-"])
        if r.returncode != 0 or r.stderr.strip():
            problems.append(f"{name}: decode error rc={r.returncode}: {r.stderr.strip()[:200]}")
        # loudnorm (single-pass measure) — JSON-nya multi-baris, parse blok
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
        # blackdetect
        r = run(["ffmpeg", "-v", "info", "-i", p, "-vf",
                 "blackdetect=d=0.1:pic_th=0.98:pix_th=0.10",
                 "-an", "-f", "null", "-"])
        blacks = [l for l in r.stderr.splitlines() if "blackdetect" in l and "black_start" in l]
        print(f"  blackdetect: {len(blacks)} segmen")
        if blacks:
            problems.append(f"{name}: blackdetect {len(blacks)}: {blacks[:3]}")
        # faststart: moov sebelum mdat?
        with open(p, "rb") as f:
            head = f.read(64)
        moov_pos = head.find(b"moov")
        mdat_pos = head.find(b"mdat")
        fast = moov_pos != -1 and (mdat_pos == -1 or moov_pos < mdat_pos)
        print(f"  faststart: {'YA' if fast else 'TIDAK'} (moov@{moov_pos} mdat@{mdat_pos})")
        if not fast:
            problems.append(f"{name}: moov tidak di depan")
    # frame t=1,0 + t=59,5 dari full 9x16
    qa = os.path.join(OUT, "qa")
    os.makedirs(qa, exist_ok=True)
    full9 = os.path.join(OUT, "nexus-ep5-full-9x16.mp4")
    if os.path.exists(full9):
        for t, tag in (("1.0", "t1-judul-S1"), ("59.5", "t595-endcard")):
            out = os.path.join(qa, f"{tag}.png")
            run(["ffmpeg", "-v", "error", "-y", "-ss", t, "-i", full9,
                 "-frames:v", "1", out])
            print(f"frame {tag}: {out} ({os.path.getsize(out)} byte)")
    print("\nPROBLEMS:" if problems else "\nQA LOLOS — TIDAK ADA MASALAH")
    for p in problems:
        print("  -", p)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
