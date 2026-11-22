#!/usr/bin/env python3
# plan_nexus_ep5.py — generator plan.json NEXUS ZERO Episode 5 "THE EMPTY HALL".
# Satu baris per frame (f 0..1439). Per frame: rig tiap karakter, intensitas
# lampu, kamera (x,y,z,target,focus,lens,roll Dutch), flag.
# Murni Python (tanpa bpy). Pola: plan_nexus_ep4.py.
# Set: aula memori GELAP (RX=80, 60x48 m, dinding 16 m, wajah NEXUS HILANG,
# gerbang 5x6 m TERBUKA PENUH sejak S1, 213 rak arsip — 212 gelap + 1 amber
# di ujung terjauh (RX, -20)).
# TIDAK ADA flash putih di Ep 5 (berakhir hitam + end card).
# TIDAK ADA merah di Ep 5 — satu frame pun (kolom gelap, lampu nexus/eye = 0
# selalu, TIDAK ADA Sentinel, TIDAK ADA 213 Kairo, TIDAK ADA kota fajar).
# Flag baru Ep 5: amber_shelf (S3 naik 0..1, bertahan S4-S6/S8, meredup S8),
# dawn_line (S1/S7 saja, 0..1 — garis fajar tipis lewat gerbang).
# Flag warisan: gate_open = 1.0 di SEMUA frame; scar_glow = True di semua
# frame (kilau biru TERANG lanjutan Ep 3 S6); nexus_face = False SELALU.
#   python3 plan_nexus_ep5.py [plan.json]
import json
import math
import os
import sys

N = 1440
RX = 80.0   # offset aula memori (sama dengan build_scene_nexus_ep4/5.py)
AMBER_X, AMBER_Y = RX, -20.0  # rak amber di ujung terjauh lorong tengah
ALL_CHARS = ["KAI", "EVA", "KAI001"]


def clamp(x, a, b):
    return max(a, min(b, x))


def lerp(a, b, t):
    return a + (b - a) * t


def smooth(t):
    t = clamp(t, 0.0, 1.0)
    return t * t * (3 - 2 * t)


def seg_t(f, a, b):
    return clamp((f - a) / max(1, b - a), 0.0, 1.0)


def shake(f, amp, freq=1.7):
    return amp * (math.sin(f * 0.9 * freq) * 0.6 + math.sin(f * 2.3 * freq + 1.3) * 0.4)


def walk_cycle(phase, amp, arm_amp=None):
    if arm_amp is None:
        arm_amp = amp * 0.8
    return {
        "legL": amp * math.sin(phase),
        "legR": -amp * math.sin(phase),
        "armL": -arm_amp * math.sin(phase),
        "armR": arm_amp * math.sin(phase),
        "bob": 0.045 * abs(math.cos(phase)),
    }


def char(x=0, y=0, z=0, rot=0, lean=0, squash=1.0, crouch=0.0, pitch=0.0,
         head_tilt=0, head_turn=0, armL=0, armR=0, legL=0, legR=0,
         eye_red=False, vis=True, mouthW=1.0, mouthH=1.0):
    return {"x": round(x, 3), "y": round(y, 3), "z": round(z, 3), "rot": round(rot, 2),
            "lean": round(lean, 2), "squash": round(squash, 3), "crouch": round(crouch, 3),
            "pitch": round(pitch, 2), "head_tilt": round(head_tilt, 2),
            "head_turn": round(head_turn, 2), "armL": round(armL, 2), "armR": round(armR, 2),
            "legL": round(legL, 2), "legR": round(legR, 2),
            "eye_red": bool(eye_red), "vis": bool(vis),
            "mouthW": round(mouthW, 2), "mouthH": round(mouthH, 2)}


def hidden():
    return char(vis=False)


def cam(x, y, z, tx, ty, tz, focus, lens, roll=0.0):
    return {"x": round(x, 3), "y": round(y, 3), "z": round(z, 3),
            "tx": round(tx, 3), "ty": round(ty, 3), "tz": round(tz, 3),
            "focus": round(focus, 2), "lens": round(lens, 1),
            "roll": round(roll, 2)}


