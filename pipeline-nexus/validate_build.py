# Validasi build_scene Ep 5 TANPA render (hemat RAM): exec sumber build
# sampai sebelum still-render, lalu cek objek kunci ada di koordinat benar.
#   blender -b --factory-startup -P validate_build.py -- <dummy.png>
# Cek: aula memori GELAP (60x48, dinding 16, TIDAK ADA wajah NEXUS — panel
# halo 18x13 MATI tanpa emissive/partikel, gerbang 5x6 TERBUKA PENUH sejak S1,
# 13 panel dinding belakang statis), 213 rak arsip (212 GELAP instans + 1
# AMBER di ujung terjauh (RX,-20), slot amber padam di awal), Kairo 001
# (aged grade: uban di pelipis + bekas luka SAMA + scar glow), scar glow
# Kairo 6.0, TIDAK ADA merah (rim/nexus biru, lampu nexus = 0, amber hanya
# #E8A33D), TIDAK ADA Sentinel, TIDAK ADA 213 Kairo, TIDAK ADA kota fajar,
# TIDAK ADA backpack/data core, TIDAK ADA laser, TIDAK ADA teks 3D judul.
# Headless (tanpa Blender): python3 validate_headless.py
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.argv = [sys.argv[0], "--", "/tmp/nx5_validate.png", "--res", "540", "960"]
src = open(os.path.join(HERE, "build_scene_nexus_ep5.py"),
           encoding="utf-8").read().split("scene.render.filepath = OUT")[0]
exec(src)

objs = bpy.data.objects
print("OBJECTS:", len(objs))
for name in ["NX_Gate", "NX_GateFrameL", "NX_GateFrameR", "NX_GateFrameT",
             "NX_WallPanel00", "NX_WallPanel05", "NX_WallPanel06",
             "NX_WallPanel11", "NX_WallPanelTop", "NX_WallL", "NX_WallR",
             "NX_HaloPanel", "NX_Col11",
             "KAI_Scar", "KAI_ScarGlow", "KAI001_Scar", "KAI001_ScarGlow",
             "KAI001_GreyTempleL", "KAI001_GreyTempleR",
             "EvaRimCore", "AmberLight", "DawnLight", "NexusLight", "RimRedCore",
             "SH_AmberBack", "SH_AmberPostL", "SH_AmberPostR",
             "SH_AmberTop", "SH_AmberBase", "SH_AmberSlot",
             "SH_000", "SH_105", "SH_211"]:
    o = objs.get(name)
    print(("OK  " if o is not None else "MISS"), name,
          tuple(round(v, 2) for v in o.location) if o else "")
    assert o is not None, name

# --- TIDAK BOLEH ADA (Ep 5: wajah hilang, kota hilang, Sentinel hilang,
# 213 Kairo hilang, backpack/core hilang, laser hilang, merah hilang) ---
for _gone in ["NX_FaceGlow", "NX_FaceHead", "NX_EyeL", "NX_EyeR",
              "NX_BrowL", "NX_Mouth", "NX_Scan0", "NX_Dot0", "NX_DotF0",
              "CT_Ground", "CT_Bldg0", "CT_Bldg11",
              "CT_Screen1", "CT_Screen2", "CT_LampHead0", "CT_LampHead3",
              "K213_000", "K213_106", "K213_212",
              "SEN1", "SEN1_Torso", "SEN1_Head", "SEN8",
              "RES1", "RES2", "CIV1", "CIV2",
              "KAI_Backpack", "KAI_BackpackDropped", "CoreCube", "CoreSocketed",
              "NX_SocketBase", "NX_SocketTop", "NX_SocketSlot",
              "EvaLaser1", "EvaLaser2", "KaiLaser1", "KaiLaser2",
              "HallLight1", "HallLight2", "HallFill", "HallRedFlicker",
              "EvaRimHall", "MH_Floor", "MH_Ceil", "MH_WallBack", "MH_Col0",
              "NX_FaceSmall_Glow", "NX_FaceSmall_EyeL",
              "EyeGlow", "CoreLight", "WarmLight"]:
    assert objs.get(_gone) is None, f"{_gone} HARUS TIDAK ADA di Ep 5"
    print("GONE OK", _gone)
