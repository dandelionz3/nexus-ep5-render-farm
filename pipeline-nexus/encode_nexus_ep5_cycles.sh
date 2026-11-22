#!/bin/bash
# Finalize encode NEXUS ZERO Episode 5 — VARIAN Cycles 16:9.
# Frames Cycles via kaggle/frames-cycles-16x9 (global f_0001..f_1440, 24 fps).
# Audio + ASS sama seperti jalur Eevee. TANPA grade.
set -e
NX=~/workspace/shorts/nexus-zero-ep5
OUT=$NX/out
AUDIO=$NX/audio/nexus-audio-60s.m4a
ASS16=$OUT/nexus-ep5-16x9.ass
FRAMES=$NX/kaggle/frames-cycles-16x9
mkdir -p "$OUT"
log() { echo "[$(date +%H:%M:%S)] $*"; }
enc() { # $1=frames $2=ass $3=scale $4=crf $5=preset $6=outfile
  local frames="$1" ass="$2" scale="$3" crf="$4" preset="$5" out="$6"
  local vf="scale=${scale}:flags=lanczos,subtitles=${ass},format=yuv420p"
  log "START $out (crf $crf $preset)"
  ffmpeg -v error -y -framerate 24 -i "$frames/f_%04d.png" -i "$AUDIO" \
    -filter_complex "[0:v]${vf}[v]" -map "[v]" -map 1:a \
    -c:v libx264 -preset "$preset" -crf "$crf" -c:a copy \
    -r 24 -t 60 -movflags +faststart "$out"
  log "DONE $out $(du -h "$out" | cut -f1)"
}
enc "$FRAMES" "$ASS16" "1920:1080" 18 slow   "$OUT/nexus-ep5-cycles-full-16x9.mp4"
enc "$FRAMES" "$ASS16" "1280:720"  28 medium "$OUT/nexus-ep5-cycles-lite-16x9.mp4"
log "ALL CYCLES ENCODES DONE"
ls -la "$OUT"/nexus-ep5-cycles-*.mp4