def lights(nexus=0, gate=400, rim=0, eye=0, core=0, eva=0, fill=60,
           dawn=0, warm=0):
    """Ep 5: nexus=0 SELALU (wajah hilang), eye=0 SELALU (TIDAK ADA Sentinel),
    core=0 SELALU (data core tetap di ruang inti), warm=0 SELALU (TIDAK ADA
    kota fajar), rim = rim BIRU di belakang EVA/bekas luka (bukan merah),
    gate = putih gerbang, eva = biru EVA, fill = isi ruangan gelap (rendah),
    dawn = garis fajar tipis lewat gerbang (HANYA S1/S7)."""
    return {"nexus": round(nexus, 1), "gate": round(gate, 1), "rim": round(rim, 1),
            "eye": round(eye, 1), "core": round(core, 1), "eva": round(eva, 1),
            "fill": round(fill, 1), "dawn": round(dawn, 1),
            "warm": round(warm, 1)}


def kairo001_at_shelf(head_tilt=0, head_turn=0, lean=4):
    """Kairo 001 TIDAK pernah meninggalkan raknya (S4-S8): berdiri di rak
    amber (RX, -20), menghadap lorong (+Y, rot=180 — menghadap Kairo 214
    yang mendekat dari gerbang)."""
    return char(AMBER_X, AMBER_Y, 0, rot=180, lean=lean, head_tilt=head_tilt,
                head_turn=head_turn, armL=5, armR=5, legL=0, legR=0)


