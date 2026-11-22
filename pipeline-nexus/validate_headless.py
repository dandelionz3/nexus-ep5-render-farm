#!/usr/bin/env python3
"""validate_headless.py — jalankan validate_build.py + dry-run penuh
animate_nexus_ep5.py TANPA Blender (Blender tidak terpasang di VM ini).

Alasan: pelajaran Ep 4 — cross-check statis TIDAK menangkap NameError
(`_random2`); validate HARUS dijalankan. Karena `blender` tidak ada di VM,
skrip ini memasang stub minimal `bpy` + `mathutils` ke sys.modules lalu
mengeksekusi sumber validate_build.py (assert-nya berjalan penuh terhadap
objek fake yang mencatat nama/lokasi/skala/dimensi/material) dan
animate_nexus_ep5.py untuk frame 1..1440 (dry-run: keyframing jalan,
render di-stub jadi no-op). NameError / ImportError / KeyError di
build_scene maupun animate akan meledak di sini, bukan di farm.

Stub ini BUKAN Blender: ia tidak menilai gambar/pencahayaan. Yang ia
buktikan: (1) semua nama yang dirujuk ada, (2) semua assert koordinat/
jumlah/flag di validate_build.py lolos, (3) loop keyframe animate jalan
penuh 1440 frame tanpa error. Validasi visual tetap butuh stills farm.

  python3 validate_headless.py
"""
import os
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
PLAN = os.path.join(HERE, "plan.json")


# ---------------------------------------------------------------- stub bpy
class Fake:
    """Objek serba-bisa: atribut apa pun yang dibaca auto-dibuat (dan
    di-cache), dipanggil mengembalikan dirinya, di-iterasi kosong."""

    def __init__(self, name=""):
        object.__setattr__(self, "_fake_name", name)
        object.__setattr__(self, "_fake_attrs", {})

    def __getattr__(self, attr):
        if attr.startswith("__"):
            raise AttributeError(attr)
        attrs = object.__getattribute__(self, "_fake_attrs")
        if attr not in attrs:
            attrs[attr] = Fake(attr)
        return attrs[attr]

    def __setattr__(self, attr, value):
        if attr.startswith("_"):
            object.__setattr__(self, attr, value)
        else:
            object.__getattribute__(self, "_fake_attrs")[attr] = value

    def __call__(self, *a, **k):
        return self

    def __getitem__(self, key):
        # e.g. bpy.context.preferences.addons["cycles"] di jalur Cycles.
        return self

    def __iter__(self):
        return iter(())

    def __bool__(self):
        return True

    def __repr__(self):
        return f"<Fake {object.__getattribute__(self, '_fake_name')}>"


class FakeSocket:
    def __init__(self):
        self.default_value = 0.0

    def keyframe_insert(self, *a, **k):
        return None


class FakeInputs(dict):
    """dict input node: key yang belum ada auto-dibuat; `in` hanya benar
    untuk key yang pernah ditulis (seperti node Blender asli)."""

    def __missing__(self, key):
        s = FakeSocket()
        self[key] = s
        return s


class FakeNode:
    def __init__(self, ntype=""):
        self.type = ntype
        self.inputs = FakeInputs()
        self.outputs = FakeInputs()
        self.color_ramp = Fake("ColorRamp")

    def __repr__(self):
        return f"<FakeNode {self.type}>"


class FakeNodes(dict):
    def __missing__(self, key):
        n = FakeNode(key)
        self[key] = n
        return n

    def new(self, ntype):
        n = FakeNode(ntype)
        self[f"node_{len(self)}"] = n
        return n

    def remove(self, node):
        for k, v in list(self.items()):
            if v is node:
                del self[k]


class FakeLinks:
    def new(self, *a, **k):
        return None


class FakeNodeTree:
    def __init__(self):
        self.nodes = FakeNodes()
        self.links = FakeLinks()


class FakeMaterial:
    def __init__(self, name):
        self.name = name
        self.node_tree = FakeNodeTree()
        self.use_nodes = True
        self.blend_method = "OPAQUE"


class FakeWorld:
    def __init__(self, name):
        self.name = name
        self.node_tree = FakeNodeTree()
        self.use_nodes = True


class FakeData(Fake):
    def __init__(self):
        super().__init__("data")
        self.materials = []

    def keyframe_insert(self, *a, **k):
        return None


class FakeMatrix:
    def copy(self):
        return FakeMatrix()


class FakeDriver:
    def __init__(self):
        self.driver = Fake("driver")


