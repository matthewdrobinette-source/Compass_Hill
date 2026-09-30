"""Motor court, pavilion on the cistern, pads, covered walk, and the tunnels."""

import math

from . import interact as I
from . import layout as L
from .common import Geo, empty
from .site import rect, rot_rect

CX, CS = L.COURT_C
ZF, ZC = -11.0, -2.0  # tunnel floor and ceiling


def polar(r, ang_deg, cx=CX, cs=CS):
    a = math.radians(ang_deg)
    return cx + r * math.cos(a), cs - r * math.sin(a)


def annulus(g, mat, r0, r1, z0, z1, a0=0, a1=360, seg=48, faces=("top", "bottom", "inner", "outer"), cx=CX, cs=CS):
    """Annular prism between radii r0<r1, angles a0..a1 (deg, CCW from east)."""
    n = max(2, int(seg * (a1 - a0) / 360))
    for i in range(n):
        t0 = a0 + (a1 - a0) * i / n
        t1 = a0 + (a1 - a0) * (i + 1) / n
        p = lambda r, t, z: (*polar(r, t, cx, cs), z)
        if "top" in faces:
            g.face(mat, [p(r0, t0, z1), p(r1, t0, z1), p(r1, t1, z1), p(r0, t1, z1)])
        if "bottom" in faces:
            g.face(mat, [p(r0, t1, z0), p(r1, t1, z0), p(r1, t0, z0), p(r0, t0, z0)])
        if "outer" in faces:
            g.face(mat, [p(r1, t0, z0), p(r1, t1, z0), p(r1, t1, z1), p(r1, t0, z1)])
        if "inner" in faces:
            g.face(mat, [p(r0, t1, z0), p(r0, t0, z0), p(r0, t0, z1), p(r0, t1, z1)])


def gaps_to_spans(gaps, a0=-180, a1=180):
    """Angles not covered by gaps [(start, end), ...]."""
    gaps = sorted(gaps)
    spans, cur = [], a0
    for g0, g1 in gaps:
        if g0 > cur:
            spans.append((cur, g0))
        cur = max(cur, g1)
    if cur < a1:
        spans.append((cur, a1))
    return spans


PADS = [0, 45, 90, 135, 180, -135, -45]      # spokes; south (-90) left open
EXITS = [-22.5, -157.5]                       # exit stairs between pads (east & west)


def half_angle(width, r):
    return math.degrees(math.asin(width / 2 / r))