rows = []
for f in range(N):
    chars = {}
    # Backpack + data core tetap di ruang inti — TIDAK muncul di Ep 5.
    # Gerbang TERBUKA PENUH sejak S1 (gate_open = 1 konstan). Bekas luka
    # menyala TERANG sejak frame 0 (lanjutan Ep 3 S6). Wajah NEXUS TIDAK
    # ADA (nexus_face = False selalu). TIDAK ADA 213 Kairo, TIDAK ADA
    # Sentinel — aula harus terasa kosong.
    props = {"core_in_hand": False, "core_table": False, "core_socket": False,
             "backpack": False, "backpack_dropped": False, "rain": False,
             "gate": True, "scar_glow": True, "nexus_face": False}
    gate_open = 1.0
    amber_shelf = 0.0
    dawn_line = 0.0
    flash_white = False  # TIDAK ADA flash di Ep 5

    # ================= S1 HOOK (0-71) — "WE CAME BACK." =================
    if f < 72:
        # Kairo 214 + EVA melangkah masuk lewat gerbang putih di belakang
        # mereka, kembali ke aula memori; langit-langit KOSONG — wajah NEXUS
        # HILANG; aula gelap, barisan rak hitam; garis fajar tipis masuk
        # lewat gerbang. Shake halus HANYA di S1 (kamera ikut hening sesudahnya).
        dawn_line = 1.0
        t = seg_t(f, 0, 71)
        kai_y = lerp(20.0, 10.0, smooth(t))
        eva_y = lerp(19.0, 9.0, smooth(t))
        ph = f * 0.35
        c = walk_cycle(ph, 26)
        sh = shake(f, 0.03)
        chars["KAI"] = char(RX, kai_y, c["bob"], rot=180, lean=6, head_tilt=0,
                            armL=c["armL"], armR=c["armR"],
                            legL=c["legL"], legR=c["legR"])
        chars["EVA"] = char(RX + 2.0, eva_y, c["bob"], rot=180, lean=2, head_tilt=0,
                            armL=c["armL"], armR=c["armR"],
                            legL=c["legL"], legR=c["legR"])
        chars["KAI001"] = hidden()  # belum ditemukan — rak amber masih gelap
        if f < 24:
            # 1a: low-angle hero, slow push-in, Dutch 8 derajat
            chars_cam = cam(RX + 0.6, lerp(-7.0, -5.5, smooth(seg_t(f, 0, 23))) + sh,
                            lerp(1.0, 1.1, smooth(seg_t(f, 0, 23))),
                            RX, 12.0, 1.5, lerp(10.0, 8.0, smooth(seg_t(f, 0, 23))),
                            lerp(52, 50, seg_t(f, 0, 23)), roll=8)
        elif f < 48:
            # 1b: push-in lanjut, Kairo + EVA membesar
            chars_cam = cam(RX + 0.6, lerp(-5.5, -4.0, smooth(seg_t(f, 24, 47))) + sh,
                            lerp(1.1, 1.2, smooth(seg_t(f, 24, 47))),
                            RX + 0.5, 11.0, 1.45, lerp(8.0, 6.5, smooth(seg_t(f, 24, 47))),
                            lerp(50, 48, seg_t(f, 24, 47)), roll=8)
        else:
            # 1c: wide hero, Kairo ~25% tinggi frame; judul besar (ASS saja)
            chars_cam = cam(RX, -8.0, 2.0, RX, 14.0, 1.5, 16.0, 48, roll=8)
        li = lights(gate=450, rim=200, eva=300, fill=60, dawn=150 * dawn_line)
    # ================= S2 DUA RATUS TIGA BELAS RAK (72-287) =================
    elif f < 288:
        # Slow tracking menyusuri lorong tengah antar barisan rak gelap —
        # kamera menghitung kekosongan, rak demi rak, semua gelap.
        if f < 144:
            # 2a: EVA berjalan di antara rak-rak gelap; 213 slot lampu PADAM
            t = seg_t(f, 72, 143)
            eva_y = lerp(8.0, 2.0, smooth(t))
            ph = f * 0.30
            c = walk_cycle(ph, 20)
            chars["EVA"] = char(RX + 0.3, eva_y, c["bob"], rot=180, lean=2, head_tilt=0,
                                armL=c["armL"], armR=c["armR"],
                                legL=c["legL"], legR=c["legR"])
            chars["KAI"] = char(RX - 0.9, eva_y + 3.0, c["bob"], rot=180, lean=5, head_tilt=0,
                                armL=c["armL"], armR=c["armR"],
                                legL=c["legL"], legR=c["legR"])
            chars_cam = cam(RX + 3.5, eva_y - 7.0, 1.7, RX + 0.3, eva_y, 1.4,
                            6.0, 50)
            li = lights(gate=400, rim=150, eva=300, fill=55)
        elif f < 216:
            # 2b: tracking lanjut, barisan rak gelap berganti — tanpa ujung
            t = seg_t(f, 144, 215)
            eva_y = lerp(2.0, -4.0, smooth(t))
            ph = f * 0.30
            c = walk_cycle(ph, 20)
            chars["EVA"] = char(RX + 0.3, eva_y, c["bob"], rot=180, lean=2, head_tilt=0,
                                armL=c["armL"], armR=c["armR"],
                                legL=c["legL"], legR=c["legR"])
            chars["KAI"] = char(RX - 0.9, eva_y + 3.0, c["bob"], rot=180, lean=5, head_tilt=0,
                                armL=c["armL"], armR=c["armR"],
                                legL=c["legL"], legR=c["legR"])
            chars_cam = cam(RX + 3.5, eva_y - 7.0, 1.7, RX + 0.3, eva_y, 1.4,
                            6.0, 50)
            li = lights(gate=400, rim=150, eva=300, fill=55)
        else:
            # 2c: EVA berhenti di antara rak yang padam; Kairo 214 di belakangnya
            chars["EVA"] = char(RX + 0.3, -6.0, 0, rot=180, lean=2, head_tilt=0,
                                armL=5, armR=5, legL=0, legR=0)
            chars["KAI"] = char(RX - 0.9, -3.0, 0, rot=180, lean=5, head_tilt=0,
                                armL=5, armR=5, legL=0, legR=0)
            chars_cam = cam(RX + 3.0, -13.0, 1.7, RX + 0.3, -6.0, 1.4, 6.0, 50)
            li = lights(gate=400, rim=150, eva=320, fill=55)
        chars["KAI001"] = hidden()  # rak amber masih gelap
    # ================= S3 APA YANG MASIH MENYALA? (288-599) =================
    elif f < 600:
        # Slow dolly-in ke ujung aula: SATU rak menyala hangat amber.
        # Amber naik PELAN saat rak disadari (swell lembut, bukan nyala mendadak).
        amber_shelf = smooth(seg_t(f, 288, 360))
        if f < 360:
            # 3a: dolly-in, Kairo 214 menoleh — ia melihat cahaya itu dulu
            t = seg_t(f, 288, 359)
            chars["KAI"] = char(RX - 0.9, -3.0, 0, rot=180, lean=5,
                                head_turn=lerp(0, -25, smooth(t)),
                                armL=5, armR=5, legL=0, legR=0)
            chars["EVA"] = char(RX + 0.3, -6.0, 0, rot=180, lean=2, head_tilt=0,
                                armL=5, armR=5, legL=0, legR=0)
            chars_cam = cam(RX, lerp(6.0, -2.0, smooth(t)), 1.8,
                            RX, AMBER_Y, 2.5, lerp(18.0, 14.0, smooth(t)), 50)
            li = lights(gate=450, rim=180, eva=400, fill=55)
        elif f < 480:
            # 3b: dolly-in lanjut, rak amber membesar; teks "WHAT STILL GLOWS?"
            t = seg_t(f, 360, 479)
            chars["KAI"] = char(RX - 0.9, -3.0, 0, rot=180, lean=5, head_turn=-25,
                                armL=5, armR=5, legL=0, legR=0)
            chars["EVA"] = char(RX + 0.3, -6.0, 0, rot=180, lean=2, head_tilt=0,
                                armL=5, armR=5, legL=0, legR=0)
            chars_cam = cam(RX, lerp(-2.0, -8.0, smooth(t)), 1.8,
                            RX, AMBER_Y, 2.5, lerp(14.0, 10.0, smooth(t)), 52)
            li = lights(gate=450, rim=180, eva=400, fill=55)
        else:
            # 3c: dolly-in lanjut -> rak TERBUKA; Kairo + EVA mendekat pelan
            t = seg_t(f, 480, 599)
            kai_y = lerp(-3.0, -10.0, smooth(t))
            eva_y = lerp(-6.0, -12.0, smooth(t))
            ph = f * 0.30
            c = walk_cycle(ph, 16)
            chars["KAI"] = char(RX - 0.9, kai_y, c["bob"], rot=180, lean=5, head_turn=-25,
                                armL=c["armL"], armR=c["armR"],
                                legL=c["legL"], legR=c["legR"])
            chars["EVA"] = char(RX + 0.3, eva_y, c["bob"], rot=180, lean=2, head_tilt=0,
                                armL=c["armL"], armR=c["armR"],
                                legL=c["legL"], legR=c["legR"])
            chars_cam = cam(RX, lerp(-8.0, -14.0, smooth(t)), 1.8,
                            RX, AMBER_Y, 2.2, lerp(10.0, 7.0, smooth(t)), 55)
            li = lights(gate=450, rim=180, eva=400, fill=55)
        # Kairo 001 sudah ada di rak sejak S3 (terlihat samar saat rak menyala)
        chars["KAI001"] = kairo001_at_shelf() if f >= 360 else hidden()
    # ================= S4 KAIRO PERTAMA (600-863) =================
    elif f < 864:
        amber_shelf = 1.0
        if f < 672:
            # 4a: dolly-in ke rak -> medium Kairo 001 (wajah sama, lebih tua)
            t = seg_t(f, 600, 671)
            chars["KAI"] = char(RX - 0.9, -18.3, 0, rot=0, lean=4, head_tilt=0,
                                armL=5, armR=5, legL=0, legR=0)
            chars["EVA"] = char(RX + 2.5, -16.0, 0, rot=180, lean=2, head_tilt=0,
                                armL=5, armR=5, legL=0, legR=0)
            chars["KAI001"] = kairo001_at_shelf()
            chars_cam = cam(RX + 0.5, lerp(-14.0, -16.5, smooth(t)),
                            lerp(1.8, 1.7, smooth(t)),
                            RX, AMBER_Y, 1.5, lerp(7.0, 5.0, smooth(t)),
                            lerp(55, 65, t))
            li = lights(gate=400, rim=180, eva=350, fill=55)
        elif f < 768:
            # 4b: dolly-in lanjut -> ECU Kairo 001; bekas luka yang SAMA HARUS terlihat
            t = seg_t(f, 672, 767)
            chars["KAI"] = char(RX - 0.9, -18.3, 0, rot=0, lean=4, head_tilt=0,
                                armL=5, armR=5, legL=0, legR=0)
            chars["EVA"] = char(RX + 2.5, -16.0, 0, rot=180, lean=2, head_tilt=0,
                                armL=5, armR=5, legL=0, legR=0)
            chars["KAI001"] = kairo001_at_shelf()
            chars_cam = cam(lerp(RX + 0.3, RX + 0.15, smooth(t)), lerp(-16.5, -18.6, smooth(t)),
                            lerp(1.7, 1.62, smooth(t)),
                            RX, AMBER_Y, 1.5, lerp(5.0, 2.4, smooth(t)), lerp(65, 85, t))
            li = lights(gate=400, rim=180, eva=350, fill=55)
        else:
            # 4c: ECU tahan, Kairo 001 menatap Kairo 214
            chars["KAI"] = char(RX - 0.9, -18.3, 0, rot=0, lean=4, head_tilt=0,
                                armL=5, armR=5, legL=0, legR=0)
            chars["EVA"] = char(RX + 2.5, -16.0, 0, rot=180, lean=2, head_tilt=0,
                                armL=5, armR=5, legL=0, legR=0)
            chars["KAI001"] = kairo001_at_shelf()
            chars_cam = cam(RX + 0.15, -18.6, 1.62, RX, AMBER_Y, 1.5, 2.4, 85)
            li = lights(gate=400, rim=180, eva=350, fill=55)
    # ================= S5 MESIN MEMENANGKAN PERANG (864-1055) =================
    elif f < 1056:
        amber_shelf = 1.0
        # Two-shot Kairo 214 + Kairo 001 — dua wajah yang sama, 25 tahun
        # terpisah, dalam satu frame; cahaya amber + biru bekas luka.
        if f < 936:
            # 5a: Kairo 001 bicara; Kairo 214 mendengarkan
            t = seg_t(f, 864, 935)
            chars["KAI"] = char(RX - 1.1, -18.4, 0, rot=0, lean=4, head_tilt=0,
                                armL=5, armR=5, legL=0, legR=0)
            chars["KAI001"] = kairo001_at_shelf()
            chars["EVA"] = char(RX + 2.5, -16.0, 0, rot=180, lean=2, head_tilt=0,
                                armL=5, armR=5, legL=0, legR=0)
            chars_cam = cam(RX + 0.4, lerp(-15.5, -16.2, smooth(t)), 1.6,
                            RX - 0.2, -19.2, 1.45, 4.5, 55)
            li = lights(gate=380, rim=200, eva=350, fill=55)
        elif f < 1008:
            # 5b: two-shot lanjut, Kairo 001 menatap lurus
            chars["KAI"] = char(RX - 1.1, -18.4, 0, rot=0, lean=4, head_tilt=0,
                                armL=5, armR=5, legL=0, legR=0)
            chars["KAI001"] = kairo001_at_shelf()
            chars["EVA"] = char(RX + 2.5, -16.0, 0, rot=180, lean=2, head_tilt=0,
                                armL=5, armR=5, legL=0, legR=0)
            chars_cam = cam(RX + 0.4, -16.2, 1.6, RX - 0.2, -19.2, 1.45, 4.5, 55)
            li = lights(gate=380, rim=200, eva=350, fill=55)
        else:
            # 5c: two-shot tahan, Kairo 214 diam satu detik penuh
            chars["KAI"] = char(RX - 1.1, -18.4, 0, rot=0, lean=4, head_tilt=-2,
                                armL=5, armR=5, legL=0, legR=0)
            chars["KAI001"] = kairo001_at_shelf()
            chars["EVA"] = char(RX + 2.5, -16.0, 0, rot=180, lean=2, head_tilt=0,
                                armL=5, armR=5, legL=0, legR=0)
            chars_cam = cam(RX + 0.4, -16.2, 1.6, RX - 0.2, -19.2, 1.45, 4.5, 55)
            li = lights(gate=380, rim=200, eva=350, fill=55)
    # ================= S6 NEXUS BUKAN MUSUH (1056-1199) =================
    elif f < 1200:
        amber_shelf = 1.0
        if f < 1120:
            # 6a: wide aula, lalu slow push-in ke Kairo 001
            t = seg_t(f, 1056, 1119)
            chars["KAI"] = char(RX - 1.1, -18.4, 0, rot=0, lean=4, head_tilt=0,
                                armL=5, armR=5, legL=0, legR=0)
            chars["KAI001"] = kairo001_at_shelf()
            chars["EVA"] = char(RX + 2.5, -16.0, 0, rot=180, lean=2, head_tilt=0,
                                armL=5, armR=5, legL=0, legR=0)
            chars_cam = cam(RX, lerp(-4.0, -8.0, smooth(t)), lerp(3.5, 2.6, smooth(t)),
                            RX, AMBER_Y, 2.0, lerp(20.0, 14.0, smooth(t)),
                            lerp(46, 50, t))
            li = lights(gate=380, rim=200, eva=300, fill=55)
        else:
            # 6b: push-in lanjut -> close Kairo 001; wajah memenuhi frame
            t = seg_t(f, 1120, 1199)
            chars["KAI"] = char(RX - 1.1, -18.4, 0, rot=0, lean=4, head_tilt=0,
                                armL=5, armR=5, legL=0, legR=0)
            chars["KAI001"] = kairo001_at_shelf()
            chars["EVA"] = char(RX + 2.5, -16.0, 0, rot=180, lean=2, head_tilt=0,
                                armL=5, armR=5, legL=0, legR=0)
            chars_cam = cam(RX + 0.3, lerp(-8.0, -15.0, smooth(t)),
                            lerp(2.6, 1.8, smooth(t)),
                            RX, AMBER_Y, 1.6, lerp(14.0, 6.0, smooth(t)),
                            lerp(50, 60, t))
            li = lights(gate=380, rim=200, eva=300, fill=55)
    # ================= S7 GERBANG TETAP TERBUKA (1200-1319) =================
    elif f < 1320:
        # Tracking ke gerbang: EVA berdiri di gerbang putih yang terbuka —
        # PENJAGA GERBANG; ia TIDAK menoleh ke Kairo 001; cahaya fajar masuk
        # tipis; gerbang kini terbuka dua arah. Kairo 214 + Kairo 001 tetap
        # di rak amber (jauh di belakang, satu titik amber di ujung aula).
        amber_shelf = 1.0
        dawn_line = 1.0
        if f < 1260:
            # 7a: tracking ke gerbang
            t = seg_t(f, 1200, 1259)
            chars["EVA"] = char(RX, 21.0, 0, rot=180, lean=2, head_tilt=0,
                                armL=5, armR=5, legL=0, legR=0)
            chars["KAI"] = char(RX - 1.1, -18.4, 0, rot=0, lean=4, head_tilt=0,
                                armL=5, armR=5, legL=0, legR=0)
            chars["KAI001"] = kairo001_at_shelf()
            chars_cam = cam(RX + 1.5, lerp(12.0, 15.0, smooth(t)), 1.8,
                            RX, 21.0, 1.6, lerp(10.0, 7.0, smooth(t)), 50)
            li = lights(gate=500, rim=150, eva=400, fill=70, dawn=150 * dawn_line)
        else:
            # 7b: tracking lanjut, gerbang membesar di belakang EVA
            chars["EVA"] = char(RX, 21.0, 0, rot=180, lean=2, head_tilt=0,
                                armL=5, armR=5, legL=0, legR=0)
            chars["KAI"] = char(RX - 1.1, -18.4, 0, rot=0, lean=4, head_tilt=0,
                                armL=5, armR=5, legL=0, legR=0)
            chars["KAI001"] = kairo001_at_shelf()
            chars_cam = cam(RX + 0.8, 16.5, 1.8, RX, 21.5, 1.6, 7.0, 50)
            li = lights(gate=500, rim=150, eva=400, fill=70, dawn=150 * dawn_line)
    # ================= S8 TWIST (1320-1439) =================
    else:
        # ECU Kairo 001 -> hitam. Amber meredup PELAN; end card f1380-1439 (ASS).
        amber_shelf = lerp(1.0, 0.1, smooth(seg_t(f, 1320, 1439)))
        if f < 1380:
            # 8a: ECU Kairo 001, hook terakhir hampir berbisik
            chars["KAI001"] = kairo001_at_shelf()
            chars["KAI"] = char(RX - 1.1, -18.4, 0, rot=0, lean=4, head_tilt=-2,
                                armL=5, armR=5, legL=0, legR=0)
            chars["EVA"] = char(RX, 21.0, 0, rot=180, lean=2, head_tilt=0,
                                armL=5, armR=5, legL=0, legR=0)
            chars_cam = cam(RX + 0.15, -18.6, 1.62, RX, AMBER_Y, 1.5, 2.4, 85)
            li = lights(gate=300, rim=180, eva=300, fill=55)
        else:
            # 8b: ECU lanjut -> hitam + end card (f1380-1439, ASS)
            chars["KAI001"] = kairo001_at_shelf()
            chars["KAI"] = char(RX - 1.1, -18.4, 0, rot=0, lean=4, head_tilt=-2,
                                armL=5, armR=5, legL=0, legR=0)
            chars["EVA"] = char(RX, 21.0, 0, rot=180, lean=2, head_tilt=0,
                                armL=5, armR=5, legL=0, legR=0)
            chars_cam = cam(RX + 0.15, -18.6, 1.62, RX, AMBER_Y, 1.5,
                            lerp(2.4, 2.6, smooth(seg_t(f, 1380, 1439))), 85)
            # meredup menuju hitam (end card di atas hitam)
            dim = 1.0 - 0.92 * smooth(seg_t(f, 1400, 1439))
            li = lights(gate=300 * dim, rim=180 * dim, eva=300 * dim,
                        fill=55 * dim)

    # pastikan SEMUA karakter ada di tiap baris (0 frame kosong)
    for _p in ALL_CHARS:
        if _p not in chars:
            chars[_p] = hidden()

    rows.append({"f": f, "t": round(f / 24.0, 4), "chars": chars, "lights": li,
                 "cam": chars_cam, "props": props, "flash_white": flash_white,
                 "gate_open": round(gate_open, 3),
                 "amber_shelf": round(amber_shelf, 3),
                 "dawn_line": round(dawn_line, 3)})


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "plan.json")
    with open(out, "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, separators=(",", ":")) + "\n")
    print(f"WROTE {out}: {len(rows)} rows")
    # self-checks
    assert len(rows) == N
    assert rows[0]["f"] == 0 and rows[-1]["f"] == N - 1
    flashes = [r["f"] for r in rows if r["flash_white"]]
    assert flashes == [], f"flash frames (harus kosong di Ep 5): {flashes}"
    empty_rows = [r["f"] for r in rows if not r["chars"]]
    assert not empty_rows, f"frame kosong: {empty_rows}"
    missing = [(r["f"], [p for p in ALL_CHARS if p not in r["chars"]])
               for r in rows if any(p not in r["chars"] for p in ALL_CHARS)]
    assert not missing, f"karakter hilang: {missing[:5]}"
    gate = [r["f"] for r in rows if r["gate_open"] > 0]
    assert gate == list(range(N)), f"gate_open harus 1.0 di semua frame"
    nexus = [r["f"] for r in rows if r["lights"]["nexus"] > 0]
    assert nexus == [], f"nexus light harus 0 selalu: {nexus[:5]}"
    eye = [r["f"] for r in rows if r["lights"]["eye"] > 0]
    assert eye == [], f"eye light harus 0 selalu: {eye[:5]}"
    warm = [r["f"] for r in rows if r["lights"]["warm"] > 0]
    assert warm == [], f"warm light harus 0 selalu (TIDAK ADA kota): {warm[:5]}"
    core = [r["f"] for r in rows if r["lights"]["core"] > 0]
    assert core == [], f"core light harus 0 selalu: {core[:5]}"
    face = [r["f"] for r in rows if r["props"]["nexus_face"]]
    assert face == [], f"nexus_face harus False selalu: {face[:5]}"
    scar = [r["f"] for r in rows if r["props"]["scar_glow"]]
    assert scar == list(range(N)), "scar_glow harus True di semua frame"
    # amber_shelf: 0 di S1-S2, naik S3 (288-360), 1.0 di S4-S7, meredup S8
    am = [(r["f"], r["amber_shelf"]) for r in rows if r["amber_shelf"] > 0]
    assert 288 <= am[0][0] <= 293, f"amber_shelf mulai: {am[0]}"
    assert rows[360]["amber_shelf"] == 1.0, "amber_shelf harus 1.0 di f360"
    assert rows[599]["amber_shelf"] == 1.0, "amber_shelf harus 1.0 di f599"
    assert rows[1319]["amber_shelf"] == 1.0, "amber_shelf harus 1.0 di f1319"
    assert 0.0 < rows[1439]["amber_shelf"] < 1.0, \
        f"amber_shelf harus meredup di f1439: {rows[1439]['amber_shelf']}"
    assert all(r["amber_shelf"] == 0.0 for r in rows[:288]), \
        "amber_shelf harus 0 di S1-S2"
    # dawn_line: HANYA S1 (0-71) + S7 (1200-1319)
    dw = [r["f"] for r in rows if r["dawn_line"] > 0]
    assert dw == list(range(0, 72)) + list(range(1200, 1320)), \
        f"dawn_line harus hanya S1+S7, dapat {dw[:5]}...{dw[-5:]} ({len(dw)} frame)"
    # Kairo 001 TIDAK pernah meninggalkan rak amber (RX, -20) saat terlihat
    for r in rows:
        c = r["chars"]["KAI001"]
        if c["vis"]:
            assert abs(c["x"] - AMBER_X) < 0.01 and abs(c["y"] - AMBER_Y) < 0.01, \
                f"KAI001 di luar rak f{r['f']}: ({c['x']}, {c['y']})"
    # Kairo 001 tersembunyi S1-S2 (belum ditemukan), terlihat S4-S8
    assert all(not rows[f]["chars"]["KAI001"]["vis"] for f in range(0, 288)), \
        "KAI001 harus hidden di S1-S2"
    assert all(rows[f]["chars"]["KAI001"]["vis"] for f in range(600, 1440)), \
        "KAI001 harus terlihat di S4-S8"
    # EVA di gerbang S7 (y=21), Kairo 214 di rak S4-S8
    assert rows[1250]["chars"]["EVA"]["y"] == 21.0, "EVA harus di gerbang S7"
    assert rows[900]["chars"]["KAI"]["y"] == -18.4, "KAI harus di rak S5"
    print(f"CHECK OK: 0 flash, semua {len(rows)} baris punya "
          f"{len(ALL_CHARS)} karakter, 0 frame kosong")
    print(f"  gate_open=1: semua {len(gate)} frame | nexus=0 eye=0 warm=0 core=0 selalu")
    print(f"  scar_glow: semua frame | nexus_face: tidak pernah")
    print(f"  amber_shelf naik: {am[0][0]}-360 (1.0 sejak f360), meredup S8 -> "
          f"{rows[1439]['amber_shelf']} di f1439")
    print(f"  dawn_line: S1 (0-71) + S7 (1200-1319), {len(dw)} frame")
    print(f"  KAI001: hidden S1-S2, di rak (RX,-20) S3(360+)-S8")


if __name__ == "__main__":
    main()
