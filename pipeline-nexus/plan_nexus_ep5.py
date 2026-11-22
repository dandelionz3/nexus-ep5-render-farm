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


def cam(x, y, z, tx, ty, tz, focus, lens, roll=0.0, fstop=2.0):
    return {"x": round(x, 3), "y": round(y, 3), "z": round(z, 3),
            "tx": round(tx, 3), "ty": round(ty, 3), "tz": round(tz, 3),
            "focus": round(focus, 2), "lens": round(lens, 1),
            "roll": round(roll, 2), "fstop": round(fstop, 1)}


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
            # FIX 22 Nov (farm test run 44999774330): kamera lama di x=RX+3.5
            # = 83.5 berjalan MENURUNI kolom rak c=9 (rak x 81.6-84.0) — kamera
            # di DALAM kotak rak pada 68/216 frame S2 -> frame datar biru-abu.
            # Kamera kini di x=RX=80 (lorong tengah c=8 yang dikosongkan).
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
            chars_cam = cam(RX, eva_y - 7.0, 1.7, RX + 0.3, eva_y, 1.4,
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
            chars_cam = cam(RX, eva_y - 7.0, 1.7, RX + 0.3, eva_y, 1.4,
                            6.0, 50)
            li = lights(gate=400, rim=150, eva=300, fill=55)
        else:
            # 2c: EVA berhenti di antara rak yang padam; Kairo 214 di belakangnya
            # (kamera juga pindah ke lorong x=RX — lihat catatan FIX di 2a)
            chars["EVA"] = char(RX + 0.3, -6.0, 0, rot=180, lean=2, head_tilt=0,
                                armL=5, armR=5, legL=0, legR=0)
            chars["KAI"] = char(RX - 0.9, -3.0, 0, rot=180, lean=5, head_tilt=0,
                                armL=5, armR=5, legL=0, legR=0)
            chars_cam = cam(RX, -13.0, 1.7, RX + 0.3, -6.0, 1.4, 6.0, 50)
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
            # FIX 22 Nov: focus lama 5.0->2.4 vs jarak kamera-target 3.5->1.4 m
            # (seluruh frame lunak di f_0730); focus kini dihitung otomatis =
            # jarak kamera-target (lihat akhir loop). ECU 1.4 m + lens 85 +
            # f/2 punya DOF ~8 cm untuk kepala 0.55 m — jadi fstop 8.0 supaya
            # mata/bekas luka/uban pelipis sekaligus tajam.
            t = seg_t(f, 672, 767)
            chars["KAI"] = char(RX - 0.9, -18.3, 0, rot=0, lean=4, head_tilt=0,
                                armL=5, armR=5, legL=0, legR=0)
            chars["EVA"] = char(RX + 2.5, -16.0, 0, rot=180, lean=2, head_tilt=0,
                                armL=5, armR=5, legL=0, legR=0)
            chars["KAI001"] = kairo001_at_shelf()
            chars_cam = cam(lerp(RX + 0.3, RX + 0.15, smooth(t)), lerp(-16.5, -18.6, smooth(t)),
                            lerp(1.7, 1.62, smooth(t)),
                            RX, AMBER_Y, 1.5, lerp(5.0, 2.4, smooth(t)), lerp(65, 85, t),
                            fstop=8.0)
            li = lights(gate=400, rim=180, eva=350, fill=55)
        else:
            # 4c: ECU tahan, Kairo 001 menatap Kairo 214 (fstop 8.0 — sama spt 4b)
            chars["KAI"] = char(RX - 0.9, -18.3, 0, rot=0, lean=4, head_tilt=0,
                                armL=5, armR=5, legL=0, legR=0)
            chars["EVA"] = char(RX + 2.5, -16.0, 0, rot=180, lean=2, head_tilt=0,
                                armL=5, armR=5, legL=0, legR=0)
            chars["KAI001"] = kairo001_at_shelf()
            chars_cam = cam(RX + 0.15, -18.6, 1.62, RX, AMBER_Y, 1.5, 2.4, 85, fstop=8.0)
            li = lights(gate=400, rim=180, eva=350, fill=55)
    # ================= S5 MESIN MEMENANGKAN PERANG (864-1055) =================
    elif f < 1056:
        amber_shelf = 1.0
        # Two-shot Kairo 214 + Kairo 001 — dua wajah yang sama, 25 tahun
        # terpisah, dalam satu frame; cahaya amber + biru bekas luka.
        # FIX 22 Nov (farm test run 44999774330, f_0910): kamera lama di utara
        # (80.4, -15.9) terlalu dekat — Kairo 214 terpotong di tepi kanan.
        # Pull-back dari utara TIDAK BISA menunjukkan wajah Kairo 214: ia
        # menghadap SELATAN (rot=0, ke arah Kairo 001) sementara Kairo 001
        # menghadap UTARA (rot=180) — dari utara hanya terlihat punggung
        # kepala 214. Two-shot kini dari SISI TIMUR, lorong antar-baris
        # (x=83, y~-18.2, di antara baris rak r0/r1): kedua wajah terbaca
        # profil — 214 profil penuh, 001 tiga-perempat. Target = titik tengah
        # kedua kepala (79.45, -19.2, 1.45). Lens 30 (lebar) supaya rentang
        # sudut ~28 deg + lebar wajah muat di hFOV ~40 deg. Jarak pandang ke
        # kepala 001 melewati tiang rak amber dengan jarak bebas ~0.18 m.
        _S5_TGT = (79.45, -19.2, 1.45)
        if f < 936:
            # 5a: Kairo 001 bicara; Kairo 214 mendengarkan
            t = seg_t(f, 864, 935)
            chars["KAI"] = char(RX - 1.1, -18.4, 0, rot=0, lean=4, head_tilt=0,
                                armL=5, armR=5, legL=0, legR=0)
            chars["KAI001"] = kairo001_at_shelf()
            chars["EVA"] = char(RX + 2.5, -16.0, 0, rot=180, lean=2, head_tilt=0,
                                armL=5, armR=5, legL=0, legR=0)
            chars_cam = cam(lerp(83.4, 83.2, smooth(t)), lerp(-18.0, -18.15, smooth(t)), 1.7,
                            _S5_TGT[0], _S5_TGT[1], _S5_TGT[2], 4.5, 30)
            li = lights(gate=380, rim=200, eva=350, fill=55)
        elif f < 1008:
            # 5b: two-shot lanjut, Kairo 001 menatap lurus
            chars["KAI"] = char(RX - 1.1, -18.4, 0, rot=0, lean=4, head_tilt=0,
                                armL=5, armR=5, legL=0, legR=0)
            chars["KAI001"] = kairo001_at_shelf()
            chars["EVA"] = char(RX + 2.5, -16.0, 0, rot=180, lean=2, head_tilt=0,
                                armL=5, armR=5, legL=0, legR=0)
            chars_cam = cam(83.2, -18.15, 1.7,
                            _S5_TGT[0], _S5_TGT[1], _S5_TGT[2], 4.5, 30)
            li = lights(gate=380, rim=200, eva=350, fill=55)
        else:
            # 5c: two-shot tahan, Kairo 214 diam satu detik penuh
            chars["KAI"] = char(RX - 1.1, -18.4, 0, rot=0, lean=4, head_tilt=-2,
                                armL=5, armR=5, legL=0, legR=0)
            chars["KAI001"] = kairo001_at_shelf()
            chars["EVA"] = char(RX + 2.5, -16.0, 0, rot=180, lean=2, head_tilt=0,
                                armL=5, armR=5, legL=0, legR=0)
            chars_cam = cam(83.0, -18.3, 1.7,
                            _S5_TGT[0], _S5_TGT[1], _S5_TGT[2], 4.5, 30)
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
        # FIX 22 Nov (farm test f_1260): EVA siluet hitam total di depan
        # gerbang putih blown-out. GateLight 500->280 (gerbang jangan clipping),
        # fill 70->300 + rim BIRU 150->500 (RimRedCore di y=10 ada di sisi
        # kamera EVA — memberi cahaya depan/tepi biru) + eva 400->600, supaya
        # kulit silver-white + mata biru terbaca. Focus juga kini otomatis =
        # jarak kamera-target (7b: 7.0 -> 5.07 m).
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
            li = lights(gate=280, rim=500, eva=600, fill=300, dawn=150 * dawn_line)
        else:
            # 7b: tracking lanjut, gerbang membesar di belakang EVA
            chars["EVA"] = char(RX, 21.0, 0, rot=180, lean=2, head_tilt=0,
                                armL=5, armR=5, legL=0, legR=0)
            chars["KAI"] = char(RX - 1.1, -18.4, 0, rot=0, lean=4, head_tilt=0,
                                armL=5, armR=5, legL=0, legR=0)
            chars["KAI001"] = kairo001_at_shelf()
            chars_cam = cam(RX + 0.8, 16.5, 1.8, RX, 21.5, 1.6, 7.0, 50)
            li = lights(gate=280, rim=500, eva=600, fill=300, dawn=150 * dawn_line)
    # ================= S8 TWIST (1320-1439) =================
    else:
        # ECU Kairo 001 -> hitam. Amber meredup PELAN; end card f1380-1439 (ASS).
        amber_shelf = lerp(1.0, 0.1, smooth(seg_t(f, 1320, 1439)))
        if f < 1380:
            # 8a: ECU Kairo 001, hook terakhir hampir berbisik (fstop 8.0 — ECU
            # yang sama dengan S4 4b/4c; focus otomatis = jarak kamera-target)
            chars["KAI001"] = kairo001_at_shelf()
            chars["KAI"] = char(RX - 1.1, -18.4, 0, rot=0, lean=4, head_tilt=-2,
                                armL=5, armR=5, legL=0, legR=0)
            chars["EVA"] = char(RX, 21.0, 0, rot=180, lean=2, head_tilt=0,
                                armL=5, armR=5, legL=0, legR=0)
            chars_cam = cam(RX + 0.15, -18.6, 1.62, RX, AMBER_Y, 1.5, 2.4, 85, fstop=8.0)
            li = lights(gate=300, rim=180, eva=300, fill=55)
        else:
            # 8b: ECU lanjut -> hitam + end card (f1380-1439, ASS)
            chars["KAI001"] = kairo001_at_shelf()
            chars["KAI"] = char(RX - 1.1, -18.4, 0, rot=0, lean=4, head_tilt=-2,
                                armL=5, armR=5, legL=0, legR=0)
            chars["EVA"] = char(RX, 21.0, 0, rot=180, lean=2, head_tilt=0,
                                armL=5, armR=5, legL=0, legR=0)
            chars_cam = cam(RX + 0.15, -18.6, 1.62, RX, AMBER_Y, 1.5,
                            lerp(2.4, 2.6, smooth(seg_t(f, 1380, 1439))), 85, fstop=8.0)
            # meredup menuju hitam (end card di atas hitam)
            dim = 1.0 - 0.92 * smooth(seg_t(f, 1400, 1439))
            li = lights(gate=300 * dim, rim=180 * dim, eva=300 * dim,
                        fill=55 * dim)

    # FIX 22 Nov: focus OTOMATIS = jarak kamera-target di SEMUA frame.
    # Nilai focus tulis-tangan lama menyimpang sampai ~1.3 m (S4: 3.41 vs 2.08
    # di f730; S7 7b: 7.0 vs 5.07; S3: 18 vs 26 di f288) -> frame lunak.
    # Override di sini supaya tidak ada lagi angka focus yang bisa basi saat
    # kamera digeser. (Nilai focus di cam(...) di atas kini hanya placeholder.)
    _dx = chars_cam["tx"] - chars_cam["x"]
    _dy = chars_cam["ty"] - chars_cam["y"]
    _dz = chars_cam["tz"] - chars_cam["z"]
    chars_cam["focus"] = round(math.sqrt(_dx * _dx + _dy * _dy + _dz * _dz), 2)

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
    # FIX 22 Nov — self-check kamera vs geometri set (pelajaran farm test
    # run 44999774330: S2 kamera di DALAM rak 68 frame tanpa ketahuan plan).
    # Kotak-kotak disalin dari build_scene_nexus_ep5.py: 212 rak gelap
    # (grid 17x13 minus lorong c=8 r1-12 minus amber c8 r0 + baris y=19),
    # rangka rak amber, 12 kolom. Kamera TIDAK BOLEH berada di dalam kotak
    # apa pun di segmen mana pun.
    def _boxes():
        bx = []
        for _r in range(13):
            for _c in range(17):
                if _c == 8 and 1 <= _r <= 12:
                    continue
                if _c == 8 and _r == 0:
                    continue
                bx.append((f"SH_c{_c}r{_r}", RX - 22.4 + _c * 2.8, -20.0 + _r * 3.0, 2.5,
                           1.2, 0.5, 2.5))
        for _c in (0, 1, 15, 16):
            bx.append((f"SH_extra_c{_c}", RX - 22.4 + _c * 2.8, 19.0, 2.5, 1.2, 0.5, 2.5))
        bx += [("AMBER_Back", AMBER_X, AMBER_Y - 0.45, 2.5, 1.2, 0.075, 2.5),
               ("AMBER_PostL", AMBER_X - 1.12, AMBER_Y, 2.5, 0.075, 0.5, 2.5),
               ("AMBER_PostR", AMBER_X + 1.12, AMBER_Y, 2.5, 0.075, 0.5, 2.5),
               ("AMBER_Top", AMBER_X, AMBER_Y, 4.95, 1.2, 0.5, 0.075),
               ("AMBER_Base", AMBER_X, AMBER_Y, 0.08, 1.2, 0.5, 0.075)]
        for _i, (_ccx, _ccy) in enumerate(((-20, -12), (-20, 12), (20, -12), (20, 12),
                                           (-10, -6), (-10, 6), (10, -6), (10, 6),
                                           (-5, 15), (5, 15), (-5, -18), (5, -18))):
            bx.append((f"COL{_i}", RX + _ccx, _ccy, 7.0, 0.6, 0.6, 7.0))
        return bx
    _all_boxes = _boxes()
    assert len([b for b in _all_boxes if b[0].startswith("SH_")]) == 212, \
        f"rak gelap di check: {len([b for b in _all_boxes if b[0].startswith('SH_')])} (harus 212)"
    _inside = []
    for _r in rows:
        _cm = _r["cam"]
        for (_nm, _bx, _by, _bz, _hx, _hy, _hz) in _all_boxes:
            if (abs(_cm["x"] - _bx) < _hx and abs(_cm["y"] - _by) < _hy
                    and abs(_cm["z"] - _bz) < _hz):
                _inside.append((_r["f"], _nm, _cm["x"], _cm["y"], _cm["z"]))
    assert not _inside, f"kamera DI DALAM kotak set: {_inside[:10]} ({len(_inside)} frame)"
    # focus = jarak kamera-target di semua frame (toleransi pembulatan 0.06)
    _foc_err = []
    for _r in rows:
        _cm = _r["cam"]
        _d = math.sqrt((_cm["tx"] - _cm["x"]) ** 2 + (_cm["ty"] - _cm["y"]) ** 2
                       + (_cm["tz"] - _cm["z"]) ** 2)
        if abs(_cm["focus"] - _d) > 0.06:
            _foc_err.append((_r["f"], _cm["focus"], round(_d, 2)))
    assert not _foc_err, f"focus != jarak kamera-target: {_foc_err[:10]}"
    # S2: kamera harus di lorong x=80 di semua frame S2
    assert all(rows[_f]["cam"]["x"] == 80.0 for _f in range(72, 288)), \
        "kamera S2 harus x=80 (lorong c=8)"
    # S5: kamera two-shot dari sisi timur (x 83.0-83.4), lens lebar 30
    assert all(83.0 <= rows[_f]["cam"]["x"] <= 83.4 for _f in range(864, 1056)), \
        "kamera S5 harus di sisi timur x=83.0-83.4"
    assert all(rows[_f]["cam"]["lens"] == 30.0 for _f in range(864, 1056)), \
        "lens S5 harus 30"
    # S5: garis pandang kamera -> kedua kepala TIDAK BOLEH menembus tiang rak
    # amber (slab test segmen-AABB terhadap AMBER_PostL/R).
    def _seg_hits_box(p0, p1, box):
        _nm, _bx, _by, _bz, _hx, _hy, _hz = box
        _tmin, _tmax = 0.0, 1.0
        for _p, _q, _c, _h in ((p0[0], p1[0], _bx, _hx), (p0[1], p1[1], _by, _hy),
                               (p0[2], p1[2], _bz, _hz)):
            _d = _q - _p
            if abs(_d) < 1e-9:
                if abs(_p - _c) >= _h:
                    return False
            else:
                _t1 = (_c - _h - _p) / _d
                _t2 = (_c + _h - _p) / _d
                _tmin = max(_tmin, min(_t1, _t2))
                _tmax = min(_tmax, max(_t1, _t2))
                if _tmin > _tmax:
                    return False
        return True
    _posts = [b for b in _all_boxes if b[0] in ("AMBER_PostL", "AMBER_PostR")]
    _blocked = []
    for _f in range(864, 1056):
        _cm = rows[_f]["cam"]
        _p0 = (_cm["x"], _cm["y"], _cm["z"])
        for _head in ((78.9, -18.4, 1.45), (80.0, -20.0, 1.45)):  # KAI, KAI001
            for _pb in _posts:
                if _seg_hits_box(_p0, _head, _pb):
                    _blocked.append((_f, _pb[0], _head))
    assert not _blocked, f"garis pandang S5 terhalang tiang amber: {_blocked[:10]}"
    # S7: gate diredup + fill/rim depan dinaikkan
    assert all(rows[_f]["lights"]["gate"] == 280.0 for _f in range(1200, 1320)), \
        "gate S7 harus 280"
    assert all(rows[_f]["lights"]["fill"] == 300.0 for _f in range(1200, 1320)), \
        "fill S7 harus 300"
    assert all(rows[_f]["lights"]["rim"] == 500.0 for _f in range(1200, 1320)), \
        "rim S7 harus 500"
    # S4 4b/4c + S8: ECU fstop 8.0
    assert all(rows[_f]["cam"]["fstop"] == 8.0 for _f in list(range(672, 864)) + list(range(1320, 1440))), \
        "fstop ECU S4 4b/4c + S8 harus 8.0"
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
    print(f"  FIX 22 Nov: kamera DI DALAM kotak set: 0 frame (cek {len(_all_boxes)} kotak "
          f"di semua {len(rows)} frame)")
    print(f"  FIX 22 Nov: focus = jarak kamera-target semua frame "
          f"(S4 f730: {rows[730]['cam']['focus']}, S7 f1260: {rows[1260]['cam']['focus']})")
    print(f"  FIX 22 Nov: S2 kamera x=80 semua frame | S5 kamera timur "
          f"x={rows[900]['cam']['x']} lens 30, garis pandang ke 2 kepala bersih | "
          f"S7 gate 280 fill 300 rim 500 | ECU S4/S8 fstop 8.0")


if __name__ == "__main__":
    main()
