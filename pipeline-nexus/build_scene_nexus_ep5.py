# build_scene_nexus_ep5.py — NEXUS ZERO Episode 5 "THE EMPTY HALL" (vinyl-toy stylized).
# Copy build_scene_nexus_ep4.py, adaptasi Ep 5 (bukan dari nol).
# SATU set: aula memori GELAP (RX=80, 60x48 m, dinding 16 m, lantai
# reflektif, 12 kolom circuitry GELAP, gerbang putih 5x6 m TERBUKA PENUH
# sejak S1 — gate_open=1 konstan, langit-langit KOSONG — panel halo 18x13 m
# tetap ada sebagai geometri tapi MATI, tanpa emissive, tanpa partikel).
# 213 rak arsip: 212 GELAP (slot lampu padam) + 1 AMBER di ujung terjauh
# (RX, -20) — satu-satunya cahaya hangat; amber HANYA di rak itu + rim
# Kairo 001 (GATE_M 0.9 supaya amber tidak blown-out).
# TIDAK ADA: wajah NEXUS (dalam bentuk apa pun), merah (satu frame pun),
# Sentinel (0), 213 Kairo sebelumnya (0), set kota fajar (hanya garis fajar
# tipis lewat gerbang S1/S7), backpack + data core (tetap di ruang inti,
# TIDAK muncul di Ep 5), dinding runtuh, teks 3D judul (judul hanya ASS).
# 3 karakter lock DESIGN-v1.md: KAIRO 214 (1.8 m, bekas luka alis kiri WAJIB,
# kilau biru TERANG), KAIRO 001 (model Kairo YANG SAMA + aged grade: uban di
# pelipis, kulit lelah, bekas luka SAMA — TIDAK pernah meninggalkan raknya),
# EVA (silver-white, mata biru, penjaga gerbang S7).
# Render setup B7: Eevee, samples env FS_SAMPLES default 6, ray OFF, volumetrics
# tile 16, DOF ON, motion blur ON, subsurf 1, bevel 0, AgX. World strength 0.45,
# kabut 0.02 aula.
# Run:
#   blender -b --factory-startup -P build_scene_nexus_ep5.py -- <out.png> [--res 540 960]
import bpy
import math
import os
import random as _random2
import sys
from mathutils import Vector

argv = sys.argv
args = argv[argv.index("--") + 1:] if "--" in argv else []
OUT = args[0] if args else "//nexus_ep5_preview.png"
RES_X, RES_Y = (540, 960)
if "--res" in args:
    i = args.index("--res")
    RES_X, RES_Y = int(args[i + 1]), int(args[i + 2])

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# ---------- render setup B7 ----------
scene.render.engine = "BLENDER_EEVEE_NEXT"
scene.render.resolution_x = RES_X
scene.render.resolution_y = RES_Y
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.view_settings.view_transform = "AgX"
scene.view_settings.look = "None"


def _set(obj, attr, value):
    if hasattr(obj, attr):
        setattr(obj, attr, value)


_set(scene.eevee, "use_raytracing", os.environ.get("FS_RAY", "0") == "1")
_set(scene.eevee, "use_shadows", True)
_set(scene.eevee, "volumetric_tile_size", os.environ.get("FS_VOLTILE", "16"))
_set(scene.eevee, "volumetric_end", 60.0)
scene.eevee.taa_render_samples = int(os.environ.get("FS_SAMPLES", "6"))
scene.render.use_motion_blur = os.environ.get("FS_MB", "1") == "1"
_set(scene.render, "motion_blur_shutter", 0.5)

world = bpy.data.worlds.new("World")
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs["Color"].default_value = (0.055, 0.059, 0.067, 1.0)  # langit malam #0E0F11
bg.inputs["Strength"].default_value = 0.45  # aula GELAP, bukan abu-abu terang


# ---------- materials ----------
def mat(name, rgb, rough=0.45, metal=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1.0)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    return m


def emissive(name, rgb, strength):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1.0)
    b.inputs["Emission Color"].default_value = (*rgb, 1.0)
    b.inputs["Emission Strength"].default_value = strength
    return m