# --------------------------------------------------------------------------
def cistern_and_loop(g, gn, col):
    # tank: 40 ft across (reaches under all eight posts), shallow, below the court
    g.cylinder("concrete", CX, CS, 20.0, -9.6, -9.5, seg=48)
    annulus(g, "tunnel_wall", 0, 20.0, -1.0, -0.4, faces=("bottom",))
    g.cylinder("concrete", CX, CS, 20.0, -9.5, -1.0, seg=48, caps=False, inward=True)
    water = Geo()
    annulus(water, "water", 0, 19.9, -5.2, -5.0, faces=("top",))
    gn.merge(water)
    # loop: floor, ceiling, inner (tank) wall, outer wall with openings
    annulus(g, "concrete", 21.0, 31.0, ZF - 1, ZF, faces=("top",))
    annulus(g, "tunnel_wall", 21.0, 31.0, ZC, ZC + 1, faces=("bottom",))
    annulus(g, "tunnel_wall", 20.0, 21.0, ZF, ZC, faces=("outer",))
    # flexible joint line between tank and loop (black strip at the ceiling/floor)
    annulus(gn, "black_iron", 21.0, 21.25, ZF, ZF + 0.02, faces=("top",))
    gaps = [(-90 - half_angle(10, 31), -90 + half_angle(10, 31)), (90 - half_angle(10, 31), 90 + half_angle(10, 31))]
    for e in EXITS:
        h = half_angle(5.2, 31)
        gaps.append((e - h, e + h))
    for a0, a1 in gaps_to_spans([((x + 180) % 360 - 180, (y + 180) % 360 - 180) for x, y in gaps]):
        annulus(g, "tunnel_wall", 31.0, 32.0, ZF, ZC, a0, a1, faces=("inner", "top"))
    # pipes low on the inner (tank-side) wall... water low on one wall, power high on the other
    for r, z0, mat in ((21.3, ZF + 0.8, "pipe_purple"), (21.3, ZF + 1.6, "pipe_red"), (21.3, ZF + 2.4, "pipe_blue")):
        annulus(gn, mat, r, r + 0.4, z0, z0 + 0.4, faces=("top", "bottom", "outer"))
    for a0, a1 in gaps_to_spans([((x + 180) % 360 - 180, (y + 180) % 360 - 180) for x, y in gaps]):
        annulus(gn, "cable_tray", 30.2, 31.0, ZC - 1.2, ZC - 1.0, a0, a1, faces=("top", "bottom", "inner"))
        annulus(gn, "cable_tray", 30.2, 31.0, ZC - 0.6, ZC - 0.4, a0, a1, faces=("top", "bottom", "inner"))
    # valves on the loop side of every tank pipe
    labels = ["inlet valve", "outlet valve", "overflow valve", "pump suction valve", "fire-hydrant valve",
              "second inlet valve"]
    for k, ang in enumerate((-60, -120, 30, 150, 60, 120)):
        x, s = polar(21.0, ang)
        ux, us = math.cos(math.radians(ang)), -math.sin(math.radians(ang))
        g.cylinder("pipe_gray", x + ux * 0.6, s + us * 0.6, 0.35, ZF, ZF + 4.2, seg=10)
        v = Geo()
        # hand wheel (spins)
        v.cylinder("pipe_red", 0, 0, 0.9, -0.08, 0.08, seg=14, caps=True)
        v.cylinder("black_iron", 0, 0, 0.2, -0.15, 0.15, seg=8)
        vo = v.to_object(f"CisternValve_{k}", col, local_at=(x + ux * 0.6, s + us * 0.6, ZF + 4.4),
                         props={"interact": "spin", "axis": "z", "label": f"turn the {labels[k]}", "collide": 0})
    # level gauge (sensor) near the south junction
    x, s = polar(21.0, -75)
    g.box("stainless", x - 0.3, x + 0.3, s - 0.1, s + 0.1, ZF + 3, ZF + 7)
    # side hatch into the tank (above the water line) with a steel platform
    hx, hs = polar(21.0, 180)
    g.box("safety_yellow", hx + 0.1, hx + 4.0, hs - 2.5, hs + 2.5, ZF, -5.6)
    for i in range(1, 9):
        g.box("black_iron", hx + 4.0 + (8 - i) * 0.9, hx + 4.9 + (8 - i) * 0.9, hs - 1.5, hs + 1.5, ZF + i * 0.6 - 0.2, ZF + i * 0.6)
    for k in range(6):
        g.box("black_iron", hx - 0.6, hx - 0.5, hs - 1.2 + k * 0.5, hs - 1.15 + k * 0.5, -5.5, -3.0)  # grate bars
    hd = Geo()
    hd.box("stainless", -0.1, 0.1, 0, 2.6, 0, 2.4)
    I.hinged_door_s(col, "CisternHatch", hx + 0.25, hs - 1.3, -5.5, 2.6, +1, opens_east=True,
                    label="cistern side hatch", mat="stainless", height=2.4, thick=0.2)
    # chimney buttress (the loop carries the pavilion chimney) + ash-pit cleanout door
    x, s = polar(31.0, 90)
    g.box("fieldstone", x - 3, x + 3, s - 0.5, s + 0.2, ZF, ZC)
    I.hinged_door_x(col, "AshPitDoor", x - 1.0, s + 0.25, ZF + 2.0, 2.0, +1, opens_south=True,
                    label="ash-pit cleanout", mat="black_iron", height=1.6, thick=0.12)
    # loop lights
    for k in range(8):
        ang = k * 45 + 22.5
        x, s = polar(26, ang)
        lamp = Geo()
        lamp.box("lamp_warm", -0.8, 0.8, -0.3, 0.3, 0, 0.12)
        lamp.to_object(f"LoopLamp_{k}", col, local_at=(x, s, ZC - 0.15), props={"lamp_group": "tunnels"})
        I.light(col, f"LoopLight_{k}", x, s, ZC - 1.0, "tunnels", intensity=6, color="#fff1d6", range_m=10)