for _prefix in ("K213_", "SEN", "CT_", "KF_"):
    _bad = [o for o in objs if o.name.startswith(_prefix)]
    assert not _bad, f"objek {_prefix}* HARUS TIDAK ADA di Ep 5: {[o.name for o in _bad[:3]]}"
    print("GONE PREFIX OK", _prefix)
assert NX_FACE_SMALL_OBJS == [], "NX_FACE_SMALL_OBJS harus kosong di Ep 5"
assert sorted(CHARS.keys()) == ["EVA", "KAI", "KAI001"], \
    f"karakter harus KAI+EVA+KAI001, dapat {sorted(CHARS.keys())}"

# --- koordinat kunci ---
assert tuple(round(v, 2) for v in objs["NX_Gate"].scale) == (1.0, 1.0, 1.0), "gerbang harus skala penuh (terbuka)"
assert objs["NX_Gate"].hide_render is False, "gerbang TIDAK boleh hidden (terbuka sejak S1)"
# gerbang 5x6 m: plane scale (5,6) di lokasi (RX, 23.55, 3.0)
assert abs(objs["NX_Gate"].location.x - 80.0) < 0.01
assert abs(objs["NX_Gate"].location.y - 23.55) < 0.01
assert abs(objs["NX_Gate"].location.z - 3.0) < 0.01
# panel dinding belakang: panel 00 di (52.5, 23.8, 8.0), panel atas di (80, 23.8, 11.0)
assert abs(objs["NX_WallPanel00"].location.x - 52.5) < 0.01
assert abs(objs["NX_WallPanel00"].location.y - 23.8) < 0.01
assert abs(objs["NX_WallPanel00"].location.z - 8.0) < 0.01
assert abs(objs["NX_WallPanelTop"].location.x - 80.0) < 0.01
assert abs(objs["NX_WallPanelTop"].location.z - 11.0) < 0.01
# lantai aula memori 60x48 (block() meng-apply scale -> cek dimensions)
assert tuple(round(v, 2) for v in objs["NX_Floor"].dimensions) == (60.0, 48.0, 0.2)
# panel halo MATI di langit-langit (80, 0, 14.0), 18x13 m
assert abs(objs["NX_HaloPanel"].location.x - 80.0) < 0.01
assert abs(objs["NX_HaloPanel"].location.y - 0.0) < 0.01
assert abs(objs["NX_HaloPanel"].location.z - 14.0) < 0.01
assert tuple(round(v, 2) for v in objs["NX_HaloPanel"].dimensions) == (18.0, 13.0, 0.0), \
    f"halo panel harus 18x13, dapat {tuple(round(v, 2) for v in objs['NX_HaloPanel'].dimensions)}"
_halo_bsdf = bpy.data.materials["HaloDead"].node_tree.nodes["Principled BSDF"]
assert abs(_halo_bsdf.inputs["Emission Strength"].default_value) < 0.01, \
    "panel halo harus MATI (emissive 0)"
# rak amber di ujung terjauh (RX, -20): slot di (80, -19.47, 4.2)
assert abs(objs["SH_AmberSlot"].location.x - 80.0) < 0.01
assert abs(objs["SH_AmberSlot"].location.y - (-19.47)) < 0.01
assert abs(objs["SH_AmberSlot"].location.z - 4.2) < 0.01
assert abs(objs["SH_AmberBack"].location.y - (-20.45)) < 0.01
# scar glow Kairo + Kairo 001: emisi 6.0 (TERANG sejak frame 0, lanjutan Ep 3 S6)
_sg = bpy.data.materials["ScarGlowM"].node_tree.nodes["Principled BSDF"]
assert abs(_sg.inputs["Emission Strength"].default_value - 6.0) < 0.01, "ScarGlowM harus 6.0"
# 212 rak gelap (instans SH_000..SH_211) + 1 rak amber = 213 rak
shelves = [o for o in objs if o.name.startswith("SH_") and o.name[3:6].isdigit()
           and len(o.name) == 6]