# --- Kairo 214 ---
SKIN_KAI = mat("SkinKairo", (0.79, 0.63, 0.51), 0.5)          # #C9A186
HAIR_KAI = mat("HairKairo", (0.05, 0.05, 0.06), 0.6)
JACKET = mat("JacketKairo", (0.12, 0.13, 0.15), 0.6)          # #1E2126
JACKET2 = mat("JacketRes1", (0.16, 0.14, 0.12), 0.6)
JACKET3 = mat("JacketRes2", (0.10, 0.13, 0.16), 0.6)
SHIRT = mat("ShirtKairo", (0.16, 0.16, 0.18), 0.6)
PANTS_K = mat("PantsKairo", (0.08, 0.09, 0.10), 0.6)          # #14161A
BOOTS = mat("BootsKairo", (0.16, 0.13, 0.09), 0.55)           # #2A2118
EYE_DARK = mat("EyeDark", (0.05, 0.03, 0.02), 0.2)            # mata cokelat gelap Kairo
# --- Kairo 001 (aged grade dari model yang SAMA — BUKAN cetakan baru) ---
SKIN_KAI001 = mat("SkinKairo001", (0.72, 0.57, 0.46), 0.55)   # kulit lebih lelah / kusam
JACKET_AGED = mat("JacketKairo001", (0.10, 0.11, 0.12), 0.65)  # jaket sama, lebih usang
GREY_HAIR = mat("GreyHair", (0.55, 0.55, 0.57), 0.6)          # uban di pelipis
# --- EVA ---
SKIN_EVA = mat("SkinEva", (0.85, 0.87, 0.89), 0.25, metal=0.6)  # silver-white #D8DDE3
SUIT_EVA = mat("SuitEva", (0.88, 0.89, 0.91), 0.3, metal=0.4)
EYE_BLUE = emissive("EyeBlue", (0.30, 0.65, 1.0), 1.2)       # #4DA6FF — satu-satunya biru
CIRCUIT_BLUE = emissive("CircuitBlue", (0.30, 0.65, 1.0), 0.5)
# --- Sentinel (TIDAK dipakai di Ep 5 — material disimpan supaya make_character
# tetap utuh; TIDAK ADA objek Sentinel yang dibuat) ---
METAL_SEN = mat("MetalSentinel", (0.05, 0.06, 0.06), 0.35, metal=0.9)
METAL_SEN2 = mat("MetalSentinel2", (0.10, 0.11, 0.12), 0.3, metal=0.9)
SENSOR_OFF = mat("SensorOff", (0.08, 0.02, 0.02), 0.3)
# --- set ---
GROUND = mat("Ground", (0.090, 0.094, 0.102), 0.9)
WET_GROUND = mat("WetGround", (0.05, 0.06, 0.08), 0.15)      # lantai reflektif aula
WALL = mat("Wall", (0.141, 0.149, 0.165), 0.85)
# Ep 5: gerbang cahaya putih — GATE_M 0.9 (pelajaran Ep 1/2/3/4: 1.5 blown-out).
GATE_M = emissive("GateLight", (1.0, 1.0, 0.95), 0.9)
# panel halo langit-langit: geometri MATI — gelap, TANPA emissive, TANPA partikel.
HALO_DEAD_M = mat("HaloDead", (0.05, 0.05, 0.06), 0.9)
# rak arsip gelap: kotak gelap + slot lampu PADAM (emissive 0 penuh).
SHELF_M = mat("ShelfDark", (0.10, 0.11, 0.13), 0.8)
SHELF_SLOT_OFF = mat("ShelfSlotOff", (0.06, 0.06, 0.07), 0.5)
# rak amber: slot menyala #E8A33D — emisi di-key 0 -> 4 di animate dari
# amber_shelf (S3 naik, S4-S6/S8 bertahan, S8 meredup). Amber HANYA di rak
# ini + rim Kairo 001 — jangan bocorkan ke rak lain atau gerbang.
AMBER_SHELF_M = emissive("AmberShelfM", (1.0, 0.64, 0.24), 0.0)


def smooth(o):
    bpy.context.view_layer.objects.active = o
    o.select_set(True)
    bpy.ops.object.shade_smooth()
    o.select_set(False)