def tunnel_room(g, gn, x0, x1, s0, s1, openings, pipes=None):
    """Rectangular tunnel/chamber: floor, ceiling, walls with full-height openings.
    openings: {'n': [(a0, a1)], 's': [...], 'e': [...], 'w': [...]} along X for n/s, S for e/w."""
    g.box("concrete", x0, x1, s0, s1, ZF - 1, ZF, skip=("n", "s", "e", "w", "bottom"))
    g.box("tunnel_wall", x0, x1, s0, s1, ZC, ZC + 1, skip=("n", "s", "e", "w", "top"))
    op = lambda k: [(a, b, ZF, ZC) for a, b in openings.get(k, [])]
    from .common import wall_s, wall_x
    wall_x(g, "tunnel_wall", x0 - 1, x1 + 1, s0 - 1, s0, ZF, ZC, op("n"))
    wall_x(g, "tunnel_wall", x0 - 1, x1 + 1, s1, s1 + 1, ZF, ZC, op("s"))
    wall_s(g, "tunnel_wall", s0, s1, x0 - 1, x0, ZF, ZC, op("w"))
    wall_s(g, "tunnel_wall", s0, s1, x1, x1 + 1, ZF, ZC, op("e"))
    # safety stripe at the floor edges
    for xa, xb, sa, sb in ((x0, x1, s0, s0 + 0.25), (x0, x1, s1 - 0.25, s1)):
        gn.box("safety_yellow", xa, xb, sa, sb, ZF, ZF + 0.02)


def tunnel_pipes_x(gn, x0, x1, s_wall_low, s_wall_high):
    """Water low on one wall, power and data high on the other (runs east-west)."""
    d = 1 if s_wall_low < s_wall_high else -1
    for k, mat in enumerate(("pipe_blue", "pipe_purple", "pipe_red", "pipe_gray")):
        s = s_wall_low + d * (0.3 + 0.05)
        gn.box(mat, x0, x1, s - 0.2, s + 0.2, ZF + 0.6 + k * 0.7, ZF + 1.0 + k * 0.7)
    for k in range(2):
        s = s_wall_high - d * 0.5
        gn.box("cable_tray", x0, x1, s - 0.4, s + 0.4, ZC - 1.3 + k * 0.6, ZC - 1.2 + k * 0.6)


def tunnel_pipes_s(gn, s0, s1, x_wall_low, x_wall_high):
    d = 1 if x_wall_low < x_wall_high else -1
    for k, mat in enumerate(("pipe_blue", "pipe_purple", "pipe_red", "pipe_gray")):
        x = x_wall_low + d * 0.35
        gn.box(mat, x - 0.2, x + 0.2, s0, s1, ZF + 0.6 + k * 0.7, ZF + 1.0 + k * 0.7)
    for k in range(2):
        x = x_wall_high - d * 0.5
        gn.box("cable_tray", x - 0.4, x + 0.4, s0, s1, ZC - 1.3 + k * 0.6, ZC - 1.2 + k * 0.6)


def tunnel_light(col, name, X, S):
    lamp = Geo()
    lamp.box("lamp_warm", -0.3, 0.3, -1.2, 1.2, 0, 0.12)
    lamp.to_object(name, col, local_at=(X, S, ZC - 0.15), props={"lamp_group": "tunnels"})
    I.light(col, name + "_light", X, S, ZC - 1.0, "tunnels", intensity=6, color="#fff1d6", range_m=10)


