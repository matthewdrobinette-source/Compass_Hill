"""Legacy woods, belts, meadow, Zen garden, brook, basin, arch, creeks, pool, spreaders."""

import math
import random

from . import interact as I
from . import layout as L
from .common import Geo

T = L.terrain
rnd = random.Random(1803)  # Ohio statehood


# --------------------------------------------------------------------------
# Trees (low-poly, merged per material)
# --------------------------------------------------------------------------
def deciduous(g, gn, x, s, h, spread, leaf="foliage_oak", bark="bark", lean=0.0):
    z = T(x, s) - 0.3
    trunk_h = h * 0.45
    g.cylinder(bark, x, s, spread * 0.07 + 0.4, z, z + trunk_h, seg=6, caps=False, r_top=spread * 0.045 + 0.25)
    n = 5 if spread > 12 else 4
    for k in range(n):
        a = rnd.uniform(0, 2 * math.pi)
        r = spread * rnd.uniform(0.15, 0.45)
        cz = z + trunk_h + h * rnd.uniform(0.12, 0.38)
        rad = spread * rnd.uniform(0.38, 0.55)
        gn.sphere(leaf, x + r * math.cos(a) + lean, s + r * math.sin(a), cz, rad, rad, rad * 0.72, seg=7, rings=5)
    gn.sphere(leaf, x + lean, s, z + h * 0.8, spread * 0.5, spread * 0.5, spread * 0.42, seg=7, rings=5)


def conifer(gn, g, x, s, h, r, leaf="foliage_cedar", tiers=3):
    z = T(x, s) - 0.3
    g.cylinder("bark", x, s, 0.4, z, z + h * 0.25, seg=5, caps=False)
    for k in range(tiers):
        f = k / tiers
        gn.cone(leaf, x, s, r * (1 - 0.55 * f), z + h * (0.12 + 0.28 * f), z + h * (0.55 + 0.45 * (k + 1) / tiers), seg=7)


def white_pine(gn, g, x, s, h):
    z = T(x, s) - 0.3
    g.cylinder("bark", x, s, 0.6, z, z + h * 0.95, seg=5, caps=False, r_top=0.2)
    for k in range(5):
        zz = z + h * (0.3 + k * 0.14)
        rr = h * 0.22 * (1 - k * 0.15)
        gn.sphere("foliage_pine", x + rnd.uniform(-1, 1), s + rnd.uniform(-1, 1), zz, rr, rr, rr * 0.35, seg=7, rings=4)


def mixed_tree(g, gn, x, s, scale=1.0):
    kind = rnd.random()
    if kind < 0.42:      # white / bur / chinkapin oak (the backbone)
        deciduous(g, gn, x, s, 58 * scale, 44 * scale, leaf=rnd.choice(["foliage_oak", "foliage_oak", "foliage_turning"]))
    elif kind < 0.5:     # sugar maple, turning orange in early October
        deciduous(g, gn, x, s, 52 * scale, 34 * scale, leaf="foliage_maple")
    elif kind < 0.62:    # tulip poplar, tall and narrow
        deciduous(g, gn, x, s, 78 * scale, 24 * scale, leaf="foliage_turning")
    elif kind < 0.74:    # shagbark hickory
        deciduous(g, gn, x, s, 60 * scale, 28 * scale, leaf="foliage_turning")
    elif kind < 0.86:    # Ohio buckeye
        deciduous(g, gn, x, s, 38 * scale, 26 * scale, leaf="foliage_turning")
    else:                # black gum
        deciduous(g, gn, x, s, 44 * scale, 24 * scale, leaf="foliage_oak")


def scatter(x0, x1, s0, s1, spacing, jitter=0.45, keep=None):
    pts = []
    s = s0
    row = 0
    while s < s1:
        x = x0 + (spacing / 2 if row % 2 else 0)
        while x < x1:
            px = x + rnd.uniform(-jitter, jitter) * spacing
            ps = s + rnd.uniform(-jitter, jitter) * spacing
            if keep is None or keep(px, ps):
                pts.append((px, ps))
            x += spacing
        s += spacing * 0.87
        row += 1
    return pts