def block(name, loc, size, m, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(m)
    smooth(o)
    return o


def ball(name, loc, size, m):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=loc, segments=32, ring_count=16)
    o = bpy.context.object
    o.name = name
    o.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(m)
    smooth(o)
    return o


def cylinder(name, loc, radius, depth, m, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, location=loc, rotation=rot, vertices=32)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(m)
    smooth(o)
    return o


def dot(name, loc, size, m):
    """Titik partikel hemat: icosphere subdiv 1 (bukan UV sphere 32x16)."""
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = (size, size, size)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(m)
    smooth(o)
    return o


def plane(name, loc, size, m, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_plane_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.scale = (size[0], size[1], 1.0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(m)
    return o


# ---------- SET: aula memori (RX=80, 60x48 m, dinding 16 m) ----------
RX = 80.0
block("NX_Floor", (RX, 0, -0.1), (60, 48, 0.2), WET_GROUND)  # lantai reflektif 60x48 m
# Dinding belakang = PANEL STATIS (bukan dinding padat, bukan runtuh — Ep 5
# tidak ada runtuh): 12 panel samping + 1 panel atas; celah gerbang
# 5x6 m (x RX-2.5..RX+2.5, z 0..6) tetap terbuka di bawahnya.
for _i in range(5):
    block(f"NX_WallPanel{_i:02d}", (RX - 27.5 + _i * 5.0, 23.8, 8.0), (5.0, 0.4, 16.0), WALL)
    block(f"NX_WallPanel{_i + 7:02d}", (RX + 7.5 + _i * 5.0, 23.8, 8.0), (5.0, 0.4, 16.0), WALL)
block("NX_WallPanel05", (RX - 3.9, 23.8, 8.0), (2.2, 0.4, 16.0), WALL)
block("NX_WallPanel06", (RX + 3.9, 23.8, 8.0), (2.2, 0.4, 16.0), WALL)
block("NX_WallPanelTop", (RX, 23.8, 11.0), (5.6, 0.4, 10.0), WALL)
block("NX_WallL", (RX - 29.8, 0, 8.0), (0.4, 48, 16.0), WALL)
block("NX_WallR", (RX + 29.8, 0, 8.0), (0.4, 48, 16.0), WALL)
block("NX_WallFront", (RX, -23.8, 8.0), (60, 0.4, 16.0), WALL)
# Ep 5: TIDAK ADA wajah NEXUS — langit-langit KOSONG. Panel halo 18x13 m
# tetap ada sebagai GEOMETRI (menghadap ke bawah, z=14.0) tapi MATI:
# material gelap tanpa emissive, tanpa partikel wajah.
_halo = plane("NX_HaloPanel", (RX, 0, 14.0), (18.0, 13.0), HALO_DEAD_M,
              rot=(math.radians(180), 0, 0))
# partikel digital melayang di ruangan (BIRU — debu cahaya bekas luka;
# BUKAN partikel wajah — wajah tidak punya partikel di Ep 5).
_random2.seed(214)
for i in range(40):
    px = RX + _random2.uniform(-25, 25)
    py = _random2.uniform(-20, 20)
    pz = _random2.uniform(0.5, 14.0)
    _s = _random2.uniform(0.04, 0.10)
    ball(f"NX_Float{i}", (px, py, pz), (_s, _s, _s), CIRCUIT_BLUE)
# kolom circuitry GELAP (tidak menyala — merah hilang total di Ep 5;
# strip kolom memakai WALL gelap, bukan emissive).
for i, (ccx, ccy) in enumerate(((-20, -12), (-20, 12), (20, -12), (20, 12),
                                (-10, -6), (-10, 6), (10, -6), (10, 6),
                                (-5, 15), (5, 15), (-5, -18), (5, -18))):
    block(f"NX_Col{i}", (RX + ccx, ccy, 7.0), (1.2, 1.2, 14.0), WALL)
    block(f"NX_ColLight{i}", (RX + ccx, ccy - 0.65 if ccy < 0 else ccy + 0.65, 7.0),
          (0.15, 0.15, 13.6), WALL)
    for _k in range(3):
        block(f"NX_ColStrip{i}_{_k}", (RX + ccx, ccy, 2.4 + _k * 4.0),
              (1.25, 1.25, 0.12), WALL)
# gerbang cahaya putih di dinding belakang bawah (di bawah langit-langit kosong)
# Ep 5: gerbang TERBUKA PENUH sejak S1 (gate_open=1 konstan, skala X di-key di animate)
_gate_plane = plane("NX_Gate", (RX, 23.55, 3.0), (5.0, 6.0), GATE_M, rot=(math.radians(90), 0, 0))  # gerbang 5x6 m
_gate_plane.hide_render = False
block("NX_GateFrameL", (RX - 2.6, 23.5, 3.0), (0.4, 0.5, 6.0), WALL)
block("NX_GateFrameR", (RX + 2.6, 23.5, 3.0), (0.4, 0.5, 6.0), WALL)
block("NX_GateFrameT", (RX, 23.5, 6.1), (5.6, 0.5, 0.4), WALL)

# ---------- 213 rak arsip: 212 GELAP + 1 AMBER (ujung terjauh) ----------
# Grid 17 kolom (x RX-22.4..RX+22.4 step 2.8) x 13 baris (y -20..16 step 3.0)
# = 221 slot. Lorong tengah (kolom c=8, x=RX) DIBUKA untuk r=1..12 supaya
# EVA/Kairo bisa berjalan menyusuri aula sampai ke rak amber; rak amber
# berdiri di ujung lorong (c=8, r=0) = (RX, -20). Baris ekstra r=13 (y=19)
# 4 rak di sisi gerbang (c=0,1,15,16). Total gelap: 221-12-1+4 = 212.
# Rak = geometri sederhana (kotak tinggi + slot lampu kecil), instancing
# satu model rak yang sama; 212 rak MATI (slot emissive 0 penuh).
SHELF_COLL = bpy.data.collections.new("ShelfDark")
bpy.context.scene.collection.children.link(SHELF_COLL)
_SH = []
_SH.append(block("SH_Box", (0, 0, 2.5), (2.4, 1.0, 5.0), SHELF_M))
_SH.append(block("SH_Slot", (0, -0.53, 4.2), (0.35, 0.06, 0.18), SHELF_SLOT_OFF))
for _o in _SH:
    bpy.context.scene.collection.objects.unlink(_o)
    SHELF_COLL.objects.link(_o)
SHELF_BASE = {}
_shelf_positions = []
for _r in range(13):
    for _c in range(17):
        if _c == 8 and 1 <= _r <= 12:
            continue  # lorong tengah terbuka
        if _c == 8 and _r == 0:
            continue  # rak amber (dibangun terpisah di bawah)
        _shelf_positions.append((RX - 22.4 + _c * 2.8, -20.0 + _r * 3.0))
for _c in (0, 1, 15, 16):  # baris ekstra y=19, mengapit gerbang
    _shelf_positions.append((RX - 22.4 + _c * 2.8, 19.0))
for _idx, (_sx, _sy) in enumerate(_shelf_positions):
    _e = bpy.data.objects.new(f"SH_{_idx:03d}", None)
    bpy.context.scene.collection.objects.link(_e)
    _e.instance_type = "COLLECTION"
    _e.instance_collection = SHELF_COLL
    _e.location = (_sx, _sy, 0.0)
    SHELF_BASE[_e.name] = (_sx, _sy, 0.0)
assert len(SHELF_BASE) == 212, f"rak gelap: {len(SHELF_BASE)} (harus 212)"
# --- SATU rak menyala amber (ujung terjauh, RX, -20): rangka TERBUKA supaya
# Kairo 001 terlihat di dalamnya — panel belakang + 2 tiang samping + atap +
# alas; slot amber di depan atas. Amber HANYA di rak ini. ---
AMBER_X, AMBER_Y = RX, -20.0
block("SH_AmberBack", (AMBER_X, AMBER_Y - 0.45, 2.5), (2.4, 0.15, 5.0), SHELF_M)
block("SH_AmberPostL", (AMBER_X - 1.12, AMBER_Y, 2.5), (0.15, 1.0, 5.0), SHELF_M)
block("SH_AmberPostR", (AMBER_X + 1.12, AMBER_Y, 2.5), (0.15, 1.0, 5.0), SHELF_M)
block("SH_AmberTop", (AMBER_X, AMBER_Y, 4.95), (2.4, 1.0, 0.15), SHELF_M)
block("SH_AmberBase", (AMBER_X, AMBER_Y, 0.08), (2.4, 1.0, 0.15), SHELF_M)
block("SH_AmberSlot", (AMBER_X, AMBER_Y + 0.53, 4.2), (0.35, 0.06, 0.18), AMBER_SHELF_M)
# --- wajah NEXUS kecil: TIDAK ADA di Ep 5 (daftar kosong, animate tidak key apa-apa) ---
NX_FACE_SMALL_OBJS = []

# ---------- kabut (volume) ----------
def haze(name, loc, scale, density):
    m = bpy.data.materials.new(name + "M")
    m.use_nodes = True
    nt = m.node_tree.nodes
    nt.remove(nt["Principled BSDF"])
    vol = nt.new("ShaderNodeVolumePrincipled")
    vol.inputs["Density"].default_value = density
    vol.inputs["Color"].default_value = (0.85, 0.88, 0.95, 1.0)
    m.node_tree.links.new(vol.outputs["Volume"], nt["Material Output"].inputs["Volume"])
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    h = bpy.context.object
    h.name = name
    h.scale = scale
    h.data.materials.append(m)
    return h


if os.environ.get("FS_VOL", "1") == "1":
    haze("NX_Haze", (RX, 0, 6.0), (30, 24, 8), 0.02)  # aula memori (volume 60x48x16)

# ---------- karakter vinyl-toy ----------
# Kepala ~40% tinggi (KAIRO 1.8 unit). Karakter menghadap -Y (ke arah kamera default).
# Rig empty dibuat di animate_nexus.py.
CHARS = {}


def make_character(prefix, kind, scale, base, jacket_mat, skin_mat, eye_mat,
                   eye_red_mat=None):
    """kind: kairo | eva | sentinel | res | civ. base=(x,y,z)."""
    s = scale
    bx, by, bz = base
    hip_z = 0.48 * s
    sho_z = 1.12 * s
    sho_x = 0.38 * s * (1.35 if kind == "sentinel" else 1.0)
    head_z = 1.45 * s
    head_r = 0.275 * s * (1.1 if kind == "sentinel" else 1.0)
    head_mat = skin_mat
    # sentinel: mata sensor merah yang bisa dinyalakan via eye_red
    _red = kind == "sentinel"
    eye_r = 0.065 * s if _red else 0.055 * s  # sentinel 0.065 (0.075 terlalu besar/kartun)

    def P(x, y, z):
        return (bx + x, by + y, bz + z)

    body, head, armL, armR, legL, legR = [], [], [], [], [], []
    for side, sx in (("L", -1), ("R", 1)):
        _leg = block(f"{prefix}_Leg{side}", P(0.14 * sx * s, 0, 0.24 * s),
                     (0.17 * s, 0.2 * s, 0.42 * s), PANTS_K if kind in ("kairo", "res") else
                     (SUIT_EVA if kind == "eva" else (METAL_SEN if kind == "sentinel" else JACKET3)))
        _shoe = block(f"{prefix}_Shoe{side}", P(0.14 * sx * s, -0.04 * s, 0.07 * s),
                      (0.2 * s, 0.3 * s, 0.12 * s),
                      BOOTS if kind in ("kairo", "res") else METAL_SEN)
        (legL if side == "L" else legR).extend([_leg, _shoe])
    # torso + detail
    body.append(block(f"{prefix}_Torso", P(0, 0, 0.78 * s), (0.62 * s, 0.5 * s, 0.6 * s), jacket_mat))
    if kind == "kairo":
        # saku dada taktis (kotak pipih — JANGAN kena subsurf, biar tetap crisp)
        for side, sx in (("L", -1), ("R", 1)):
            body.append(block(f"{prefix}_Pocket{side}", P(0.15 * sx * s, -0.26 * s, 0.88 * s),
                              (0.2 * s, 0.03 * s, 0.14 * s), SHIRT))
        # bantalan bahu taktis
        for side, sx in (("L", -1), ("R", 1)):
            body.append(block(f"{prefix}_Pad{side}", P(0.32 * sx * s, 0, 1.08 * s),
                              (0.22 * s, 0.3 * s, 0.1 * s), JACKET))
    if kind == "sentinel":
        for side, sx in (("L", -1), ("R", 1)):
            body.append(block(f"{prefix}_Pad{side}", P(0.52 * sx * s, 0, 1.15 * s),
                              (0.42 * s, 0.36 * s, 0.22 * s), METAL_SEN2))
        # piston sendi bahu
        for side, sx in (("L", -1), ("R", 1)):
            body.append(cylinder(f"{prefix}_Piston{side}", P(sho_x * sx, 0.1 * s, sho_z),
                                 0.05 * s, 0.3 * s, METAL_SEN2, rot=(0, math.radians(90), 0)))
    # lengan (pivot di bahu)
    for side, sx in (("L", -1), ("R", 1)):
        lst = armL if side == "L" else armR
        lst.append(block(f"{prefix}_Arm{side}", P(sho_x * sx, 0, sho_z - 0.28 * s),
                         (0.16 * s, 0.18 * s, 0.5 * s), jacket_mat))
        lst.append(ball(f"{prefix}_Hand{side}", P(sho_x * sx, 0, sho_z - 0.56 * s),
                        (0.09 * s,) * 3, head_mat))
    # kepala + wajah
    head.append(ball(f"{prefix}_Head", P(0, 0, head_z), (head_r, head_r * 0.92, head_r), head_mat))
    if kind == "kairo":
        # rambut hitam pendek (mesh pendek, bukan particle hair)
        head.append(ball(f"{prefix}_Hair", P(0, 0.06 * s, head_z + 0.10 * s),
                         (head_r * 1.02, head_r * 0.95, head_r * 0.75), HAIR_KAI))
        # kerah tinggi jaket
        head.append(block(f"{prefix}_Collar", P(0, 0.05 * s, head_z - 0.24 * s),
                          (0.4 * s, 0.3 * s, 0.14 * s), JACKET))
    if kind == "sentinel":
        # helm / pelat kepala logam + visor
        head.append(ball(f"{prefix}_Helm", P(0, 0.05 * s, head_z + 0.08 * s),
                         (head_r * 1.08, head_r * 1.0, head_r * 0.7), METAL_SEN2))
        head.append(block(f"{prefix}_Visor", P(0, -0.22 * s, head_z + 0.05 * s),
                          (0.34 * s, 0.04 * s, 0.07 * s), SENSOR_OFF))
    eyes_black, eyes_red = [], []
    for side, sx in (("L", -1), ("R", 1)):
        eyes_black.append(ball(f"{prefix}_EyeB{side}", P(0.11 * sx * s, -0.235 * s, head_z + 0.03 * s),
                               (0.055 * s, 0.03 * s, 0.07 * s), eye_mat))
        if eye_red_mat is not None:
            eyes_red.append(ball(f"{prefix}_EyeR{side}", P(0.11 * sx * s, -0.24 * s, head_z + 0.03 * s),
                                 (eye_r, 0.032 * s, eye_r * 1.25), eye_red_mat))
    head.extend(eyes_black)
    head.extend(eyes_red)
    mouth = block(f"{prefix}_Mouth", P(0, -0.25 * s, head_z - 0.13 * s),
                  (0.12 * s, 0.03 * s, 0.03 * s), mat(f"{prefix}_MouthM", (0.10, 0.02, 0.03), 0.3))
    head.append(mouth)
    if kind in ("kairo", "res", "civ"):
        for side, sx in (("L", -1), ("R", 1)):
            head.append(block(f"{prefix}_Brow{side}", P(0.11 * sx * s, -0.25 * s, head_z + 0.13 * s),
                              (0.12 * s, 0.03 * s, 0.03 * s), HAIR_KAI, rot=(0, 0, math.radians(-10 * sx))))
    if kind == "eva":
        # garis circuitry biru di pelipis + "rambut energi" tipis
        for side, sx in (("L", -1), ("R", 1)):
            head.append(block(f"{prefix}_Circuit{side}", P(0.24 * sx * s, -0.1 * s, head_z + 0.1 * s),
                              (0.03 * s, 0.03 * s, 0.16 * s), CIRCUIT_BLUE))
    info = {
        "base": Vector(base), "scale": s, "kind": kind,
        "hip_z": hip_z, "sho_z": sho_z, "sho_x": sho_x, "head_z": head_z,
        "head_pivot_z": 1.18 * s,
        "body": body, "head": head, "armL": armL, "armR": armR,
        "legL": legL, "legR": legR,
        "eyes_black": eyes_black, "eyes_red": eyes_red, "mouth": mouth,
    }
    CHARS[prefix] = info
    return info


make_character("KAI", "kairo", 1.0, (0, 0, 0), JACKET, SKIN_KAI, EYE_DARK)
make_character("EVA", "eva", 1.0, (0, 0, 0), SUIT_EVA, SKIN_EVA, EYE_BLUE)
# KAIRO 001: model Kairo YANG SAMA + aged grade (kulit lelah, jaket usang).
# Uban di pelipis + bekas luka yang SAMA ditambahkan di bawah.
make_character("KAI001", "kairo", 1.0, (0, 0, 0), JACKET_AGED, SKIN_KAI001, EYE_DARK)
# Ep 5: TIDAK ADA Sentinel, TIDAK ADA RES/CIV, TIDAK ADA 213 Kairo —
# aula harus terasa kosong. JANGAN instans duplikat Kairo.

# --- bekas luka alis kiri KAIRO (WAJIB terbaca di close-up) ---
# Alis kiri = sisi +X (karakter menghadap -Y: kiri anatomis = +X).
# Garis TIPIS warna kulit sedikit lebih gelap #A68066, TANPA emissive.
SCAR_M = mat("Scar", (0.65, 0.50, 0.40), 0.7)
scar = block("KAI_Scar", (0.11, -0.22, 1.60), (0.06, 0.008, 0.006), SCAR_M,
             rot=(0, 0, math.radians(-25)))
CHARS["KAI"]["head"].append(scar)
CHARS["KAI"]["scar"] = scar
# kilau biru bekas luka (TERANG sejak frame 0, lanjutan Ep 3 S6) — salah satu
# dari tiga sumber cahaya di aula gelap. Nama material "ScarGlowM" dipakai
# animate_nexus_ep5.py.
SCAR_GLOW_M = emissive("ScarGlowM", (0.10, 0.30, 0.90), 6.0)
scar_glow = block("KAI_ScarGlow", (0.11, -0.235, 1.60), (0.07, 0.006, 0.008),
                  SCAR_GLOW_M, rot=(0, 0, math.radians(-25)))
scar_glow.hide_render = True
CHARS["KAI"]["head"].append(scar_glow)
CHARS["KAI"]["scar_glow"] = scar_glow
# --- KAIRO 001: uban di pelipis + bekas luka yang SAMA (buktinya ia Kairo
# yang sama — HARUS terlihat di semua close-up S4/S5/S6/S8). Fitur wajah di
# depan permukaan, bukan terkubur (pelajaran Ep 2). ---
for _side, _sx in (("L", -1), ("R", 1)):
    _grey = block(f"KAI001_GreyTemple{_side}", (0.26 * _sx, -0.05, 1.52),
                  (0.06, 0.10, 0.12), GREY_HAIR)
    CHARS["KAI001"]["head"].append(_grey)
scar001 = block("KAI001_Scar", (0.11, -0.22, 1.60), (0.06, 0.008, 0.006), SCAR_M,
                rot=(0, 0, math.radians(-25)))
CHARS["KAI001"]["head"].append(scar001)
CHARS["KAI001"]["scar"] = scar001
scar001_glow = block("KAI001_ScarGlow", (0.11, -0.235, 1.60), (0.07, 0.006, 0.008),
                     SCAR_GLOW_M, rot=(0, 0, math.radians(-25)))
scar001_glow.hide_render = True
CHARS["KAI001"]["head"].append(scar001_glow)
CHARS["KAI001"]["scar_glow"] = scar001_glow
# Ep 5: TIDAK ADA laser, TIDAK ADA backpack (tetap di lantai ruang inti),
# TIDAK ADA data core (tetap di soket ruang inti) — ketiganya TIDAK muncul
# satu frame pun di Ep 5.

# ---------- lampu ----------
def point_light(name, loc, color, energy, shadow=False):
    bpy.ops.object.light_add(type="POINT", location=loc)
    o = bpy.context.object
    o.name = name
    o.data.color = color
    o.data.energy = energy
    o.data.shadow_soft_size = 0.5
    o.data.use_shadow = shadow
    return o


def area_light(name, loc, color, energy, size, rot, shadow=False):
    bpy.ops.object.light_add(type="AREA", location=loc)
    o = bpy.context.object
    o.name = name
    o.data.color = color
    o.data.energy = energy
    o.data.size = size
    o.data.use_shadow = shadow
    o.rotation_euler = rot
    return o


# --- aula memori GELAP (Ep 5: tanpa merah — rim BIRU, nexus/eye = 0) ---
area_light("CoreFill", (RX, -16, 8), (0.62, 0.72, 1.0), 90.0, 16, (math.radians(55), 0, 0))
point_light("RimRedCore", (RX, 10.0, 3.0), (0.30, 0.65, 1.0), 500.0)  # Ep 5: rim BIRU (nama objek warisan Ep 2/3/4)
point_light("EvaRimCore", (RX + 4, -6, 2.5), (0.30, 0.65, 1.0), 0.0)
point_light("GateFill", (RX, 17.0, 3.0), (0.85, 0.88, 1.0), 0.0)  # Ep 5 re-test 2: fill depan EVA di S7 (di sisi kamera gerbang; 0 di luar S7)
point_light("NexusLight", (RX, 16.0, 10.0), (0.30, 0.65, 1.0), 0.0)  # Ep 5: 0 SELALU (wajah hilang)
area_light("GateLight", (RX, 22.5, 3.5), (1.0, 1.0, 0.95), 0.0, 12, (math.radians(90), 0, 0))
# garis fajar TIPIS lewat gerbang (HANYA S1/S7, di-key di animate dari
# lights["dawn"]): cahaya hangat #FFC98A, bukan kota — TIDAK ADA set kota.
area_light("DawnLight", (RX, 22.0, 4.0), (1.0, 0.79, 0.54), 0.0, 8, (math.radians(90), 0, 0))
# cahaya amber rak yang menyala (di-key di animate dari amber_shelf 0..1).
point_light("AmberLight", (AMBER_X, AMBER_Y + 1.0, 2.5), (1.0, 0.64, 0.24), 0.0)

# ---------- quality pass B7: subsurf 1 di semua bagian karakter, bevel 0 ----------
# Detail pipih (saku, bekas luka, circuitry, visor, uban) TIDAK kena subsurf —
# kalau kena, kotak pipih menggembung jadi bantal.
SUB = int(os.environ.get("FS_SUB", "1"))
_NOSUB = ("Pocket", "Scar", "Circuit", "Visor", "GreyTemple")
for _info in CHARS.values():
    for _part in (_info["body"] + _info["head"] + _info["armL"] + _info["armR"]
                  + _info["legL"] + _info["legR"]):
        if _part.type == "MESH" and SUB > 0 and not any(_k in _part.name for _k in _NOSUB):
            _s = _part.modifiers.new("Subdiv", "SUBSURF")
            _s.levels = 0
            _s.render_levels = SUB
# vinyl: clear-coat ringan
for _m, _coat in ((SKIN_KAI, 0.5), (JACKET, 0.3), (SKIN_KAI001, 0.5),
                  (JACKET_AGED, 0.3), (SKIN_EVA, 0.6)):
    _b = _m.node_tree.nodes["Principled BSDF"]
    if "Coat Weight" in _b.inputs:
        _b.inputs["Coat Weight"].default_value = _coat
        _b.inputs["Coat Roughness"].default_value = 0.15

# ---------- kamera default (plan yang menggerakkan per frame) ----------
bpy.ops.object.camera_add(location=(0, -6.5, 1.7))
cam = bpy.context.object
cam.data.lens = 40
look = Vector((0, 0, 1.3)) - cam.location
cam.rotation_euler = look.to_track_quat("-Z", "Y").to_euler()
cam.data.dof.use_dof = os.environ.get("FS_DOF", "1") == "1"
cam.data.dof.focus_distance = 6.5
cam.data.dof.aperture_fstop = 2.0
scene.camera = cam

scene.render.filepath = OUT
bpy.ops.render.render(write_still=True)
print("WROTE", OUT)