def tunnels(g, gn, col):
    # South loop junction chamber, main tunnel, forecourt junction, cart bay
    tunnel_room(g, gn, -12, 12, 623.5, 647, {"n": [(-5, 5)], "s": [(-5, 5)]})
    tunnel_room(g, gn, -5, 5, 647, 668, {"n": [(-5, 5)], "s": [(-5, 5)]})
    tunnel_room(g, gn, -12, 12, 668, 692, {"n": [(-5, 5)], "s": [(-5, 5)], "w": [(675, 685)]})
    tunnel_room(g, gn, -5, 5, 692, 712, {"n": [(-5, 5)], "s": [(-5, 5)]})
    tunnel_room(g, gn, -12, 12, 712, 735.0, {"n": [(-5, 5)], "s": [(-2, 2)]})
    tunnel_pipes_s(gn, 647, 668, -5, 5)
    tunnel_pipes_s(gn, 692, 712, -5, 5)
    # North loop junction and the sealed stub toward the gate (future gate tunnel)
    tunnel_room(g, gn, -12, 12, 535, 558.5, {"s": [(-5, 5)], "n": [(-5, 5)]})
    tunnel_room(g, gn, -5, 5, 520, 535, {"s": [(-5, 5)]})
    g.box("safety_yellow", -4.5, 4.5, 520.0, 520.3, ZF, ZF + 0.5)
    sign = Geo()
    sign.box("sign_green", -2.5, 2.5, 0, 0.1, 0, 1.2)
    sign.to_object("GateStubSign", col, local_at=(0, 520.2, ZF + 5.0), props={"lamp_group": "tunnels"})
    # Garage tunnel (west) with a pull-out halfway, garage lobby, inverter room
    tunnel_room(g, gn, -154, -12, 675, 685, {"e": [(675, 685)], "w": [(675, 685)], "s": [(-92, -72)]})
    tunnel_room(g, gn, -92, -72, 685, 693, {"n": [(-92, -72)]})
    tunnel_pipes_x(gn, -154, -12, 675, 685)
    tunnel_room(g, gn, -178, -154, 668, 692, {"e": [(675, 685)], "w": [(675, 685)], "n": [(-168, -164)]})
    tunnel_room(g, gn, -178, -154, 648, 667, {"s": [(-168, -164)]})
    I.hinged_door_x(col, "InverterRoomDoor", -168, 667.5, ZF, 4, +1, opens_south=False, label="inverter room",
                    mat="stainless")
    # inverters and panels (serviced from the tunnel; the vault doors never open here)
    for k in range(6):
        x = -176 + k * 3.6
        g.box("steel_shelf", x, x + 2.8, 648.2, 649.6, ZF, ZF + 6.2)
        g.box("sign_green", x + 0.3, x + 0.8, 649.6, 649.65, ZF + 5.0, ZF + 5.3)
    g.box("steel_shelf", -177.5, -176.2, 652, 664, ZF, ZF + 7.0)
    # tunnel lights
    for s in (635, 657, 680, 702, 724, 546, 527):
        tunnel_light(col, f"TunnelLamp_{s}", 0, s)
    for x in (-30, -55, -82, -110, -135, -166):
        tunnel_light(col, f"TunnelLamp_w{-x}", x, 680)
    tunnel_light(col, "TunnelLamp_inv", -166, 658)
    # house cart bay: a charging golf cart waits by the house door
    for name, label in (("tunnels", "tunnel lights"),):
        I.switch(col, "Switch_tunnels_bay", -3.6, 734.6, ZF + 3.8, "tunnels", "tunnel lights")
        I.switch(col, "Switch_tunnels_garage", -155.2, 690, ZF + 3.8, "tunnels", "tunnel lights", facing="e")


