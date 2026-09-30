"""Geometry toolkit for the Compass Hill build.

All inputs are in FEET, in site coordinates taken from the master plan:
  X = feet east of the north-south axis
  S = feet south of the public road (the plan's "distance from the road")
  Z = feet above the house main floor (hilltop grade = 0, walkout floor = -11)
Blender/glTF output is in meters, with the house centered near the origin:
  x = X * FT,  y = -(S - S0) * FT,  z = Z * FT
"""

import math
from pathlib import Path

import bpy
from mathutils import Vector

FT = 0.3048
S0 = 760.0  # the house's center line; puts the house at the origin
TEX_DIR = Path(__file__).resolve().parent.parent / "textures"


def P(X, S, Z):
    return Vector((X * FT, -(S - S0) * FT, Z * FT))


# --------------------------------------------------------------------------
# Materials
# --------------------------------------------------------------------------
# name: (texture or None, tile size in ft, base color, roughness, metallic, extras)
MATERIALS = {
    "limestone": ("limestone", 8.0, None, 0.85, 0.0, {}),
    "limestone_smooth": (None, 1, (0.72, 0.68, 0.60), 0.8, 0.0, {}),
    "slate": ("slate", 6.0, None, 0.6, 0.0, {}),
    "oak_siding": ("oak_siding", 5.33, None, 0.8, 0.0, {}),
    "oak": ("oak_floor", 5.33, (0.95, 0.9, 0.85), 0.55, 0.0, {}),
    "oak_timber": ("oak_siding", 8.0, (0.85, 0.78, 0.68), 0.7, 0.0, {}),
    "oak_floor": ("oak_floor", 5.33, None, 0.35, 0.0, {}),
    "standing_seam": ("standing_seam", 10.67, None, 0.45, 0.6, {}),
    "pv": ("pv", 5.5, None, 0.2, 0.3, {}),
    "grass": ("grass", 12.0, None, 0.95, 0.0, {}),
    "lawn": ("grass", 14.0, None, 0.95, 0.0, {}),
    "meadow": ("meadow", 16.0, None, 0.95, 0.0, {}),
    "woods_floor": ("leaf_litter", 12.0, None, 0.95, 0.0, {}),
    "gravel": ("gravel", 6.0, None, 0.95, 0.0, {}),
    "raked_gravel": ("raked_gravel", 8.0, None, 0.95, 0.0, {}),
    "aggregate": ("aggregate", 20.0, None, 0.85, 0.0, {}),
    "asphalt": ("asphalt", 10.0, None, 0.9, 0.0, {}),
    "cobble": ("cobble", 6.0, None, 0.9, 0.0, {}),
    "brick": ("brick", 5.0, None, 0.85, 0.0, {}),
    "plaster": ("plaster", 10.0, None, 0.9, 0.0, {}),
    "plaster_ceiling": ("plaster", 10.0, (1.0, 0.98, 0.95), 0.95, 0.0, {}),
    "polished_concrete": ("polished_concrete", 10.0, None, 0.25, 0.0, {}),
    "concrete": ("polished_concrete", 12.0, (0.85, 0.85, 0.83), 0.9, 0.0, {}),
    "tunnel_wall": ("polished_concrete", 10.0, (0.95, 0.94, 0.9), 0.85, 0.0, {}),
    "bark": ("bark", 4.0, None, 0.95, 0.0, {}),
    "bark_sycamore": ("plaster", 3.0, (0.85, 0.82, 0.74), 0.9, 0.0, {}),
    "foliage_oak": ("foliage", 10.0, (0.95, 1.0, 0.9), 0.9, 0.0, {}),
    "foliage_maple": ("autumn_foliage", 10.0, None, 0.9, 0.0, {}),
    "foliage_turning": ("foliage", 10.0, (0.95, 0.85, 0.55), 0.9, 0.0, {}),
    "foliage_cedar": ("dark_foliage", 6.0, None, 0.9, 0.0, {}),
    "foliage_pine": ("dark_foliage", 6.0, (0.9, 1.0, 1.0), 0.9, 0.0, {}),
    "meadow_tuft": ("meadow", 4.0, None, 0.95, 0.0, {}),
    "sedge": ("foliage", 3.0, (0.95, 1.0, 0.8), 0.95, 0.0, {}),
    "bronze_frame": (None, 1, (0.16, 0.13, 0.10), 0.45, 0.7, {}),
    "stainless": (None, 1, (0.78, 0.78, 0.76), 0.3, 1.0, {}),
    "bronze_ss": (None, 1, (0.55, 0.40, 0.22), 0.3, 1.0, {}),
    "black_iron": (None, 1, (0.05, 0.05, 0.05), 0.5, 0.8, {}),
    "glass": (None, 1, (0.55, 0.65, 0.68), 0.05, 0.0, {"alpha": 0.28}),
    "water": (None, 1, (0.16, 0.26, 0.24), 0.05, 0.0, {"alpha": 0.75}),
    "river_stone": (None, 1, (0.46, 0.44, 0.40), 0.7, 0.0, {}),
    "fieldstone": ("limestone", 3.0, (0.9, 0.9, 0.9), 0.9, 0.0, {}),
    "white_paint": (None, 1, (0.9, 0.88, 0.84), 0.6, 0.0, {}),
    "fabric_linen": (None, 1, (0.72, 0.66, 0.56), 0.95, 0.0, {}),
    "fabric_green": (None, 1, (0.22, 0.33, 0.25), 0.95, 0.0, {}),
    "fabric_rust": (None, 1, (0.52, 0.26, 0.16), 0.95, 0.0, {}),
    "leather": (None, 1, (0.30, 0.17, 0.09), 0.6, 0.0, {}),
    "rug_wool": (None, 1, (0.55, 0.42, 0.30), 1.0, 0.0, {}),
    "felt_green": (None, 1, (0.08, 0.32, 0.18), 1.0, 0.0, {}),
    "soapstone": (None, 1, (0.28, 0.30, 0.30), 0.5, 0.0, {}),
    "book_mix": ("brick", 1.5, (0.9, 0.8, 0.7), 0.8, 0.0, {}),
    "steel_shelf": (None, 1, (0.45, 0.47, 0.5), 0.5, 0.8, {}),
    "bin_blue": (None, 1, (0.16, 0.28, 0.46), 0.6, 0.0, {}),
    "tank_white": (None, 1, (0.86, 0.86, 0.84), 0.4, 0.2, {}),
    "pipe_blue": (None, 1, (0.15, 0.32, 0.62), 0.5, 0.2, {}),
    "pipe_purple": (None, 1, (0.45, 0.22, 0.55), 0.5, 0.2, {}),
    "pipe_red": (None, 1, (0.62, 0.10, 0.08), 0.5, 0.2, {}),
    "pipe_gray": (None, 1, (0.35, 0.36, 0.36), 0.5, 0.2, {}),
    "cable_tray": (None, 1, (0.6, 0.62, 0.62), 0.4, 0.9, {}),
    "safety_yellow": (None, 1, (0.85, 0.65, 0.08), 0.6, 0.0, {}),
    "screen_off": (None, 1, (0.02, 0.02, 0.025), 0.2, 0.0, {}),
    "lamp_warm": (None, 1, (1.0, 0.86, 0.66), 0.5, 0.0, {"emission": (1.0, 0.78, 0.5), "strength": 3.0}),
    "lamp_shade": (None, 1, (0.93, 0.86, 0.72), 0.8, 0.0, {"emission": (1.0, 0.8, 0.55), "strength": 0.6}),
    "flame": (None, 1, (1.0, 0.45, 0.08), 0.8, 0.0, {"emission": (1.0, 0.42, 0.06), "strength": 8.0}),
    "ember": (None, 1, (0.4, 0.05, 0.01), 0.9, 0.0, {"emission": (0.9, 0.2, 0.02), "strength": 2.0}),
    "sign_green": (None, 1, (0.1, 0.35, 0.18), 0.6, 0.0, {"emission": (0.1, 0.9, 0.3), "strength": 1.5}),
    "button": (None, 1, (0.85, 0.75, 0.5), 0.3, 1.0, {"emission": (1.0, 0.8, 0.4), "strength": 0.5}),
    "car_paint": (None, 1, (0.12, 0.2, 0.16), 0.35, 0.4, {}),
    "cart_white": (None, 1, (0.9, 0.9, 0.86), 0.4, 0.0, {}),
    "rubber": (None, 1, (0.04, 0.04, 0.04), 0.9, 0.0, {}),
    "canvas_blue": (None, 1, (0.18, 0.24, 0.36), 0.9, 0.0, {}),
    "skin": (None, 1, (0.72, 0.53, 0.40), 0.7, 0.0, {}),
    "denim": (None, 1, (0.18, 0.24, 0.38), 0.9, 0.0, {}),
    "shirt": (None, 1, (0.62, 0.36, 0.20), 0.9, 0.0, {}),
    "hair": (None, 1, (0.2, 0.14, 0.09), 0.8, 0.0, {}),
    "mailbox": (None, 1, (0.08, 0.08, 0.08), 0.5, 0.6, {}),
    "board_fence": (None, 1, (0.08, 0.08, 0.08), 0.8, 0.0, {}),
}