class FakeObject(Fake):
    def __init__(self, name="", prim=None):
        super().__init__(name)
        object.__setattr__(self, "_prim", prim)
        object.__setattr__(self, "_dimensions", None)
        self.name = name  # -> register ke OBJECTS
        self.location = (0.0, 0.0, 0.0)
        self.scale = (1.0, 1.0, 1.0)
        self.rotation_euler = (0.0, 0.0, 0.0)
        self.hide_render = False
        self.data = FakeData()
        self.matrix_world = FakeMatrix()

    def __setattr__(self, attr, value):
        if attr.startswith("_"):
            object.__setattr__(self, attr, value)
        elif attr == "location" and isinstance(value, (tuple, list)):
            # Blender asli menyimpan location sebagai Vector (.x/.y/.z);
            # stub meniru itu supaya validate yang memakai .location.x jalan.
            super().__setattr__(attr, Vector(tuple(float(v) for v in value)))
        elif attr == "name":
            super().__setattr__(attr, value)
            if value:
                OBJECTS._register(value, self)
        else:
            super().__setattr__(attr, value)

    @property
    def dimensions(self):
        d = object.__getattribute__(self, "_dimensions")
        if d is not None:
            return d
        s = self.scale
        if object.__getattribute__(self, "_prim") == "PLANE":
            return (s[0], s[1], 0.0)
        return tuple(s)

    def select_set(self, v):
        return None

    def keyframe_insert(self, *a, **k):
        return None

    def driver_add(self, *a, **k):
        return FakeDriver()


class ObjectRegistry(dict):
    """bpy.data.objects: iterasi menghasilkan OBJEK (bukan key)."""

    def __iter__(self):
        return iter(list(self.values()))

    def _register(self, name, obj):
        self[name] = obj

    def new(self, name, data):
        return FakeObject(name)


class MaterialRegistry(dict):
    def new(self, name):
        m = FakeMaterial(name)
        self[name] = m
        return m


class WorldRegistry(dict):
    def new(self, name):
        w = FakeWorld(name)
        self[name] = w
        return w


class CollectionRegistry(dict):
    def new(self, name):
        c = FakeCollection(name)
        self[name] = c
        return c


class FakeObjList(list):
    def link(self, obj):
        if obj not in self:
            self.append(obj)
        if isinstance(obj, FakeObject):
            try:
                nm = obj.name
            except Exception:
                nm = None
            if nm:
                OBJECTS._register(nm, obj)

    def unlink(self, obj):
        if obj in self:
            self.remove(obj)


class FakeCollection:
    def __init__(self, name=""):
        self.name = name
        self.objects = FakeObjList()
        self.children = FakeObjList()


OBJECTS = ObjectRegistry()
MATERIALS = MaterialRegistry()
WORLDS = WorldRegistry()
COLLECTIONS = CollectionRegistry()


class FakeViewLayer:
    def __init__(self):
        self.objects = Fake("view_layer_objects")

    def update(self):
        return None


class FakeScene(Fake):
    def __init__(self):
        super().__init__("scene")
        self.collection = FakeCollection("Scene Collection")


class FakeContext:
    def __init__(self, scene):
        self.scene = scene
        self.object = None
        self.view_layer = FakeViewLayer()
        self.collection = scene.collection
        self.preferences = Fake("preferences")


SCENE = FakeScene()
CONTEXT = FakeContext(SCENE)


def _new_prim(prim, location, rotation):
    o = FakeObject("", prim=prim)
    o.location = tuple(location)
    o.rotation_euler = tuple(rotation)
    CONTEXT.object = o
    SCENE.collection.objects.link(o)
    return o


def _clear_scene():
    OBJECTS.clear()
    MATERIALS.clear()
    WORLDS.clear()
    COLLECTIONS.clear()
    SCENE.collection.objects.clear()
    SCENE.collection.children.clear()
    CONTEXT.object = None


class _OpsWM:
    def read_factory_settings(self, use_empty=True):
        _clear_scene()
        return None

    def __getattr__(self, name):
        return lambda *a, **k: Fake(name)


class _OpsMesh:
    def primitive_cube_add(self, size=1, location=(0, 0, 0), rotation=(0, 0, 0)):
        return _new_prim("CUBE", location, rotation)

    def primitive_uv_sphere_add(self, radius=1, location=(0, 0, 0), segments=32,
                                ring_count=16, rotation=(0, 0, 0)):
        return _new_prim("SPHERE", location, rotation)

    def primitive_cylinder_add(self, radius=1, depth=1, location=(0, 0, 0),
                               rotation=(0, 0, 0), vertices=32):
        return _new_prim("CYLINDER", location, rotation)

    def primitive_ico_sphere_add(self, subdivisions=1, radius=1, location=(0, 0, 0)):
        return _new_prim("SPHERE", location, (0, 0, 0))

    def primitive_plane_add(self, size=1, location=(0, 0, 0), rotation=(0, 0, 0)):
        return _new_prim("PLANE", location, rotation)

    def __getattr__(self, name):
        return lambda *a, **k: Fake(name)