def exit_stairs(g, gn, col):
    """Two exit stairs rise from the loop between pads on the east and west sides,
    each under a small limestone head-house with a slate hip roof."""
    holes = []
    for k, ang in enumerate(EXITS):
        loc = Geo()
        n, r = 18, 11.0 / 18
        # local frame: +X runs radially outward from the loop wall (u), S across (v)
        for i in range(1, n + 1):
            top = ZF + i * r
            u0 = 1.0 + (i - 1) * 0.9167
            loc.box("limestone_smooth", u0, u0 + 0.9167, -2.2, 2.2, top - 1.0, top)
        loc.box("limestone_smooth", 17.5, 20.5, -2.2, 2.2, -1.0, 0.0)   # top landing
        loc.box("concrete", -0.5, 1.0, -2.2, 2.2, ZF - 1, ZF)
        for v0, v1 in ((-3.2, -2.2), (2.2, 3.2)):
            loc.box("tunnel_wall", -0.5, 21.3, v0, v1, ZF, 0.0)       # below-grade walls
            loc.box("limestone", 3.0, 21.3, v0, v1, 0.0, 8.5)         # head-house walls
            loc.box("oak", 1.5, 19.5, v0 + (0.8 if v0 > 0 else 0.2), v0 + (0.8 if v0 > 0 else 0.2) + 0.2 if False else v1, ZF + 3.0, ZF + 3.0) if False else None
        loc.box("tunnel_wall", -0.5, 3.0, -3.2, 3.2, ZC, 0.0)          # roof over the lower flight
        from .common import wall_s
        wall_s(loc, "limestone", -3.2, 3.2, 20.5, 21.3, 0.0, 8.5, [(-1.6, 1.6, 0.0, 7.0)])
        wall_s(loc, "limestone", -3.2, 3.2, 3.0, 3.8, -2.0, 8.5)
        # hip roof (slate)
        for pts in (((2.5, -3.8), (21.8, -3.8), (18.8, 0), (5.5, 0)), ((21.8, 3.8), (2.5, 3.8), (5.5, 0), (18.8, 0))):
            loc.face("slate", [(pts[0][0], pts[0][1], 8.5), (pts[1][0], pts[1][1], 8.5), (pts[2][0], pts[2][1], 11.3), (pts[3][0], pts[3][1], 11.3)][::-1])
        loc.face("slate", [(2.5, -3.8, 8.5), (5.5, 0, 11.3), (2.5, 3.8, 8.5)][::-1])
        loc.face("slate", [(21.8, 3.8, 8.5), (18.8, 0, 11.3), (21.8, -3.8, 8.5)][::-1])
        loc.box("plaster_ceiling", 3.8, 20.5, -2.2, 2.2, 8.3, 8.5, skip=("top",))
        # handrail
        loc.box("black_iron", 1.0, 17.5, -2.1, -2.0, ZF + 3.0, 3.0) if False else None
        x, s = polar(31.5, ang)
        loc.to_object(f"ExitStair_{k}", col, local_at=(x, s, 0.0), rot_deg=ang, props={"collide": 1})
        # door at the top (local u = 20.9), hinged
        u, v = 20.9, -1.6
        a = math.radians(ang)
        hx = x + u * math.cos(a) - v * -math.sin(a) * 0 + (-v) * math.sin(a) * 0
        # compute hinge point in site coords: local (u, v) -> site (X, S) with rotation ang (CCW from east)
        ux, us = math.cos(a), -math.sin(a)
        vx, vs = math.sin(a), math.cos(a)
        hx, hs = x + u * ux + v * vx, s + u * us + v * vs
        d = Geo()
        d.box("oak", -0.1, 0.1, 0, 3.2, 0, 7.0)
        d.sphere("bronze_ss", 0.25, 2.9, 3.2, 0.12, seg=8, rings=4)
        d.sphere("bronze_ss", -0.25, 2.9, 3.2, 0.12, seg=8, rings=4)
        d.to_object(f"ExitStairDoor_{k}", col, local_at=(hx, hs, 0.0), rot_deg=ang,
                    props={"interact": "rotate", "axis": "z", "angle": 95, "label": "exit stair door", "collide": 1})
        lamp = Geo()
        lamp.box("lamp_warm", -0.5, 0.5, -0.5, 0.5, 0, 0.1)
        cx_, cs_ = x + 12 * ux, s + 12 * us
        lamp.to_object(f"ExitStairLamp_{k}", col, local_at=(cx_, cs_, 8.2), props={"lamp_group": "tunnels"})
        I.light(col, f"ExitStairLight_{k}", cx_, cs_, 6.0, "tunnels", intensity=5, range_m=9)
        cx2, cs2 = x + 9 * ux, s + 9 * us
        I.light(col, f"ExitStairLightLow_{k}", cx2, cs2, -4.0, "tunnels", intensity=5, range_m=9)
        holes.append(rot_rect(x + 12.0 * ux, s + 12.0 * us, 18.6, 6.0, ang))
    return holes