assert len(shelves) == 212, f"rak gelap: {len(shelves)} (harus 212)"
assert len(SHELF_BASE) == 212, f"SHELF_BASE: {len(SHELF_BASE)} (harus 212)"
# grid rak: 16 kolom x RX-22.4..RX+22.4 (kolom tengah x=RX adalah lorong
# terbuka — tidak ada rak gelap di sana; rak amber berdiri di ujungnya);
# baris y -20..16 + baris ekstra 19
_xs = sorted({round(o.location.x, 1) for o in shelves})
_ys = sorted({round(o.location.y, 1) for o in shelves})
assert len(_xs) == 16 and _xs[0] == 57.6 and _xs[-1] == 102.4, f"kolom x: {_xs}"
assert 80.0 not in _xs, "kolom x=RX harus kosong (lorong tengah)"
assert len(_ys) == 14 and _ys[0] == -20.0 and _ys[-1] == 19.0, f"baris y: {_ys}"
# lorong tengah (x=RX) TERBUKA untuk y >= -17 (rak amber satu-satunya di x=RX)
_aisle = [o for o in shelves if abs(o.location.x - 80.0) < 0.01]
assert _aisle == [], f"lorong tengah harus kosong (rak gelap): {[o.name for o in _aisle]}"
# slot amber padam di awal (di-key 0 -> 4 di animate dari amber_shelf S3)
_am = bpy.data.materials["AmberShelfM"].node_tree.nodes["Principled BSDF"]
assert abs(_am.inputs["Emission Strength"].default_value) < 0.01, \
    "AmberShelfM harus 0 di awal"
assert abs(_am.inputs["Emission Color"].default_value[0] - 1.0) < 0.01
assert abs(_am.inputs["Emission Color"].default_value[1] - 0.64) < 0.01
assert abs(_am.inputs["Emission Color"].default_value[2] - 0.24) < 0.01, \
    "amber harus #E8A33D (1.0, 0.64, 0.24)"
# lampu amber + fajar + nexus = 0 di awal (di-key di animate)
assert abs(objs["AmberLight"].data.energy) < 0.01, "AmberLight harus 0 di awal"
assert abs(objs["DawnLight"].data.energy) < 0.01, "DawnLight harus 0 di awal"
assert abs(objs["NexusLight"].data.energy) < 0.01, "NexusLight harus 0 (wajah hilang)"
# TIDAK ADA merah: TIDAK ADA material bernama *Red* / *Nexus*; rim/nexus BIRU
for _m in bpy.data.materials:
    _mn = _m.name if hasattr(_m, "name") else _m
    assert "red" not in _mn.lower() and "nexus" not in _mn.lower(), \
        f"material merah/NEXUS tidak boleh ada: {_mn}"
for _ln in ("RimRedCore", "NexusLight"):
    _c = tuple(round(v, 2) for v in objs[_ln].data.color)
    assert _c == (0.30, 0.65, 1.0), f"{_ln} harus biru, dapat {_c}"
_ac = tuple(round(v, 2) for v in objs["AmberLight"].data.color)
assert _ac == (1.0, 0.64, 0.24), f"AmberLight harus amber, dapat {_ac}"
# TIDAK ADA teks 3D judul
assert not [o for o in objs if o.type == "FONT"], "teks 3D judul TIDAK boleh ada (judul hanya ASS)"
print("CHARS:", sorted(CHARS.keys()))
print("SHELF rows:", len(_ys), "cols:", len(_xs), "| SHELF_BASE:", len(SHELF_BASE))
print("GATE scale:", tuple(objs["NX_Gate"].scale),
      "| gate hidden:", objs["NX_Gate"].hide_render)
print("WALL PANELS:", len([o for o in objs if o.name.startswith("NX_WallPanel")]))
print("COLUMNS:", len([o for o in objs if o.name.startswith("NX_Col") and o.name[6:].isdigit()]))
print("VALIDATE_BUILD_OK")