class _OpsObject:
    def shade_smooth(self, *a, **k):
        return None

    def transform_apply(self, location=False, rotation=False, scale=True):
        o = CONTEXT.object
        if o is None:
            return None
        if scale:
            s = tuple(o.scale)
            if object.__getattribute__(o, "_prim") == "PLANE":
                object.__setattr__(o, "_dimensions", (s[0], s[1], 0.0))
            else:
                object.__setattr__(o, "_dimensions", (s[0], s[1], s[2]))
            o.scale = (1.0, 1.0, 1.0)
        return None

    def light_add(self, type="POINT", location=(0, 0, 0)):
        o = _new_prim("LIGHT", location, (0, 0, 0))
        o.data = FakeData()
        CONTEXT.object = o
        return None

    def camera_add(self, location=(0, 0, 0)):
        o = _new_prim("CAMERA", location, (0, 0, 0))
        o.data = FakeData()
        CONTEXT.object = o
        return None

    def __getattr__(self, name):
        return lambda *a, **k: Fake(name)


class _OpsRender:
    def render(self, *a, **k):
        print("[stub] bpy.ops.render.render — no-op (bukan Blender asli)")
        return None

    def __getattr__(self, name):
        return lambda *a, **k: Fake(name)


class _Ops:
    def __init__(self):
        self.wm = _OpsWM()
        self.mesh = _OpsMesh()
        self.object = _OpsObject()
        self.render = _OpsRender()

    def __getattr__(self, name):
        return Fake(name)


class _BpyData:
    def __init__(self):
        self.objects = OBJECTS
        self.materials = MATERIALS
        self.worlds = WORLDS
        self.collections = COLLECTIONS
        self.fonts = Fake("fonts")


class _Bpy:
    def __init__(self):
        self.data = _BpyData()
        self.context = CONTEXT
        self.ops = _Ops()


# ---------------------------------------------------------------- stub mathutils
class Vector:
    def __init__(self, seq=(0.0, 0.0, 0.0)):
        self._v = tuple(float(v) for v in seq)

    def __iter__(self):
        return iter(self._v)

    def __getitem__(self, i):
        return self._v[i]

    def __len__(self):
        return len(self._v)

    @property
    def x(self):
        return self._v[0]

    @property
    def y(self):
        return self._v[1]

    @property
    def z(self):
        return self._v[2]

    def __sub__(self, other):
        o = getattr(other, "_v", None)
        if o is None:
            try:
                o = tuple(float(v) for v in other)
            except Exception:
                return Vector((0.0, 0.0, 0.0))
        return Vector(tuple(a - b for a, b in zip(self._v, o)))

    def to_track_quat(self, *a):
        return _Quat()

    def __repr__(self):
        return f"Vector{self._v}"


class _Quat:
    def to_euler(self):
        return (0.0, 0.0, 0.0)

    def __matmul__(self, other):
        return self


class Quaternion:
    def __init__(self, *a):
        pass

    def __matmul__(self, other):
        return self

    def to_euler(self):
        return (0.0, 0.0, 0.0)


def _install_stubs():
    bpy_mod = types.ModuleType("bpy")
    bpy_mod.data = _Bpy().data
    bpy_mod.context = CONTEXT
    bpy_mod.ops = _Ops()
    sys.modules["bpy"] = bpy_mod
    mu = types.ModuleType("mathutils")
    mu.Vector = Vector
    mu.Quaternion = Quaternion
    sys.modules["mathutils"] = mu


def main():
    engine = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] in ("eevee", "cycles") else "eevee"
    _install_stubs()
    # 1) validate_build.py — exec sumbernya (assert berjalan penuh)
    val_path = os.path.join(HERE, "validate_build.py")
    val_src = open(val_path, encoding="utf-8").read()
    print("=== validate_build.py (headless stub) ===")
    exec(compile(val_src, val_path, "exec"),
         {"__file__": val_path, "__name__": "__main__"})
    print("HEADLESS VALIDATE OK")
    # 2) animate_nexus_ep5.py — dry-run penuh frame 1..1440
    if not os.path.exists(PLAN):
        print(f"PLAN HILANG: {PLAN} — jalankan python3 plan_nexus_ep5.py dulu")
        return 1
    anim_path = os.path.join(HERE, "animate_nexus_ep5.py")
    anim_src = open(anim_path, encoding="utf-8").read()
    print("=== animate_nexus_ep5.py dry-run 1..1440 (headless stub) ===")
    sys.argv = ["animate_nexus_ep5.py", "--", "/tmp/nx5_anim_dryrun",
                "--start", "1", "--end", "1440",
                "--plan", PLAN, "--res", "540", "960",
                "--lensk", "0.62", "--engine", engine]
    exec(compile(anim_src, anim_path, "exec"),
         {"__file__": anim_path, "__name__": "__main__"})
    print(f"HEADLESS ANIMATE DRY-RUN OK (1..1440, {engine})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