# --------------------------------------------------------------------------
def pavilion(g, gn, col):
    # raised limestone floor over the cistern roof
    annulus(g, "limestone_smooth", 0, 22.0, -0.4, 0.6, faces=("top", "outer"))
    annulus(g, "limestone_smooth", 22.0, 23.5, -0.4, 0.25, faces=("top", "outer"))
    # compass-rose hatch at the center, aimed at the front door (stainless inlay)
    hatch = Geo()
    hatch.cylinder("limestone_smooth", 0, 0, 2.0, -0.12, 0.0, seg=24)
    for k in range(8):
        a = math.radians(k * 45 - 90)
        L_ = 1.9 if k % 2 == 0 else 1.1
        tip = (L_ * math.cos(a), -L_ * math.sin(a), 0.02)
        l = (0.25 * math.cos(a + math.pi / 2), -0.25 * math.sin(a + math.pi / 2), 0.02)
        r = (0.25 * math.cos(a - math.pi / 2), -0.25 * math.sin(a - math.pi / 2), 0.02)
        hatch.face("bronze_ss", [l, (0, 0, 0.02), r, tip][::-1] if True else [])
    hatch.to_object("CompassRoseHatch", col, local_at=(CX, CS - 2.0, 0.6),
                    props={"interact": "rotate", "axis": "x", "angle": -105, "label": "compass-rose hatch",
                           "collide": 0})
    # shaft under the hatch down to the water
    gn.box("concrete", CX - 2.0, CX + 2.0, CS - 2.0, CS + 2.0, -5.0, -0.4, skip=("top",)) if False else None
    # eight site-grown white oak posts on stone bases, aligned with the spokes
    for k in range(8):
        x, s = polar(L.PAVILION_POST_R, k * 45)
        g.box("limestone_smooth", x - 1.1, x + 1.1, s - 1.1, s + 1.1, 0.6, 1.8)
        g.box("oak_timber", x - 0.65, x + 0.65, s - 0.65, s + 0.65, 1.8, 12.0)
        # knee braces
        x2, s2 = polar(L.PAVILION_POST_R - 2.5, k * 45)
        g.box("oak_timber", min(x, x2) - 0.3, max(x, x2) + 0.3, min(s, s2) - 0.3, max(s, s2) + 0.3, 10.2, 10.8)
    # octagonal ring beam
    for k in range(8):
        x0, s0 = polar(L.PAVILION_POST_R, k * 45)
        x1, s1 = polar(L.PAVILION_POST_R, (k + 1) * 45)
        gpts = []
        for rr in (L.PAVILION_POST_R - 0.6, L.PAVILION_POST_R + 0.6):
            pass
        annulus(g, "oak_timber", L.PAVILION_POST_R - 0.7, L.PAVILION_POST_R + 0.7, 12.0, 13.4, k * 45, (k + 1) * 45, seg=8)
    # slate cone roof (9:12) with an oak ceiling, glass lantern, stainless finial
    r_eave, z_eave = 25.0, 13.0
    slope = 9 / 12
    r_top = 3.0
    z_top = z_eave + (r_eave - r_top) * slope
    seg = 32
    for i in range(seg):
        a0, a1 = 360 * i / seg, 360 * (i + 1) / seg
        p = lambda r, a, z: (*polar(r, a), z)
        g.face("slate", [p(r_eave, a0, z_eave), p(r_eave, a1, z_eave), p(r_top, a1, z_top), p(r_top, a0, z_top)])
        g.face("oak", [p(r_top, a0, z_top - 0.6), p(r_top, a1, z_top - 0.6), p(r_eave, a1, z_eave - 0.6), p(r_eave, a0, z_eave - 0.6)])
        g.face("oak", [p(r_eave, a1, z_eave - 0.6), p(r_eave, a0, z_eave - 0.6), p(r_eave, a0, z_eave), p(r_eave, a1, z_eave)][::-1])
    annulus(g, "stainless", r_eave, r_eave + 0.5, z_eave - 0.8, z_eave - 0.4, faces=("top", "outer", "bottom", "inner"))
    g.cylinder("glass", CX, CS, r_top, z_top, z_top + 3.0, seg=16, caps=False)
    for k in range(8):
        x, s = polar(r_top, k * 45)
        g.box("bronze_frame", x - 0.12, x + 0.12, s - 0.12, s + 0.12, z_top, z_top + 3.0)
    g.cone("slate", CX, CS, r_top + 0.8, z_top + 3.0, z_top + 5.4, seg=16)
    g.sphere("bronze_ss", CX, CS, z_top + 5.8, 0.45, seg=10, rings=6)
    g.cone("bronze_ss", CX, CS, 0.15, z_top + 6.1, z_top + 8.2, seg=8)
    # stone fireplace on the north side, chimney carried by the loop below
    x, s = polar(24.5, 90)
    g.box("fieldstone", x - 4.0, x + 4.0, s - 2.5, s + 2.5, 0.6, 8.5)
    g.box("fieldstone", x - 2.2, x + 2.2, s - 1.8, s + 1.8, 8.5, z_eave + (r_eave - 26.5) * slope + 12.0)
    g.box("limestone_smooth", x - 2.5, x + 2.5, s - 2.1, s + 2.1, 25.2, 25.8)
    g.box("black_iron", x - 1.6, x + 1.6, s + 2.4, s + 2.5, 1.6, 4.4)
    g.box("ember", x - 1.5, x + 1.5, s + 1.0, s + 2.4, 0.6, 0.7)
    g.box("limestone_smooth", x - 4.4, x + 4.4, s + 2.5, s + 4.0, 0.6, 1.4)  # hearth bench
    g.box("oak", x - 4.6, x + 4.6, s - 2.7, s + 2.7, 5.5, 5.9)  # mantel
    fire = Geo()
    for k, (dx, h) in enumerate(((0, 2.0), (0.7, 1.5), (-0.7, 1.4), (0.3, 1.2), (-0.3, 1.1))):
        fire.cone("flame", dx, 0, 0.55, 0, h, seg=6)
    fire.to_object("PavilionFire", col, local_at=(x, s + 1.7, 0.7), props={"flame_group": "pavilion"})
    ctl = Geo()
    ctl.box("black_iron", -0.3, 0.3, -0.05, 0.05, 0, 0.6)
    ctl.to_object("PavilionFireCtl", col, local_at=(x + 3.0, s + 2.55, 3.0),
                  props={"interact": "fire", "group": "pavilion", "label": "light the fireplace"})
    I.light(col, "PavilionFire_light", x, s + 3.5, 2.5, "fire_pavilion", intensity=10, color="#ff8a3c",
            range_m=10, on=0)
    # outdoor kitchen on the east side, long oak table, benches
    g.box("limestone_smooth", CX + 12.5, CX + 15.0, CS - 7, CS + 7, 0.6, 3.6)
    g.box("soapstone", CX + 12.3, CX + 15.2, CS - 7.2, CS + 7.2, 3.6, 3.8)
    g.box("stainless", CX + 13.0, CX + 14.6, CS - 2, CS + 2, 3.8, 4.0)
    g.box("oak", CX - 3, CX + 3, CS - 9, CS + 5, 3.0, 3.3)
    for dx in (-2.6, 2.6):
        g.box("oak", CX + dx - 0.25, CX + dx + 0.25, CS - 8.5, CS + 4.5, 0.6, 3.0)
    for dx in (-5.0, 5.0):
        g.box("oak", CX + dx - 0.8, CX + dx + 0.8, CS - 9, CS + 5, 2.0, 2.3)
        g.box("oak", CX + dx - 0.2, CX + dx + 0.2, CS - 8.5, CS + 4.5, 0.6, 2.0)
    # retractable screens on the west side (rolled up), warm pendant lights
    for k in (157.5, 180, 202.5):
        x, s = polar(19.5, k)
        gn.cylinder("canvas_blue", x, s, 0.4, 11.0, 11.8, seg=8)
    for k in range(4):
        x, s = polar(10, k * 90 + 45)
        I.pendant(col, gn, f"PavilionLamp_{k}", x, s, z_eave + 4.0, 4.5, "pavilion", shade=1.3, kind="lantern",
                  intensity=10, range_m=12)
    sw = Geo()
    sw.box("bronze_ss", -0.05, 0.05, -0.2, 0.2, -0.3, 0.3)
    x, s = polar(L.PAVILION_POST_R - 0.7, -45)
    sw.to_object("Switch_pavilion", col, local_at=(x, s, 4.5),
                 props={"interact": "switch", "group": "pavilion", "label": "pavilion lights"})
    # stone-lined drip ring piped to the cistern
    annulus(gn, "river_stone", 25.0, 27.0, -0.2, 0.05, faces=("top",))


