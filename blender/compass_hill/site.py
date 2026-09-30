"""Terrain and pavements."""

import math

import bpy

from . import layout as L
from .common import FT, P, Geo, material, smoothstep

STEP = 6.0


def _lines(lo, hi, special):
    vals = [lo + i * STEP for i in range(int((hi - lo) / STEP) + 1)]
    for v in special:
        vals = [x for x in vals if abs(x - v) > 1.5]
    return sorted(set(vals + [v for v in special if lo <= v <= hi]))


def zone_material(X, S):
    ax = abs(X)
    if ax > 385 and S > 60:
        return "woods_floor"  # privacy belts
    if S > 905 and ax > 165:
        return "woods_floor"  # legacy woods, lower corners
    if S > 1275:
        return "woods_floor"  # south cedar belt
    if S > 950:
        return "meadow"
    if 110 < X < 330 and 500 < S < 720:
        return "meadow"  # septic field under meadow, east shoulder
    if 20 < S < 40 or (S > 800 and ax > 120):
        return "meadow"
    return "lawn"


def build_terrain(col, holes):
    """holes: list of site-foot polygons [(X, S), ...] cut out with a boolean."""
    xs = _lines(L.PARCEL_X[0], L.PARCEL_X[1], [-60, 60, -290, -178, -196, -142])
    ss = _lines(L.PARCEL_S[0], L.PARCEL_S[1], [736, 784, 674, 686, 612, 642])
    verts = []
    for s in ss:
        for x in xs:
            verts.append(P(x, s, L.terrain(x, s)))
    nx = len(xs)
    faces, mats = [], []
    names = ["lawn", "meadow", "woods_floor"]
    for j in range(len(ss) - 1):
        for i in range(nx - 1):
            a = j * nx + i
            # CCW seen from above (y = -S): (i,j+1),(i+1,j+1),(i+1,j),(i,j)
            faces.append((a + nx, a + nx + 1, a + 1, a))
            cx, cs = (xs[i] + xs[i + 1]) / 2, (ss[j] + ss[j + 1]) / 2
            mats.append(names.index(zone_material(cx, cs)))
    mesh = bpy.data.meshes.new("Terrain")
    mesh.from_pydata(verts, [], faces)
    for n in names:
        mesh.materials.append(material(n))
    uv = mesh.uv_layers.new(name="UVMap")
    for poly, mi in zip(mesh.polygons, mats):
        poly.material_index = mi
        poly.use_smooth = True
        t = 14.0
        for k in range(poly.loop_total):
            v = mesh.vertices[mesh.loops[poly.loop_start + k].vertex_index].co
            uv.data[poly.loop_start + k].uv = (v.x / FT / t, v.y / FT / t)
    obj = bpy.data.objects.new("Terrain", mesh)
    col.objects.link(obj)
    obj["collide"] = 1
    obj["ground"] = 1
    # cut holes
    cutters = []
    for k, poly in enumerate(holes):
        g = Geo()
        g.prism("concrete", poly, -60, 40)
        cutters.append(g.to_object(f"_cut{k}", col))
    if cutters:
        bpy.ops.object.select_all(action="DESELECT")
        for c in cutters[1:]:
            c.select_set(True)
        bpy.context.view_layer.objects.active = cutters[0]
        cutters[0].select_set(True)
        if len(cutters) > 1:
            bpy.ops.object.join()
        cutter = cutters[0]
        mod = obj.modifiers.new("holes", "BOOLEAN")
        mod.operation = "DIFFERENCE"
        mod.solver = "EXACT"
        mod.use_hole_tolerant = True
        mod.object = cutter
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier=mod.name)
        bpy.data.objects.remove(cutter)
    return obj


def build_skirt(g):
    """Neighboring farmland beyond the parcel: harvested corn and soybean fields, fencerows."""
    from .common import Geo
    x0, x1 = L.PARCEL_X
    s0, s1 = L.PARCEL_S
    far = 2600.0
    z_far = -30.0
    step = 60.0
    xs = [x0 + i * step for i in range(int((x1 - x0) / step) + 1)]
    ss = [s0 + i * step for i in range(int((s1 - s0) / step) + 1)]
    edge = ([(x, s0) for x in xs] + [(x1, s) for s in ss[1:]] + [(x, s1) for x in reversed(xs[:-1])]
            + [(x0, s) for s in reversed(ss[1:-1])])
    cx, cs = (x0 + x1) / 2, (s0 + s1) / 2
    n = len(edge)
    for i in range(n):
        a, b = edge[i], edge[(i + 1) % n]
        def out(p):
            dx, ds = p[0] - cx, p[1] - cs
            d = math.hypot(dx, ds)
            return (cx + dx / d * far, cs + ds / d * far)
        oa, ob = out(a), out(b)
        za = L.terrain(*a) if a[1] > 0 else -8.0
        zb = L.terrain(*b) if b[1] > 0 else -8.0
        mat = "meadow"
        pts = [(a[0], a[1], za), (b[0], b[1], zb), (ob[0], ob[1], z_far), (oa[0], oa[1], z_far)]
        from .common import is_cw
        if is_cw(pts):
            pts.reverse()
        g.face(mat, pts)


def rect(x0, x1, s0, s1):
    return [(x0, s0), (x1, s0), (x1, s1), (x0, s1)]