def trees(g, gn):
    # legacy woods in the lower corners (SW has the working spreader at its edge)
    for side in (-1, 1):
        for x, s in scatter(170, 440, 915, 1265, 34):
            mixed_tree(g, gn, side * x, s, rnd.uniform(0.75, 1.1))
    # privacy belts on both side lines: red cedar and white pine, some oaks
    for side in (-1, 1):
        for x, s in scatter(392, 444, 70, 900, 22, keep=lambda x, s: True):
            r = rnd.random()
            if r < 0.45:
                conifer(gn, g, side * x, s, rnd.uniform(26, 38), rnd.uniform(6, 8))
            elif r < 0.8:
                white_pine(gn, g, side * x, s, rnd.uniform(45, 70))
            else:
                mixed_tree(g, gn, side * x, s, 0.85)
    # evergreen belt behind the lay-by and berm, with one staggered wildlife gap (west)
    for x, s in scatter(-440, 440, 86, 118, 18):
        if abs(x) < 75 or -135 < x < -112:
            continue
        if rnd.random() < 0.55:
            conifer(gn, g, x, s, rnd.uniform(24, 34), rnd.uniform(5.5, 7.5))
        else:
            white_pine(gn, g, x, s, rnd.uniform(40, 60))
    # low red cedar along the south line (shorter in the view corridor)
    for x in range(-440, 441, 16):
        h = 14 if abs(x) < 150 else 24
        conifer(gn, g, x + rnd.uniform(-4, 4), 1288 + rnd.uniform(-3, 3), h, 4.5)
    # 3-4 open-grown meadow oaks, at least 60 ft apart
    for x, s in ((-80, 1105), (70, 1160), (-15, 1235), (120, 1060)):
        deciduous(g, gn, x, s, 55, 62, leaf="foliage_oak")
    # groves concealing the S-bend and flanking the entrance court
    for x, s in [(-80, 300), (-95, 340), (-70, 400), (-100, 450), (85, 330), (70, 380), (95, 430),
                 (60, 470), (-60, 250), (70, 270), (-150, 180), (140, 190), (-120, 470), (120, 480)]:
        mixed_tree(g, gn, x, s, rnd.uniform(0.8, 1.05))
    # east shoulder and west side hilltop specimens (well and septic kept clear)
    for x, s in [(200, 480), (260, 530), (320, 610), (-330, 520), (-340, 640), (-300, 720), (300, 730)]:
        mixed_tree(g, gn, x, s, rnd.uniform(0.8, 1.0))
    # Zen garden: small trees at the sides only (hornbeam, serviceberry, redbud, dogwood, witch hazel)
    for x, s in ((-66, 815), (-64, 840), (66, 820), (63, 848), (-60, 862), (60, 866)):
        deciduous(g, gn, x, s, rnd.uniform(18, 24), rnd.uniform(14, 18),
                  leaf=rnd.choice(["foliage_maple", "foliage_turning", "foliage_oak"]))
    # sycamores along the side creeks
    for side in (-1, 1):
        for s in (960, 1060, 1170):
            deciduous(g, gn, side * 132 + rnd.uniform(-10, 10), s, 70, 40, leaf="foliage_turning", bark="bark_sycamore")


# --------------------------------------------------------------------------
def meadow_tufts(gn):
    n = 0
    for x, s in scatter(-160, 160, 955, 1270, 9, jitter=0.5):
        px, ps, rx, rs = L.POOL
        if ((x - px) / rx) ** 2 + ((s - ps) / rs) ** 2 < 1.3:
            continue
        z = T(x, s)
        gn.tuft("meadow_tuft", x, s, z - 0.1, rnd.uniform(1.8, 3.2), rnd.uniform(0.8, 1.4), rng=rnd)
        n += 1
    for x, s in scatter(115, 325, 505, 715, 11, jitter=0.5):
        z = T(x, s)
        gn.tuft("meadow_tuft", x, s, z - 0.1, rnd.uniform(1.5, 2.6), rnd.uniform(0.8, 1.2), rng=rnd)
    return n