def pads(g, gn, col):
    """Seven covered two-car pads on the spokes; hipped S1 slate on white-oak frames."""
    for k, ang in enumerate(PADS):
        loc = Geo()
        w = 18.0
        loc.box("aggregate", 32.0, 51.0, -w / 2, w / 2, 0.0, 0.05, skip=("bottom",))
        for u in (32.6, 50.4):
            for v in (-w / 2 + 0.6, w / 2 - 0.6):
                loc.box("limestone_smooth", u - 0.8, u + 0.8, v - 0.8, v + 0.8, 0.0, 1.5)
                loc.box("oak_timber", u - 0.45, u + 0.45, v - 0.45, v + 0.45, 1.5, 9.0)
                loc.box("black_iron", u - 0.2, u + 0.2, v - 0.2, v + 0.2, 0.0, 3.0)
        for v in (-w / 2 + 0.6, w / 2 - 0.6):
            loc.box("oak_timber", 32.0, 51.0, v - 0.45, v + 0.45, 9.0, 10.0)
        for u in (32.6, 50.4):
            loc.box("oak_timber", u - 0.45, u + 0.45, -w / 2, w / 2, 9.0, 10.0)
        # hipped roof: 8:12
        e = 1.5
        u0, u1, v0, v1 = 32.0 - e, 51.0 + e, -w / 2 - e, w / 2 + e
        hh = (v1 - v0) / 2 * 8 / 12
        zr = 10.0 + hh
        uc0, uc1 = u0 + (v1 - v0) / 2, u1 - (v1 - v0) / 2
        loc.face("slate", [(u0, v1, 10.0), (u1, v1, 10.0), (uc1, 0, zr), (uc0, 0, zr)][::-1])
        loc.face("slate", [(u1, v0, 10.0), (u0, v0, 10.0), (uc0, 0, zr), (uc1, 0, zr)][::-1])
        loc.face("slate", [(u0, v0, 10.0), (u0, v1, 10.0), (uc0, 0, zr)][::-1])
        loc.face("slate", [(u1, v1, 10.0), (u1, v0, 10.0), (uc1, 0, zr)][::-1])
        loc.face("oak", [(u0, v0, 9.95), (u1, v0, 9.95), (u1, v1, 9.95), (u0, v1, 9.95)][::-1])
        loc.box("rubber", 34.0, 34.4, -7.5, -1.5, 0.05, 0.4)
        loc.box("rubber", 34.0, 34.4, 1.5, 7.5, 0.05, 0.4)
        x, s = CX, CS
        loc.to_object(f"Pad_{k}", col, local_at=(x, s, 0.0), rot_deg=ang, props={"collide": 1})
    return