def rot_rect(cx, cs, along, across, ang_deg):
    """Rectangle centered at (cx, cs), 'along' in the direction ang (deg, CCW from east in plan)."""
    a = math.radians(ang_deg)
    ux, us = math.cos(a), -math.sin(a)  # plan: S grows south
    vx, vs = -us, ux
    pts = []
    for sa, sb in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        pts.append((cx + sa * along / 2 * ux + sb * across / 2 * vx, cs + sa * along / 2 * us + sb * across / 2 * vs))
    return pts


def build_pavements(g):
    """Roads, drives, court, pads, forecourt, trails (added to a static Geo)."""
    z = L.pave_z
    # County road (asphalt, 22 ft) with gravel shoulders
    g.ribbon("asphalt", [(-450, -12), (450, -12)], 22, lambda x, s: -8.0 + 0.02)
    g.ribbon("gravel", [(-450, -0.5), (450, -0.5)], 3, lambda x, s: -8.0 + 0.01)
    g.ribbon("gravel", [(-450, -23.5), (450, -23.5)], 3, lambda x, s: -8.0 + 0.01)
    # Lay-by: heavy-duty concrete, one way W -> E, with 50-ft tapers
    g.ribbon("aggregate", [(-207, 1), (-157, 45 + 14)], 28, z)
    g.ribbon("aggregate", [(157, 45 + 14), (207, 1)], 28, z)
    g.ribbon("aggregate", [(-157, 59), (157, 59)], 28, z)
    # Stem + visitor pads
    g.ribbon("aggregate", [(0, 73), (0, 132)], 24, z)
    for x0 in (-52, -32, 12, 32):
        g.ribbon("aggregate", [(x0 + 10, 73), (x0 + 10, 91)], 20, z)
    # Teardrop: ring road + cobble apron around a planted island
    tc = L.TEARDROP_C
    ring = [(tc[0] + 37 * math.cos(t), tc[1] - 37 * math.sin(t)) for t in [2 * math.pi * i / 48 for i in range(49)]]
    g.ribbon("aggregate", ring, 22, z)
    apron = [(tc[0] + 23 * math.cos(t), tc[1] - 23 * math.sin(t)) for t in [2 * math.pi * i / 40 for i in range(41)]]
    g.ribbon("cobble", apron, 6, lambda x, s: z(x, s) + 0.05)
    g.ribbon("aggregate", [(0, 222), (0, 264)], 24, z)
    # S-bend drive
    g.ribbon("aggregate", s_bend(), 24, z)
    # Motor court ring, walk ring, crosswalks
    cx, cs = L.COURT_C
    ring = [(cx + 63 * math.cos(t), cs - 63 * math.sin(t)) for t in [2 * math.pi * i / 72 for i in range(73)]]
    g.ribbon("aggregate", ring, 24, z)
    walk = [(cx + 47 * math.cos(t), cs - 47 * math.sin(t)) for t in [2 * math.pi * i / 64 for i in range(65)]]
    g.ribbon("cobble", walk, 8, lambda x, s: z(x, s) + 0.02)
    # Pads on 45-degree spokes (south slot open) are built in court.py
    # Forecourt drop-off loop (one way) under the porte-cochere
    loop = [(28, 662), (36, 690), (40, 712), (30, 719), (0, 719), (-30, 719), (-40, 712), (-36, 690), (-28, 662)]
    g.ribbon("aggregate", smooth(loop, 4), 12, z)
    g.ribbon("cobble", [(0, 712.5), (0, 725.5)], 12, lambda x, s: z(x, s) + 0.03)  # raised crosswalk
    # Porch apron / wrap porch at grade (stone) handled in house.py
    # Garage spur and loop (west)
    spur = [(-74, 591), (-110, 595), (-138, 627), (-195, 627), (-235, 627), (-262, 612), (-262, 575), (-235, 560), (-160, 560), (-110, 572), (-74, 585)]
    g.ribbon("aggregate", smooth(spur, 4), 16, z)
    g.ribbon("aggregate", [(-262, 612), (-286, 650), (-296, 680)], 14, z)  # to the ramp head
    # Trails: 8-ft crushed limestone loop through meadow and woods
    trail = [(-60, 800), (-120, 830), (-200, 900), (-280, 1000), (-300, 1120), (-220, 1230), (-60, 1250),
             (80, 1240), (240, 1200), (310, 1080), (280, 960), (200, 890), (120, 832), (60, 800)]
    g.ribbon("gravel", smooth(trail, 6), 8, lambda x, s: L.terrain(x, s) + 0.12)
    # Berm-top path with the arch crossing
    return g


def s_bend():
    pts = []
    for i in range(33):
        t = i / 32
        s = 262 + t * (516 - 262)
        x = 42 * math.sin(2 * math.pi * t)
        pts.append((x, s))
    return pts


def smooth(pts, sub):
    """Catmull-Rom through points."""
    out = []
    n = len(pts)
    for i in range(n - 1):
        p0 = pts[max(i - 1, 0)]
        p1, p2 = pts[i], pts[i + 1]
        p3 = pts[min(i + 2, n - 1)]
        for k in range(sub):
            t = k / sub
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[d]) + (-p0[d] + p2[d]) * t + (2 * p0[d] - 5 * p1[d] + 4 * p2[d] - p3[d]) * t2
                                    + (-p0[d] + 3 * p1[d] - 3 * p2[d] + p3[d]) * t3) for d in range(2)))
    out.append(pts[-1])
    return out
