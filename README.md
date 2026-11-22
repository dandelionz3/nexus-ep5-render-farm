# nexus-ep5-render-farm — NEXUS ZERO Episode 5 "THE EMPTY HALL"

GitHub Actions render farm (Eevee) untuk Episode 5. Repo dibuat 22 Nov 2026
(publik, kosong). Pola mengikuti farm Ep 4 persis — SEMUA file baru untuk
Ep 5, JANGAN pakai repo/workflow Ep 1/2/3/4.

## Struktur

```
pipeline-nexus/                 <- isi ~/workspace/shorts/nexus-zero-ep5/pipeline/
  build_scene_nexus_ep5.py      scene: aula memori GELAP, 213 rak (212 gelap + 1 amber), Kairo 001
  animate_nexus_ep5.py          keyframe plan.json (amber S3, Kairo 001 di rak)
  plan_nexus_ep5.py             generator plan.json (1440 baris)
  plan.json                     plan jadi (sudah digenerate + self-check lolos)
  validate_build.py             validasi scene TANPA render (Blender)
  validate_headless.py          stub bpy/mathutils — dry-run validate + animate 1..1440
  encode_nexus_ep5.sh           finalize 4 file (full + lite, 9:16 + 16:9)
  encode_nexus_ep5_cycles.sh    finalize varian Cycles 16:9
  merge_cycles_ep5.sh           gabung 4 job Kaggle -> 1440 frame
  qa_ep5.py / qa_ep5_cycles.py  QA akhir
.github/workflows/
  render-nexus-ep5-test.yml     6 job x 20 frame = 120 (S1/S2/S3/S4/S5/S7, 9:16)
  render-nexus-ep5-full.yml     40 job x 72 frame = 2880
```

## Target render (pola Ep 4)

- Test: 6 job x 20 frame = 120 (9:16 540x960 lensk 0.62).
- Full: 40 job x 72 frame = 2880 frame (9:16 540x960 lensk 0.62 +
  16:9 960x540 lensk 1.00; plan f 0-1439 -> frame Blender 1-1440).
- Blender 4.5.3, Eevee 6 samples, ray OFF, vol tile 16, DOF ON, MB ON,
  subsurf 1, bevel 0, AgX. Frame dinilai dari file yang ada (bukan exit code).
- Release baru: `nexus-ep5-full-run-<tanggal>` (frame zip per job).

## Pelajaran Ep 4 (WAJIB)
- Workflow YAML SELALU `${{ }}` double-brace — single-brace `${ matrix.X }`
  diteruskan mentah ke bash dan membunuh full run v1 (40/40 gagal).
  grep `\$\{ [A-Za-z_]` harus bersih SEBELUM trigger.
- validate_build HARUS dijalankan (Ep 4: NameError `_random2` lolos
  cross-check statis). Ep 5: validate dijalankan via stub headless
  (VALIDATE_BUILD_OK) karena Blender TIDAK terpasang di VM; farm test
  adalah validasi Blender-asli pertama.
- /tmp ke-reset tiap VM restart — jangan simpan clone/frame hanya di /tmp.
- Validasi PNG dengan decode penuh PIL (bukan cuma header).

## Status
- Pipeline + plan.json: SIAP (lokal, validate_headless OK).
- Repo: dibuat, push pertama (pipeline + workflow test + full).
- **FARM TEST 22 Nov ~14:5x WIB: run 44999774330 completed/success 6/6, 120/120 frame, PIL BAD 0 — TAPI STILLS GAGAL: S2 kamera di dalam rak (68/216 frame), S5 two-shot Kairo 214 terpotong, S7 EVA siluet hitam, S4 fokus lunak. FULL RUN DITAHAN sampai plan_nexus_ep5.py diperbaiki (jalur kamera S2 ke lorong x=80, framing S5, fill S7, focus S4) + test ulang bersih. Detail: PROGRESS.md Fase 4.**
- JANGAN posting ke mana pun. JANGAN encode video dulu (ASS masih dikerjakan
  tim audio paralel). Frame + verifikasi saja.