def covered_walk(g, gn, col):
    """Covered walk along the axis from the pavilion to the porte-cochere."""
    g.box("cobble", -4, 4, 616, 709, -0.2, 0.08, skip=("bottom",))
    s_posts = [620, 632, 640] + [668, 680, 692, 704]
    for s in s_posts:
        for x in (-6.3, 6.3):
            g.box("limestone_smooth", x - 0.8, x + 0.8, s - 0.8, s + 0.8, 0.0, 1.2)
            g.box("oak_timber", x - 0.5, x + 0.5, s - 0.5, s + 0.5, 1.2, 14.0)
            g.box("black_iron", x - 0.25, x + 0.25, s - 0.25, s + 0.25, -0.5, 4.0)  # steel core stops a car
    for x in (-6.3, 6.3):
        g.box("oak_timber", x - 0.5, x + 0.5, 618, 709, 14.0, 15.2)
    zr = 15.2 + 7 * 8 / 12
    g.face("slate", [(-7, 709, 15.2), (-7, 618, 15.2), (0, 618, zr), (0, 709, zr)][::-1])
    g.face("slate", [(7, 618, 15.2), (7, 709, 15.2), (0, 709, zr), (0, 618, zr)][::-1])
    g.face("plaster_ceiling", [(-6.8, 618, 14.9), (6.8, 618, 14.9), (6.8, 709, 14.9), (-6.8, 709, 14.9)])
    g.face("oak_siding", [(-7, 618, 15.2), (7, 618, 15.2), (0, 618, zr)])
    for k, s in enumerate(range(624, 708, 12)):
        lamp = Geo()
        lamp.box("lamp_warm", -1.2, 1.2, -0.4, 0.4, 0, 0.1)
        lamp.to_object(f"WalkLamp_{k}", col, local_at=(0, s, 14.75), props={"lamp_group": "covered_walk"})
        if k % 2 == 0:
            I.light(col, f"WalkLight_{k}", 0, s, 13.5, "covered_walk", intensity=5, range_m=10)


def build(col, g, gn):
    cistern_and_loop(g, gn, col)
    tunnels(g, gn, col)
    holes = exit_stairs(g, gn, col)
    pavilion(g, gn, col)
    pads(g, gn, col)
    covered_walk(g, gn, col)
    return holes
