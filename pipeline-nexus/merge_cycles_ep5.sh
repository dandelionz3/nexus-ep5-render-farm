#!/bin/bash
# Merge + verifikasi frame Cycles Ep 5 dari 4 job Kaggle.
# Sumber: kaggle/out-cycles-full/out/full_{a,b,c,d}/f_*.png (penomoran GLOBAL:
# a=f_0001..0360, b=f_0361..0720, c=f_0721..1080, d=f_1081..1440).
# Tujuan: kaggle/frames-cycles-16x9/f_0001..f_1440.png (salin, tanpa rename).
# Keluar non-zero bila ada yang kurang / tidak kontigu / PNG rusak.
# PNG divalidasi dengan decode PENUH PIL (bukan cuma header — pelajaran Ep 4).
set -e
NX=~/workspace/shorts/nexus-zero-ep5
SRC=$NX/kaggle/out-cycles-full/out
DST=$NX/kaggle/frames-cycles-16x9
mkdir -p "$DST"
log() { echo "[$(date +%H:%M:%S)] $*"; }
for t in a b c d; do
  n=$(ls "$SRC/full_$t"/f_*.png 2>/dev/null | wc -l)
  log "full_$t: $n/360 frame"
  [ "$n" -eq 360 ] || { log "GAGAL: full_$t kurang frame"; exit 1; }
done
cp "$SRC/full_a"/f_*.png "$SRC/full_b"/f_*.png "$SRC/full_c"/f_*.png "$SRC/full_d"/f_*.png "$DST/"
total=$(ls "$DST"/f_*.png | wc -l)
log "total di $DST: $total/1440"
[ "$total" -eq 1440 ] || { log "GAGAL: total bukan 1440"; exit 1; }
# Kontiguitas f_0001..f_1440
missing=0
for i in $(seq -w 1 1440); do
  [ -f "$DST/f_$i.png" ] || { log "HILANG: f_$i.png"; missing=$((missing+1)); }
done
[ "$missing" -eq 0 ] || { log "GAGAL: $missing frame hilang"; exit 1; }
# PNG valid (decode PENUH PIL, bukan cuma header — pelajaran Ep 4)
python3 - "$DST" <<'PYEOF'
import glob, sys
from PIL import Image
dst = sys.argv[1]
bad = 0
for f in sorted(glob.glob(dst + '/f_*.png')):
    try:
        with Image.open(f) as im:
            im.load()
    except Exception as e:
        bad += 1
        print('RUSAK:', f, e)
print('bad =', bad)
sys.exit(1 if bad else 0)
PYEOF
log "cek PNG (decode penuh PIL): LOLOS"
log "MERGE LOLOS — 1440/1440 frame, kontigu, PNG valid"
du -sh "$DST"
