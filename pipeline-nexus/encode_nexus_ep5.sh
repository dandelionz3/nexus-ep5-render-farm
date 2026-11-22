#!/bin/bash
# Finalize encode NEXUS ZERO Episode 5 "THE EMPTY HALL" -- 4 files, out/.
# Frames via /tmp/nx5 symlinks (f9/f16, global f_0001..f_1440, 24 fps).
# Audio copied as-is (no re-encode): nexus-audio-60s.m4a, 60.000 s.
# Pattern copied from Ep 4 encode_nexus_ep4.sh (crf 18 slow / lite crf 28
# medium, upscale lanczos, audio -c:a copy, -movflags +faststart).
# Judul bakar S1 "WE CAME BACK." + S3 "WHAT STILL GLOWS?" + end card
# f1380-1439 via ASS SAJA (TIDAK ADA teks 3D judul di set).
set -e
NX=~/workspace/shorts/nexus-zero-ep5
OUT=$NX/out
AUDIO=$NX/audio/nexus-audio-60s.m4a
ASS9=$OUT/nexus-ep5-9x16.ass
ASS16=$OUT/nexus-ep5-16x9.ass
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

enc /tmp/nx5/f9  "$ASS9"  "1080:1920" 18 slow   "$OUT/nexus-ep5-full-9x16.mp4"
enc /tmp/nx5/f9  "$ASS9"  "720:1280"  28 medium "$OUT/nexus-ep5-lite-9x16.mp4"
enc /tmp/nx5/f16 "$ASS16" "1920:1080" 18 slow   "$OUT/nexus-ep5-full-16x9.mp4"
enc /tmp/nx5/f16 "$ASS16" "1280:720"  28 medium "$OUT/nexus-ep5-lite-16x9.mp4"
log "ALL 4 ENCODES DONE"
ls -la "$OUT"/*.mp4
