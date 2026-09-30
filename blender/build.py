"""Build Compass Hill in Blender, save the .blend, export glTF, render stills.

    python3 blender/build.py [--parts site,house,...] [--no-export] [--render quick|final|none]
"""

import argparse
import math
import sys
import time
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from compass_hill import common as C  # noqa: E402
from compass_hill import site  # noqa: E402

OUT = ROOT.parent / "build"


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    import addon_utils
    addon_utils.enable("cycles")
    s = bpy.context.scene
    s.unit_settings.system = "IMPERIAL"
    s.unit_settings.length_unit = "FEET"


def finish(g, name, col, collide=True):
    obj = g.to_object(name, col, props={"collide": 1 if collide else 0})
    return obj


def build(parts):
    from compass_hill import layout as L
    t0 = time.time()
    cols = {}
    statics = {}

    def zone(name):
        if name not in cols:
            cols[name] = C.new_collection(name)
            statics[name] = (C.Geo(), C.Geo())
        return cols[name], statics[name][0], statics[name][1]

    holes = [site.rect(-60, 60, 736, 784)]
    if "court" in parts:
        from compass_hill import court
        col, g, gn = zone("Court")
        holes += court.build(col, g, gn)
    if "house" in parts:
        from compass_hill import house
        col, g, gn = zone("House")
        house.build(col, g, gn)
    if "entrance" in parts:
        from compass_hill import entrance
        col, g, gn = zone("Entrance")
        entrance.build(col, g, gn)
    if "garage" in parts:
        from compass_hill import garage
        col, g, gn = zone("Garage")
        holes += garage.build(col, g, gn)
    if "furnish" in parts:
        from compass_hill import furnish
        col, g, gn = zone("Furnishings")
        furnish.build(col, g, gn)
    if "landscape" in parts:
        from compass_hill import landscape
        col, g, gn = zone("Landscape")
        landscape.build(col, g, gn)
    if "site" in parts:
        col, g, gn = zone("Site")
        site.build_terrain(col, holes)
        site.build_pavements(g)
        site.build_skirt(gn)
    for name, (g, gn) in statics.items():
        finish(g, f"{name}_static", cols[name], True)
        finish(gn, f"{name}_detail", cols[name], False)
    print(f"built {parts} in {time.time() - t0:.1f}s; objects={len(bpy.data.objects)}")


def setup_world():
    s = bpy.context.scene
    w = bpy.data.worlds.new("Ohio sky")
    s.world = w
    w.use_nodes = True
    nt = w.node_tree
    bg = nt.nodes["Background"]
    sky = nt.nodes.new("ShaderNodeTexSky")
    sky.sky_type = "NISHITA"
    sky.sun_elevation = math.radians(28)
    sky.sun_rotation = math.radians(215)  # afternoon sun from the southwest
    sky.altitude = 250
    sky.air_density = 1.2
    sky.dust_density = 1.6
    nt.links.new(sky.outputs["Color"], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = 0.22
    sun = bpy.data.lights.new("Sun", "SUN")
    sun.energy = 2.6
    sun.angle = math.radians(1.0)
    sun.color = (1.0, 0.93, 0.82)
    so = bpy.data.objects.new("Sun", sun)
    s.collection.objects.link(so)
    # sun from the south-southwest (Blender -y is south), 28 deg up
    so.rotation_euler = (math.radians(62), 0, math.radians(215 - 180))


def camera(name, eye, target, lens=24):
    cam = bpy.data.cameras.new(name)
    cam.lens = lens
    cam.clip_end = 2000
    o = bpy.data.objects.new(name, cam)
    bpy.context.scene.collection.objects.link(o)
    o.location = C.P(*eye)
    d = C.P(*target) - o.location
    o.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    return o


VIEWS = {
    # name: (eye X,S,Z), (target X,S,Z), lens
    "aerial_southwest": ((-420, 1180, 260), (0, 700, -10), 32),
    "arrival_court": ((-30, 520, 7), (0, 700, 8), 22),
    "south_facade": ((40, 905, 2), (0, 760, 6), 22),
    "great_room": ((10, 781, 5.3), (-8, 752, 4), 16),
    "pavilion": ((70, 660, 6), (0, 591, 10), 22),
    "entrance_gate": ((30, 120, 6), (0, 230, 8), 24),
    "tunnel_loop": ((0, 645, -5.5), (0, 600, -6.5), 18),
    "berm_ring": ((-20, 902, -8), (0, 780, 2), 20),
    "meadow_pool": ((-60, 1105, -30), (0, 800, -5), 26),
}


def realize_lights():
    """Turn the walkthrough's light markers into Cycles point lights for stills."""
    n = 0
    for o in list(bpy.data.objects):
        if o.get("light") and o.get("on", 1):
            ld = bpy.data.lights.new(o.name + "_pt", "POINT")
            ld.energy = float(o["intensity"]) * 9.0
            c = o["color"].lstrip("#")
            ld.color = tuple(int(c[i:i + 2], 16) / 255 for i in (0, 2, 4))
            ld.shadow_soft_size = 0.15
            lo = bpy.data.objects.new(o.name + "_pt", ld)
            lo.location = o.matrix_world.translation
            bpy.context.scene.collection.objects.link(lo)
            n += 1
    print("point lights", n)


def render(mode, only=None):
    s = bpy.context.scene
    realize_lights()
    s.render.engine = "CYCLES"
    s.cycles.device = "CPU"
    s.cycles.samples = 16 if mode == "quick" else 64
    s.cycles.use_denoising = True
    s.cycles.max_bounces = 6
    s.render.resolution_x = 960 if mode == "quick" else 1600
    s.render.resolution_y = 540 if mode == "quick" else 900
    s.view_settings.view_transform = "AgX"
    s.view_settings.look = "AgX - Medium High Contrast" if hasattr(s.view_settings, "look") else "None"
    out = OUT / ("renders_quick" if mode == "quick" else "renders")
    out.mkdir(parents=True, exist_ok=True)
    for name, (eye, target, lens) in VIEWS.items():
        if only and name not in only:
            continue
        s.camera = camera("Cam_" + name, eye, target, lens)
        s.render.filepath = str(out / f"{name}.png")
        t = time.time()
        bpy.ops.render.render(write_still=True)
        print(f"rendered {name} in {time.time() - t:.0f}s")


def export():
    OUT.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT / "CompassHill.blend"))
    bpy.ops.export_scene.gltf(
        filepath=str(OUT / "CompassHill.glb"),
        export_format="GLB",
        export_extras=True,
        export_yup=True,
        export_apply=True,
        export_cameras=False,
        export_lights=False,
        export_image_format="JPEG",
        export_jpeg_quality=85,
    )
    print("exported", (OUT / "CompassHill.glb").stat().st_size / 1e6, "MB")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--parts", default="site,house,court,entrance,garage,landscape,furnish")
    ap.add_argument("--render", default="none")
    ap.add_argument("--views", default="")
    ap.add_argument("--no-export", action="store_true")
    a = ap.parse_args()
    reset()
    build(a.parts.split(","))
    setup_world()
    if not a.no_export:
        export()
    if a.render != "none":
        render(a.render, a.views.split(",") if a.views else None)