def zen_garden(g, gn, col):
    zy = T(0, 810) + 0.2
    # raked gravel in the upper yard, level loop path around it
    g.box("raked_gravel", -52, 52, 794, 836, zy - 0.3, zy + 0.03, skip=("bottom",))
    # fossil-limestone specimen stones from the excavation
    for x, s, r in ((-30, 806, 3.2), (-24, 812, 1.8), (18, 818, 2.6), (34, 802, 2.0), (4, 826, 1.6), (-8, 800, 1.2)):
        g.sphere("fieldstone", x, s, zy + r * 0.25, r, r * 0.8, r * 0.6, seg=8, rings=5)
    # stone-slab benches
    for x, s in ((-44, 840), (44, 840)):
        g.box("limestone_smooth", x - 4, x + 4, s - 1, s + 1, zy + 1.3, zy + 1.7)
        for dx in (-3, 3):
            g.box("limestone", x + dx - 0.5, x + dx + 0.5, s - 0.8, s + 0.8, zy - 0.2, zy + 1.3)
    # downspout stone basins feeding a winding 6-12 in river-stone brook to the basin
    path = [(-20, 786), (-16, 800), (-6, 812), (-10, 826), (2, 840), (12, 850), (6, 860), (0, 868)]
    from .site import smooth
    pts = smooth(path, 5)
    for k, (x, s) in enumerate(pts):
        for j in range(3):
            ox, os_ = rnd.uniform(-1.4, 1.4), rnd.uniform(-1.4, 1.4)
            z = T(x + ox, s + os_) + 0.05
            gn.sphere("river_stone", x + ox, s + os_, z, rnd.uniform(0.35, 0.7), rnd.uniform(0.3, 0.6), 0.22, seg=6, rings=3)
    for x in (-20, 20):
        g.box("limestone_smooth", x - 1.5, x + 1.5, 785.2, 788, T(x, 786) + 0.1, T(x, 786) + 1.3)
    # trickle reservoir at the foot (topped up from the cistern; solar pump)
    zr = T(0, 864)
    gn.cylinder("water", 0, 864, 5.5, zr - 0.25, zr - 0.15, seg=20)
    for k in range(14):
        a = 2 * math.pi * k / 14
        g.sphere("fieldstone", 6.2 * math.cos(a), 864 - 6.2 * math.sin(a), zr - 0.1, 1.1, 0.9, 0.55, seg=6, rings=3)
    g.box("pv", 7, 9, 862, 864, zr + 0.5, zr + 0.6)
    # basin plantings: sedges, blue flag iris, cardinal flower, swamp milkweed, buttonbush
    for x, s in scatter(-66, 66, 866, 890, 5, jitter=0.5):
        z = T(x, s)
        gn.tuft("sedge", x, s, z - 0.1, rnd.uniform(1.8, 3.2), rnd.uniform(0.7, 1.1), rng=rnd)
    zb = min(T(0, 877), T(20, 877), T(-20, 877))
    gn.box("water", -46, 46, 870, 884, zb + 0.35, zb + 0.4, skip=("bottom", "n", "s", "e", "w"))
    # low shielded path lights
    for k, (x, s) in enumerate(((-56, 800), (56, 800), (-56, 850), (56, 850))):
        g.cylinder("black_iron", x, s, 0.25, T(x, s), T(x, s) + 2.2, seg=6)
        I.light(col, f"PathLight_{k}", x, s, T(x, s) + 2.0, "garden", intensity=2, range_m=6)