SMOOTH = {"foliage_oak", "foliage_maple", "foliage_turning", "foliage_cedar", "foliage_pine", "bark",
          "bark_sycamore", "river_stone", "fieldstone", "skin", "hair", "rubber", "bronze_ss", "stainless_round"}

_mat_cache = {}


def material(name):
    if name in _mat_cache:
        return _mat_cache[name]
    tex, tile, color, rough, metal, extra = MATERIALS[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    base_out = None
    if tex:
        img = bpy.data.images.load(str(TEX_DIR / f"{tex}.jpg"), check_existing=True)
        node = nt.nodes.new("ShaderNodeTexImage")
        node.image = img
        base_out = node.outputs["Color"]
        if color:
            mix = nt.nodes.new("ShaderNodeMix")
            mix.data_type = "RGBA"
            mix.blend_type = "MULTIPLY"
            mix.inputs["Factor"].default_value = 1.0
            nt.links.new(base_out, mix.inputs[6])
            mix.inputs[7].default_value = (*color, 1.0)
            base_out = mix.outputs[2]
    else:
        bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    if extra.get("vertex_color") and base_out is not None:
        vc = nt.nodes.new("ShaderNodeVertexColor")
        vc.layer_name = "Col"
        mix = nt.nodes.new("ShaderNodeMix")
        mix.data_type = "RGBA"
        mix.blend_type = "MULTIPLY"
        mix.inputs["Factor"].default_value = 1.0
        nt.links.new(base_out, mix.inputs[6])
        nt.links.new(vc.outputs["Color"], mix.inputs[7])
        base_out = mix.outputs[2]
    if base_out is not None:
        nt.links.new(base_out, bsdf.inputs["Base Color"])
    if "emission" in extra:
        bsdf.inputs["Emission Color"].default_value = (*extra["emission"], 1.0)
        bsdf.inputs["Emission Strength"].default_value = extra["strength"]
    if "alpha" in extra:
        bsdf.inputs["Alpha"].default_value = extra["alpha"]
        m.blend_method = "BLEND"
        try:
            m.surface_render_method = "BLENDED"
        except AttributeError:
            pass
    m["tile_ft"] = tile
    _mat_cache[name] = m
    return m


# --------------------------------------------------------------------------
# Geometry accumulator
# --------------------------------------------------------------------------
class Geo:
    """Collects faces (in site feet) grouped by material; becomes one object."""

    def __init__(self):
        self.verts = []
        self.faces = []  # (vertex indices, material name, uvs)

    # -- primitive emitters ------------------------------------------------
    def face(self, mat, pts, uvs=None):
        """pts: list of (X, S, Z) in feet, counter-clockwise seen from outside."""
        base = len(self.verts)
        self.verts.extend(pts)
        if uvs is None:
            uvs = world_uvs(pts, MATERIALS[mat][1])
        self.faces.append((list(range(base, base + len(pts))), mat, uvs))

    def box(self, mat, x0, x1, s0, s1, z0, z1, skip=(), top=None, bottom=None, side=None, fmat=None):
        """Axis-aligned box. skip: subset of {'top','bottom','n','s','e','w'}.
        fmat: per-face material overrides, e.g. {'s': 'plaster'}."""
        if x1 < x0:
            x0, x1 = x1, x0
        if s1 < s0:
            s0, s1 = s1, s0
        if z1 < z0:
            z0, z1 = z1, z0
        if x1 - x0 < 1e-4 or s1 - s0 < 1e-4 or z1 - z0 < 1e-4:
            return
        side = side or mat
        fm = {"top": top or mat, "bottom": bottom or mat, "n": side, "s": side, "e": side, "w": side}
        fm.update(fmat or {})
        # Blender y = -S, so "north" is smaller S.
        if "top" not in skip:
            self.face(fm["top"], [(x0, s1, z1), (x1, s1, z1), (x1, s0, z1), (x0, s0, z1)])
        if "bottom" not in skip:
            self.face(fm["bottom"], [(x0, s0, z0), (x1, s0, z0), (x1, s1, z0), (x0, s1, z0)])
        if "s" not in skip:
            self.face(fm["s"], [(x0, s1, z0), (x1, s1, z0), (x1, s1, z1), (x0, s1, z1)])
        if "n" not in skip:
            self.face(fm["n"], [(x1, s0, z0), (x0, s0, z0), (x0, s0, z1), (x1, s0, z1)])
        if "e" not in skip:
            self.face(fm["e"], [(x1, s1, z0), (x1, s0, z0), (x1, s0, z1), (x1, s1, z1)])
        if "w" not in skip:
            self.face(fm["w"], [(x0, s0, z0), (x0, s1, z0), (x0, s1, z1), (x0, s0, z1)])

    def prism(self, mat, poly, z0, z1, caps=True, side=None, top=None):
        """Vertical extrusion of a plan polygon [(X, S), ...] (CCW in Blender = CW in X,S)."""
        poly = ensure_ccw_blender(poly)
        n = len(poly)
        for i in range(n):
            a, b = poly[i], poly[(i + 1) % n]
            self.face(side or mat, [(a[0], a[1], z0), (b[0], b[1], z0), (b[0], b[1], z1), (a[0], a[1], z1)])
        if caps:
            self.face(top or mat, [(x, s, z1) for x, s in poly])
            self.face(mat, [(x, s, z0) for x, s in reversed(poly)])

    def cylinder(self, mat, cx, cs, r, z0, z1, seg=16, caps=True, r_top=None, inward=False):
        r_top = r if r_top is None else r_top
        ring0 = [(cx + r * math.cos(2 * math.pi * i / seg), cs - r * math.sin(2 * math.pi * i / seg)) for i in range(seg)]
        ring1 = [(cx + r_top * math.cos(2 * math.pi * i / seg), cs - r_top * math.sin(2 * math.pi * i / seg)) for i in range(seg)]
        circ = 2 * math.pi * max(r, 0.01)
        for i in range(seg):
            j = (i + 1) % seg
            pts = [(ring0[i][0], ring0[i][1], z0), (ring0[j][0], ring0[j][1], z0),
                   (ring1[j][0], ring1[j][1], z1), (ring1[i][0], ring1[i][1], z1)]
            t = MATERIALS[mat][1]
            u0, u1 = circ * i / seg / t, circ * (i + 1) / seg / t
            uvs = [(u0, z0 / t), (u1, z0 / t), (u1, z1 / t), (u0, z1 / t)]
            if inward:
                pts.reverse()
                uvs.reverse()
            self.face(mat, pts, uvs)
        if caps and not inward:
            if r_top > 1e-3:
                self.face(mat, [(x, s, z1) for x, s in ring1])
            self.face(mat, [(x, s, z0) for x, s in reversed(ring0)])

    def cone(self, mat, cx, cs, r, z0, apex, seg=16):
        for i in range(seg):
            a0 = 2 * math.pi * i / seg
            a1 = 2 * math.pi * (i + 1) / seg
            p0 = (cx + r * math.cos(a0), cs - r * math.sin(a0), z0)
            p1 = (cx + r * math.cos(a1), cs - r * math.sin(a1), z0)
            self.face(mat, [p0, p1, (cx, cs, apex)])

    def sphere(self, mat, cx, cs, cz, rx, ry=None, rz=None, seg=8, rings=6):
        ry = rx if ry is None else ry
        rz = rx if rz is None else rz
        rows = []
        for r in range(rings + 1):
            phi = math.pi * r / rings
            row = []
            for i in range(seg):
                th = 2 * math.pi * i / seg
                row.append((cx + rx * math.sin(phi) * math.cos(th), cs - ry * math.sin(phi) * math.sin(th), cz + rz * math.cos(phi)))
            rows.append(row)
        t = MATERIALS[mat][1]
        for r in range(rings):
            for i in range(seg):
                j = (i + 1) % seg
                pts = [rows[r][i], rows[r + 1][i], rows[r + 1][j], rows[r][j]]
                if r == 0:
                    pts = [rows[0][i], rows[1][i], rows[1][j]]
                elif r == rings - 1:
                    pts = [rows[r][i], rows[r + 1][i], rows[r][j]]
                uvs = [(p[0] / t + p[2] / t, p[1] / t) for p in pts]
                self.face(mat, pts, uvs)

    def tuft(self, mat, x, s, z, h, r, blades=6, rng=None):
        """Grass/sedge clump: thin blades fanning out from a point."""
        import random as _r
        rng = rng or _r
        for k in range(blades):
            a = 2 * math.pi * k / blades + rng.uniform(-0.3, 0.3)
            lean = r * rng.uniform(0.6, 1.0)
            w = 0.18
            tip = (x + lean * math.cos(a), s - lean * math.sin(a), z + h * rng.uniform(0.7, 1.0))
            p0 = (x - w * math.sin(a), s - w * math.cos(a), z)
            p1 = (x + w * math.sin(a), s + w * math.cos(a), z)
            self.face(mat, [p0, p1, tip], [(0, 0), (0.2, 0), (0.1, 1)])
            self.face(mat, [p1, p0, tip], [(0.2, 0), (0, 0), (0.1, 1)])

    def ribbon(self, mat, path, width, zfn, offset=0.0, tile=None):
        """A strip following a plan polyline [(X, S)], height from zfn(X, S)."""
        t = tile or MATERIALS[mat][1]
        left, right = offset_polyline(path, width / 2 + offset), offset_polyline(path, -width / 2 + offset)
        dist = 0.0
        for i in range(len(path) - 1):
            seg = math.dist(path[i], path[i + 1])
            l0, l1, r0, r1 = left[i], left[i + 1], right[i], right[i + 1]
            pts = [(r0[0], r0[1], zfn(*r0)), (r1[0], r1[1], zfn(*r1)), (l1[0], l1[1], zfn(*l1)), (l0[0], l0[1], zfn(*l0))]
            uvs = [(0, dist / t), (0, (dist + seg) / t), (width / t, (dist + seg) / t), (width / t, dist / t)]
            if is_cw(pts):
                pts.reverse()
                uvs.reverse()
            self.face(mat, pts, uvs)
            dist += seg

    def merge(self, other):
        base = len(self.verts)
        self.verts.extend(other.verts)
        for idx, m, uvs in other.faces:
            self.faces.append(([i + base for i in idx], m, uvs))

    # -- output --------------------------------------------------------------
    def to_object(self, name, collection, origin=(0.0, 0.0, 0.0), props=None, local_at=None, rot_deg=0.0):
        """origin: pivot in site feet (verts are site coordinates).
        local_at: if given, verts are LOCAL feet around (0,0,0); the object is
        placed at this site point and rotated rot_deg about Z (CCW from above)."""
        if not self.faces:
            return None
        mesh = bpy.data.meshes.new(name)
        if local_at is not None:
            o = P(*local_at)
            verts = [Vector((x * FT, -s * FT, z * FT)) for x, s, z in self.verts]
        else:
            ox, os_, oz = origin
            o = P(ox, os_, oz)
            verts = [P(x, s, z) - o for x, s, z in self.verts]
        mats = []
        for _, m, _ in self.faces:
            if m not in mats:
                mats.append(m)
        mesh.from_pydata(verts, [], [f[0] for f in self.faces])
        for m in mats:
            mesh.materials.append(material(m))
        uv = mesh.uv_layers.new(name="UVMap")
        li = 0
        for poly, (idx, m, uvs) in zip(mesh.polygons, self.faces):
            poly.material_index = mats.index(m)
            poly.use_smooth = m in SMOOTH
            for k in range(poly.loop_total):
                uv.data[poly.loop_start + k].uv = uvs[k]
        mesh.validate()
        if any(m in SMOOTH for m in mats):
            import bmesh
            bm = bmesh.new()
            bm.from_mesh(mesh)
            smooth_verts = {v for f in bm.faces if f.smooth for v in f.verts}
            bmesh.ops.remove_doubles(bm, verts=list(smooth_verts), dist=0.0005)
            bm.to_mesh(mesh)
            bm.free()
        obj = bpy.data.objects.new(name, mesh)
        obj.location = o
        obj.rotation_euler = (0.0, 0.0, math.radians(rot_deg))
        collection.objects.link(obj)
        for k, v in (props or {}).items():
            obj[k] = v
        return obj


def world_uvs(pts, tile):
    """Planar UVs by the face's dominant axis, in world feet / tile."""
    n = newell(pts)
    ax = max(range(3), key=lambda i: abs(n[i]))
    out = []
    for x, s, z in pts:
        if ax == 2:
            out.append((x / tile, -s / tile))
        elif ax == 0:
            out.append((-s / tile * math.copysign(1, n[0]), z / tile))
        else:
            out.append((x / tile * math.copysign(1, -n[1]), z / tile))
    return out


def newell(pts):
    nx = ny = nz = 0.0
    for i in range(len(pts)):
        x0, y0, z0 = pts[i][0], -pts[i][1], pts[i][2]
        x1, y1, z1 = pts[(i + 1) % len(pts)][0], -pts[(i + 1) % len(pts)][1], pts[(i + 1) % len(pts)][2]
        nx += (y0 - y1) * (z0 + z1)
        ny += (z0 - z1) * (x0 + x1)
        nz += (x0 - x1) * (y0 + y1)
    return (nx, ny, nz)


def is_cw(pts):
    return newell(pts)[2] < 0


def ensure_ccw_blender(poly):
    area = 0.0
    for i in range(len(poly)):
        x0, s0 = poly[i]
        x1, s1 = poly[(i + 1) % len(poly)]
        area += x0 * (-s1) - x1 * (-s0)
    return poly if area > 0 else list(reversed(poly))


def offset_polyline(path, d):
    """Offset to the left (in Blender xy) by d feet."""
    out = []
    n = len(path)
    for i in range(n):
        if i == 0:
            dx, ds = path[1][0] - path[0][0], path[1][1] - path[0][1]
        elif i == n - 1:
            dx, ds = path[-1][0] - path[-2][0], path[-1][1] - path[-2][1]
        else:
            dx, ds = path[i + 1][0] - path[i - 1][0], path[i + 1][1] - path[i - 1][1]
        L = math.hypot(dx, ds) or 1
        # blender dir = (dx, -ds); left normal = (ds, dx) in blender => (X: ds, S: -dx)
        out.append((path[i][0] + d * (ds / L), path[i][1] - d * (dx / L)))
    return out


# --------------------------------------------------------------------------
# Walls with openings
# --------------------------------------------------------------------------
def rect_minus(rect, holes):
    """rect=(a0,a1,b0,b1); holes list of same. Returns non-overlapping rects."""
    a0, a1, b0, b1 = rect
    hs = [(max(a0, h[0]), min(a1, h[1]), max(b0, h[2]), min(b1, h[3])) for h in holes]
    hs = [h for h in hs if h[1] - h[0] > 1e-6 and h[3] - h[2] > 1e-6]
    if not hs:
        return [rect]
    As = sorted({a0, a1, *[h[0] for h in hs], *[h[1] for h in hs]})
    Bs = sorted({b0, b1, *[h[2] for h in hs], *[h[3] for h in hs]})
    out = []
    for j in range(len(Bs) - 1):
        row = []
        for i in range(len(As) - 1):
            ca, cb = (As[i] + As[i + 1]) / 2, (Bs[j] + Bs[j + 1]) / 2
            inside = any(h[0] <= ca <= h[1] and h[2] <= cb <= h[3] for h in hs)
            if not inside:
                if row and abs(row[-1][1] - As[i]) < 1e-9:
                    row[-1] = (row[-1][0], As[i + 1], Bs[j], Bs[j + 1])
                else:
                    row.append((As[i], As[i + 1], Bs[j], Bs[j + 1]))
        out.extend(row)
    return out


def wall_x(g, mat, x0, x1, s0, s1, z0, z1, openings=(), fmat=None, reveal=None):
    """Wall running east-west (thickness s0..s1). openings: [(xa, xb, za, zb)]."""
    for a0, a1, b0, b1 in rect_minus((x0, x1, z0, z1), openings):
        fm = dict(fmat or {})
        if reveal:
            # faces exposed by an opening take the reveal material
            if a0 > x0 + 1e-6:
                fm.setdefault("w", reveal)
            if a1 < x1 - 1e-6:
                fm.setdefault("e", reveal)
            if b0 > z0 + 1e-6:
                fm.setdefault("bottom", reveal)
            if b1 < z1 - 1e-6:
                fm.setdefault("top", reveal)
        g.box(mat, a0, a1, s0, s1, b0, b1, fmat=fm)


def wall_s(g, mat, s0, s1, x0, x1, z0, z1, openings=(), fmat=None, reveal=None):
    """Wall running north-south (thickness x0..x1). openings: [(sa, sb, za, zb)]."""
    for a0, a1, b0, b1 in rect_minus((s0, s1, z0, z1), openings):
        fm = dict(fmat or {})
        if reveal:
            if a0 > s0 + 1e-6:
                fm.setdefault("n", reveal)
            if a1 < s1 - 1e-6:
                fm.setdefault("s", reveal)
            if b0 > z0 + 1e-6:
                fm.setdefault("bottom", reveal)
            if b1 < z1 - 1e-6:
                fm.setdefault("top", reveal)
        g.box(mat, x0, x1, a0, a1, b0, b1, fmat=fm)


def slab(g, mat, x0, x1, s0, s1, z0, z1, holes=(), top=None, bottom=None):
    """Horizontal slab with rectangular holes [(xa, xb, sa, sb)]."""
    for a0, a1, b0, b1 in rect_minus((x0, x1, s0, s1), holes):
        g.box(mat, a0, a1, b0, b1, z0, z1, top=top, bottom=bottom)


def empty(name, collection, X, S, Z, props=None, size=0.3):
    e = bpy.data.objects.new(name, None)
    e.empty_display_size = size
    e.location = P(X, S, Z)
    collection.objects.link(e)
    for k, v in (props or {}).items():
        e[k] = v
    return e


def new_collection(name, parent=None):
    c = bpy.data.collections.new(name)
    (parent or bpy.context.scene.collection).children.link(c)
    return c


def smoothstep(e0, e1, x):
    t = min(max((x - e0) / (e1 - e0), 0.0), 1.0)
    return t * t * (3 - 2 * t)