def stone_arch(g):
    """Unlocked walk-through limestone arch in the south berm (the emergency exit)."""
    s0, s1 = 896.0, 910.0
    zf = T(0, 903) - 0.1
    r = 4.0
    zc = zf + 8.0 - r
    x_out, z_top = 11.0, T(0, 915) + 1.0
    z_top = max(z_top, zf + 11.0)
    for s, facing in ((s0, "n"), (s1, "s")):
        n = 12
        for i in range(n):
            a0, a1 = math.pi * i / n, math.pi * (i + 1) / n
            p0 = (r * math.cos(a0), zc + r * math.sin(a0))
            p1 = (r * math.cos(a1), zc + r * math.sin(a1))

            def outer(a):
                dx, dz = math.cos(a), math.sin(a)
                tx = x_out / abs(dx) if abs(dx) > 1e-6 else 1e9
                tz = (z_top - zc) / dz if dz > 1e-6 else 1e9
                t = min(tx, tz)
                return (dx * t, zc + dz * t)
            o0, o1 = outer(a0), outer(a1)
            quad = [(p0[0], s, p0[1]), (p1[0], s, p1[1]), (o1[0], s, o1[1]), (o0[0], s, o0[1])]
            g.face("limestone", quad if facing == "n" else quad[::-1])
            g.face("limestone", [(p1[0], s0, p1[1]), (p0[0], s0, p0[1]), (p0[0], s1, p0[1]), (p1[0], s1, p1[1])][::-1])
        for x, rev in ((-x_out, False), (x_out, True)):
            pass
        # jambs below the springing line
        for sx in (-1, 1):
            q = [(sx * r, s, zf), (sx * x_out, s, zf), (sx * x_out, s, zc), (sx * r, s, zc)]
            if (sx > 0) == (facing == "n"):
                q = q[::-1]
            g.face("limestone", q)
    for sx in (-1, 1):
        q = [(sx * r, s0, zf), (sx * r, s1, zf), (sx * r, s1, zc), (sx * r, s0, zc)]
        g.face("limestone", q if sx > 0 else q[::-1])
    g.box("limestone", -x_out, x_out, s0, s1, z_top, z_top + 0.01, skip=("bottom",)) if False else None
    g.face("limestone", [(-x_out, s1, z_top), (x_out, s1, z_top), (x_out, s0, z_top), (-x_out, s0, z_top)])
    for sx in (-1, 1):
        q = [(sx * x_out, s0, zf), (sx * x_out, s1, zf), (sx * x_out, s1, z_top), (sx * x_out, s0, z_top)]
        g.face("limestone", q if sx > 0 else q[::-1])
    g.box("limestone_smooth", -1.0, 1.0, s0 - 0.2, s1 + 0.2, zc + r - 0.2, zc + r + 1.2)  # keystone
    g.box("cobble", -r, r, s0 - 2, s1 + 6, zf - 0.3, zf + 0.05, skip=("bottom",))
    # armored spillway beside the arch (fieldstone)
    for k in range(10):
        x = 14 + k * 1.8
        g.sphere("fieldstone", x, 915 + rnd.uniform(-2, 2), T(x, 915) + 0.2, 1.2, 1.0, 0.5, seg=6, rings=3)


def creeks_and_outfalls(g, gn):
    # step-pool side creeks with limestone check dams (drop / slope spacing)
    for side in (-1, 1):
        x = side * 125
        s = 800
        while s < 1270:
            z = T(x, s)
            g.box("limestone_smooth", x - 4, x + 4, s, s + 1.2, z - 0.4, z + 0.9)
            gn.box("water", x - 3, x + 3, s + 1.2, s + 12, T(x, s + 6) + 0.05, T(x, s + 6) + 0.1,
                   skip=("bottom", "n", "s", "e", "w"))
            for j in range(4):
                ss = s + 2 + j * 2.6
                gn.sphere("river_stone", x + rnd.uniform(-4, 4), ss, T(x, ss) + 0.1, 0.8, 0.6, 0.3, seg=6, rings=3)
            s += 17.0
    # clean spreader: 80-ft level stone lip mid-slope
    zs = T(0, 960)
    g.box("limestone_smooth", -40, 40, 958.5, 961.5, zs - 1.2, zs + 0.35)
    # seasonal pool (fishless) in its dish
    px, ps, rx, rs = L.POOL
    zp = L.pool_level() - 0.35
    for i in range(24):
        a0, a1 = 2 * math.pi * i / 24, 2 * math.pi * (i + 1) / 24
        gn.face("water", [(px, ps, zp), (px + rx * 0.97 * math.cos(a0), ps - rs * 0.97 * math.sin(a0), zp),
                          (px + rx * 0.97 * math.cos(a1), ps - rs * 0.97 * math.sin(a1), zp)])
    # working spreader at the SW woods edge with a vegetated filter strip
    zw = T(-185, 930)
    g.box("limestone_smooth", -210, -160, 929, 931.5, zw - 1.0, zw + 0.35)


def build(col, g, gn):
    trees(g, gn)
    meadow_tufts(gn)
    zen_garden(g, gn, col)
    stone_arch(g)
    creeks_and_outfalls(g, gn)
