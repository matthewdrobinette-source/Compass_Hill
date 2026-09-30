"""The house: 120 x 48 ft, three levels (walkout -11, main 0, second +11)."""

import math

from . import interact as I
from . import layout as L
from .common import FT, Geo, empty, slab, wall_s, wall_x

XW, XE = L.HOUSE_X
SN, SS = L.HOUSE_S
LEVELS = {"walkout": -11.0, "main": 0.0, "second": 11.0}
CEIL = {"walkout": 10.0, "main": 10.0, "second": 9.0}
RISE = 11.0
NR = 18
R = RISE / NR           # riser
TD = 11.0 / 12.0        # tread
S_HALL = 751.0
S_LAND = 751.0 - 8 * TD  # 743.67


# --------------------------------------------------------------------------
def window_x(g, x0, x1, s_mid, z0, z1, depth=0.5, stone=True, lintel_side=None):
    n = max(1, round((x1 - x0) / 3.5))
    fr = 0.22
    g.box("bronze_frame", x0, x1, s_mid - depth / 2, s_mid + depth / 2, z0, z0 + fr)
    g.box("bronze_frame", x0, x1, s_mid - depth / 2, s_mid + depth / 2, z1 - fr, z1)
    for k in range(n + 1):
        x = x0 + (x1 - x0) * k / n
        g.box("bronze_frame", max(x0, x - fr / 2), min(x1, x + fr / 2), s_mid - depth / 2, s_mid + depth / 2, z0, z1)
    if (z1 - z0) > 5:
        zt = z1 - (z1 - z0) * 0.22
        g.box("bronze_frame", x0, x1, s_mid - 0.1, s_mid + 0.1, zt - 0.08, zt + 0.08)
    g.box("glass", x0, x1, s_mid - 0.03, s_mid + 0.03, z0 + fr, z1 - fr)
    if stone and lintel_side:
        d = 0.35 if lintel_side == "s" else -0.35
        sa, sb = sorted((s_mid, s_mid + d))
        g.box("limestone_smooth", x0 - 0.4, x1 + 0.4, sa, sb, z1, z1 + 0.9)
        g.box("limestone_smooth", x0 - 0.2, x1 + 0.2, sa, sb, z0 - 0.35, z0)


def window_s(g, s0, s1, x_mid, z0, z1, depth=0.5, stone=True, lintel_side=None):
    n = max(1, round((s1 - s0) / 3.5))
    fr = 0.22
    g.box("bronze_frame", x_mid - depth / 2, x_mid + depth / 2, s0, s1, z0, z0 + fr)
    g.box("bronze_frame", x_mid - depth / 2, x_mid + depth / 2, s0, s1, z1 - fr, z1)
    for k in range(n + 1):
        s = s0 + (s1 - s0) * k / n
        g.box("bronze_frame", x_mid - depth / 2, x_mid + depth / 2, max(s0, s - fr / 2), min(s1, s + fr / 2), z0, z1)
    if (z1 - z0) > 5:
        zt = z1 - (z1 - z0) * 0.22
        g.box("bronze_frame", x_mid - 0.1, x_mid + 0.1, s0, s1, zt - 0.08, zt + 0.08)
    g.box("glass", x_mid - 0.03, x_mid + 0.03, s0 + fr, s1 - fr, z0 + fr, z1 - fr)
    if stone and lintel_side:
        d = 0.35 if lintel_side == "e" else -0.35
        xa, xb = sorted((x_mid, x_mid + d))
        g.box("limestone_smooth", xa, xb, s0 - 0.4, s1 + 0.4, z1, z1 + 0.9)
        g.box("limestone_smooth", xa, xb, s0 - 0.2, s1 + 0.2, z0 - 0.35, z0)


# --------------------------------------------------------------------------
# Exterior openings, by level: (a0, a1, z0, z1, kind) with z relative to level
SOUTH = {
    "walkout": [(-56, -40, 1, 8, "w"), (-32, -16, 1, 8, "w"), (-10, -4, 1, 8, "w"), (-4, 4, 0, 7.5, "dd_glass"),
                (4, 10, 1, 8, "w"), (16, 38, 1, 8, "w"), (45, 57, 1, 8, "w")],
    "main": [(-52, -49, 0, 7.5, "door_glass"), (-46, -37, 1, 8.5, "w"), (-31, -19, 1, 8.5, "w"),
             (-14, -5, 1, 8.5, "w"), (-4, 4, 0, 8, "dd_glass"), (5, 14, 1, 8.5, "w"), (19, 31, 1, 8.5, "w"),
             (38, 56, 3, 8.5, "w")],
    "second": [(-56, -48, 2, 8, "w"), (-46, -38, 2, 8, "w"), (-32, -24, 2, 8, "w"), (-22, -14, 2, 8, "w"),
               (-8, 8, 2, 8, "w"), (16, 24, 2, 8, "w"), (26, 34, 2, 8, "w"), (40, 48, 2, 8, "w"), (50, 58, 2, 8, "w")],
}
NORTH = {
    "walkout": [(-2, 2, 0, 7, "door_cart")],
    "main": [(-54, -50, 3, 8, "w"), (-44, -40, 3, 8, "w"), (-31, -27, 3, 8, "w"), (-25, -22.5, 0, 7.5, "door_mud"),
             (-20.5, -18.5, 5.5, 8, "w"), (-15.5, -13.5, 5.5, 8, "w"), (-3, 3, 0, 8, "dd_front"),
             (17, 23, 3, 8, "w"), (40, 46, 3, 8, "w"), (50, 56, 3, 8, "w")],
    "second": [(-54, -50, 3, 8, "w"), (-42, -38, 3, 8, "w"), (-30, -26, 3, 8, "w"), (-18, -14, 3, 8, "w"),
               (-3, 3, 2, 8, "w"), (16, 20, 3, 8, "w"), (30, 33, 3, 8, "w"), (40, 43, 3, 8, "w"), (50, 54, 3, 8, "w")],
}
WEST = {
    "walkout": [(774, 781, 2, 8, "w")],
    "main": [(744, 747, 0, 7.5, "door_west"), (760, 770, 1, 8.5, "w"), (774, 781, 1, 8.5, "w")],
    "second": [(742, 746, 3, 8, "w"), (764, 772, 2, 8, "w"), (776, 781, 2, 8, "w")],
}
EAST = {
    "walkout": [(774, 781, 2, 8, "w")],
    "main": [(741, 746, 3, 8, "w"), (760, 767, 3, 8.5, "w"), (770, 773, 0, 7.5, "door_east"), (776, 781, 3, 8.5, "w")],
    "second": [(742, 746, 3, 8, "w"), (762, 770, 2, 8, "w"), (775, 781, 2, 8, "w")],
}


def exterior(g, col):
    for lvl, z in LEVELS.items():
        zb = z - 1.0 if lvl != "walkout" else z - 1.5
        zt = z + RISE - 1.0 if lvl != "second" else L.Z_EAVE
        if lvl == "walkout":
            zt = -1.0
        outer = "limestone" if lvl == "walkout" else "oak_siding"
        north_outer = "concrete" if lvl == "walkout" else "oak_siding"
        # SOUTH wall
        ops = [(a0, a1, z + b0, z + b1) for a0, a1, b0, b1, _ in SOUTH[lvl]]
        wall_x(g, outer, XW, XE, SS - 1, SS, zb, zt, ops, fmat={"n": "plaster"}, reveal="limestone_smooth")
        for a0, a1, b0, b1, kind in SOUTH[lvl]:
            if kind == "w":
                window_x(g, a0, a1, SS - 0.5, z + b0, z + b1, lintel_side="s")
        # NORTH wall
        ops = [(a0, a1, z + b0, z + b1) for a0, a1, b0, b1, _ in NORTH[lvl]]
        wall_x(g, north_outer, XW, XE, SN, SN + 1, zb, zt, ops, fmat={"s": "plaster"}, reveal="limestone_smooth")
        for a0, a1, b0, b1, kind in NORTH[lvl]:
            if kind == "w":
                window_x(g, a0, a1, SN + 0.5, z + b0, z + b1, lintel_side="n")
        # WEST / EAST walls (between north and south walls)
        for side, xs, table in (("w", (XW, XW + 1), WEST), ("e", (XE - 1, XE), EAST)):
            ops = [(a0, a1, z + b0, z + b1) for a0, a1, b0, b1, _ in table[lvl]]
            inner = "e" if side == "w" else "w"
            wall_s(g, outer, SN + 1, SS - 1, xs[0], xs[1], zb, zt, ops, fmat={inner: "plaster"}, reveal="limestone_smooth")
            for a0, a1, b0, b1, kind in table[lvl]:
                if kind == "w":
                    window_s(g, a0, a1, (xs[0] + xs[1]) / 2, z + b0, z + b1, lintel_side=side)
        # floor-line belt course (limestone) and plinth
        if lvl != "walkout":
            g.box("limestone_smooth", XW - 0.25, XE + 0.25, SN - 0.25, SN, z - 1.2, z - 0.2)
            g.box("limestone_smooth", XW - 0.25, XE + 0.25, SS, SS + 0.25, z - 1.2, z - 0.2)
            g.box("limestone_smooth", XW - 0.25, XW, SN, SS, z - 1.2, z - 0.2)
            g.box("limestone_smooth", XE, XE + 0.25, SN, SS, z - 1.2, z - 0.2)
    # foundation/footing and walkout slab
    g.box("concrete", XW - 1, XE + 1, SN - 1, SS + 1, -13.5, -12.0)
    slab(g, "polished_concrete", XW, XE, SN, SS, -12.0, -11.0, bottom="concrete")
    # corner quoins of limestone up the siding (Federal detail)
    for x0, x1 in ((XW - 0.3, XW + 1.5), (XE - 1.5, XE + 0.3)):
        for s0, s1 in ((SN - 0.3, SN + 1.5), (SS - 1.5, SS + 0.3)):
            for k in range(20):
                zz = -0.2 + k * 1.05
                if zz > L.Z_EAVE - 1:
                    break
                w = 0.6 if k % 2 else 0.0
                g.box("limestone_smooth", x0 - (w if x0 < 0 else 0), x1 + (w if x0 > 0 else 0),
                      s0 - (w if s0 < 760 else 0), s1 + (w if s0 > 760 else 0), zz, zz + 0.95)


def exterior_doors(col, g):
    z = 0.0
    I.double_door_x(col, "FrontDoor", -3, 3, SN + 0.5, z, opens_south=True, label="front door", height=8)
    g.box("limestone_smooth", -4.5, 4.5, SN - 0.4, SN, 8.0, 9.2)  # stone head
    # fanlight over the front door (Federal)
    for k in range(9):
        a0, a1 = math.pi * k / 9, math.pi * (k + 1) / 9
        g.face("bronze_frame", [(3 * math.cos(a0), SN - 0.05, 9.2 + 1.6 * math.sin(a0)),
                                (3 * math.cos(a1), SN - 0.05, 9.2 + 1.6 * math.sin(a1)),
                                (0, SN - 0.05, 9.2)])
    I.hinged_door_x(col, "MudroomDoor", -25, SN + 0.5, z, 2.5, +1, True, "mudroom door")
    I.double_door_x(col, "GreatRoomDoors", -4, 4, SS - 0.5, z, opens_south=False, label="terrace doors", glass=True, height=8)
    I.hinged_door_x(col, "PrimaryDeckDoor", -52, SS - 0.5, z, 3, +1, False, "door to deck", glass=True, height=7.5)
    I.double_door_x(col, "GalleryDoors", -4, 4, SS - 0.5, -11, opens_south=False, label="patio doors", glass=True, height=7.5)
    I.hinged_door_s(col, "WestPorchDoor", XW + 0.5, 744, z, 3, +1, True, "door to west porch", height=7.5)
    I.hinged_door_s(col, "KitchenPorchDoor", XE - 0.5, 770, z, 3, +1, False, "door to east porch", glass=True, height=7.5)
    I.hinged_door_x(col, "CartBayDoor", -2, SN + 0.5, -11, 4, +1, False, "door to the tunnel", mat="oak", height=7)


# --------------------------------------------------------------------------
# Interior partitions. Door tuples: (a0, a1) on the wall's axis; "open" = no door
def partitions(g, col):
    T = 0.25
    specs = {
        "walkout": {
            "hall_n": (-59, 59, [(-40, -37, "theater"), (-32, -29, "wine cellar"), (-22, -19, "parts library"),
                                 (-4, 4, None), (4, 8, "wall_under_stair"), (8, 12, None), (16, 19, "safe room"),
                                 (27, 30, "electrical room"), (44, 48, "mechanical room")]),
            "hall_s": (-59, 59, [(-40, -37, "guest suite"), (-18, -15, "suite 5"), (-12, 12, None),
                                 (20, 26, None), (48, 51, "gym")]),
            "north_x": [-36, -26, 12, 24, 34],
            "south_x": [-36, -12, 12, 42],
        },
        "main": {
            "hall_n": (-34, 59, [(-30, -27, "mudroom"), (-21, -18.5, "powder room"), (-16, -13.5, "powder room"),
                                 (-4, 4, None), (4, 12, None), (16, 22, None), (28, 36, None), (44, 47, "scullery")]),
            "hall_s": (-34, 59, [(-30, -27, "library"), (-16, 16, None), (19, 31, None), (34, 59, None)]),
            "north_x": [-22, -17, 28, 36],
            "south_x": [-16, 16, 34],
        },
        "second": {
            "hall_n": (-59, 59, [(-50, -47, "dressing room"), (-26, -23, "dressing room"), (-4, 4, None),
                                 (4, 8, None), (8, 12, "rail"), (16, 19, "dressing room"), (28, 32, "rail"),
                                 (32, 36, None), (39, 42, "laundry"), (50, 53, "dressing room")]),
            "hall_s": (-59, 59, [(-50, -47, "suite 1"), (-26, -23, "suite 2"), (-12, 12, None),
                                 (22, 25, "suite 3"), (46, 49, "suite 4")]),
            "north_x": [-36, 28, 36, 46],
            "south_x": [-36, -12, 12, 36],
        },
    }
    n_door = 0
    for lvl, spec in specs.items():
        z = LEVELS[lvl]
        top = z + CEIL[lvl]
        # hall walls
        for key, s_line, opens_south in (("hall_n", S_HALL, False), ("hall_s", 756.0, True)):
            x0, x1, doors = spec[key]
            ops = []
            for a0, a1, what in doors:
                if what == "wall_under_stair":
                    continue
                if what == "rail":
                    ops.append((a0, a1, z, top))
                    g.box("black_iron", a0, a1, s_line - 0.05, s_line + 0.05, z + 3.2, z + 3.4)
                    g.box("oak", a0, a1, s_line - 0.15, s_line + 0.15, z + 3.4, z + 3.55)
                    for k in range(int(a1 - a0) * 2 + 1):
                        xx = a0 + k * 0.5
                        g.box("black_iron", xx - 0.03, xx + 0.03, s_line - 0.03, s_line + 0.03, z, z + 3.3)
                    continue
                ops.append((a0, a1, z, z + (7.0 if what else top - z)))
            wall_x(g, "plaster", x0, x1, s_line - T, s_line + T, z, top, ops)
            for a0, a1, what in doors:
                if what and what not in ("wall_under_stair", "rail"):
                    # hinge on the west jamb; open into the room
                    n_door += 1
                    I.hinged_door_x(col, f"Door_{lvl}_{n_door}", a0, s_line, z, a1 - a0, +1,
                                    opens_south=(key == "hall_s"), label=what)
        # room dividers
        for x in spec["north_x"]:
            wall_s(g, "plaster", SN + 1, S_HALL - T, x - T, x + T, z, top)
        for x in spec["south_x"]:
            ops = []
            if lvl == "main" and x == 16:
                ops = [(760, 780, z, z + 8.5)]
            if lvl == "main" and x == 34:
                ops = [(759, 781, z, z + 8.5)]
            if lvl == "main" and x == -16:
                ops = [(758, 762, z, z + 7.5)]
            wall_s(g, "plaster", 756 + T, SS - 1, x - T, x + T, z, top, ops)
    # core walls (elevator hoistway, stair bays) on every level
    for lvl, z in LEVELS.items():
        top = z + CEIL[lvl]
        # hoistway: west wall, south wall, east wall with landing opening
        wall_s(g, "plaster", SN + 1, S_HALL + T, -12 - T, -12 + T, z, top)
        wall_x(g, "plaster", -12, -4, S_HALL - T, S_HALL + T, z, top)
        wall_s(g, "plaster", SN + 1, S_HALL + T, -4 - T, -4 + T, z, top, [(741, 745, z, z + 7.2)])
        # main stair bay walls
        wall_s(g, "plaster", SN + 1, S_HALL, 4 - T, 4 + T, z, top)
        wall_s(g, "plaster", SN + 1, S_HALL, 12 - T, 12 + T, z, top)
        if lvl == "walkout":
            g.box("plaster", 4, 8, S_HALL - T, S_HALL + T, z, z + 9.5)
        if lvl != "walkout":
            wall_s(g, "plaster", SN + 1, S_HALL, 28 - T, 28 + T, z, top)
            wall_s(g, "plaster", SN + 1, S_HALL, 36 - T, 36 + T, z, top)
        if lvl == "main":
            g.box("plaster", 28, 32, S_HALL - T, S_HALL + T, z, z + 9.5)
    # primary suite (main level): east wall with a door off the hall, inner wall
    z = 0.0
    wall_s(g, "plaster", SN + 1, SS - 1, -34 - T, -34 + T, z, 10, [(751.5, 754.5, z, z + 7)])
    I.hinged_door_s(col, "Door_primary", -34, 751.5, z, 3, +1, opens_east=False, label="primary suite")
    wall_x(g, "plaster", XW + 1, -34, 756 - T, 756 + T, z, 10, [(-46, -43, z, z + 7)])
    I.hinged_door_x(col, "Door_primary_bath", -46, 756, z, 3, +1, opens_south=False, label="primary bath")
    return n_door


# --------------------------------------------------------------------------
def floors(g):
    hoist = (-11.75, -4.25, SN + 1, S_HALL - 0.25)
    stair = (4.25, 11.75, SN + 1, S_HALL)
    svc = (28.25, 35.75, SN + 1, S_HALL)
    slab(g, "oak_floor", XW + 1, XE - 1, SN + 1, SS - 1, -1.0, 0.0, [hoist, stair], bottom="plaster_ceiling")
    slab(g, "oak_floor", XW + 1, XE - 1, SN + 1, SS - 1, 10.0, 11.0, [hoist, stair, svc], bottom="plaster_ceiling")
    slab(g, "plaster_ceiling", XW, XE, SN, SS, 20.0, 21.0, [], bottom="plaster_ceiling")
    # stone floors in the foyer and mudroom
    g.box("limestone_smooth", -4, 4, SN + 1, S_HALL, 0.0, 0.02)
    g.box("limestone_smooth", -34, -22, SN + 1, S_HALL, 0.0, 0.02)


def u_stair(g, xa0, xa1, xb0, xb1, z):
    """U-stair: flight A rises north from the hall line, landing at the north end,
    flight B returns south to arrive at the hall line one level up."""
    for i in range(1, 9):
        top = z + i * R
        s1 = S_HALL - (i - 1) * TD
        s0 = S_HALL - i * TD
        g.box("oak", xa0, xa1, s0, s1, top - 0.9, top, fmat={"bottom": "plaster_ceiling"})
    land = z + 9 * R
    g.box("oak", xa0 if xa0 < xb0 else xb0, xb1 if xb1 > xa1 else xa1, SN + 1, S_LAND, land - 0.9, land,
          fmat={"bottom": "plaster_ceiling"})
    for j in range(1, 9):
        top = z + (9 + j) * R
        s0 = S_LAND + (j - 1) * TD
        s1 = S_LAND + j * TD
        g.box("oak", xb0, xb1, s0, s1, top - 0.9, top, fmat={"bottom": "plaster_ceiling"})
    # center wall between flights with an oak handrail
    xm = (min(xa1, xb1) + max(xa0, xb0)) / 2
    g.box("plaster", xm - 0.12, xm + 0.12, S_LAND, S_HALL - 0.8, z - 0.9, z + RISE + 3.0)
    g.box("oak", xm - 0.2, xm + 0.2, S_LAND, S_HALL - 0.8, z + RISE + 3.0, z + RISE + 3.2)


def stairs(g):
    # main stair: flight A on the east half (8..12), flight B on the west half (4..8)
    u_stair(g, 8.0, 11.75, 4.25, 8.0, -11.0)
    u_stair(g, 8.0, 11.75, 4.25, 8.0, 0.0)
    # service stair main -> second
    u_stair(g, 32.0, 35.75, 28.25, 32.0, 0.0)
    # handrails (black iron) along the open sides of landings at the second floor
    g.box("black_iron", 4.25, 11.75, S_LAND - 0.05, S_LAND + 0.05, 11 + 3.3, 11 + 3.4)


def elevator(g, col):
    """LU/LA elevator: hoistway -12..-4, car moves between the three levels."""
    import bpy
    car = Geo()
    w0, w1, d0, d1 = -11.4, -5.0, 739.5, 747.5
    car.box("oak", w0 - (-8.2), w1 - (-8.2), d0 - 743.5, d1 - 743.5, 0, 0.3)
    car.box("oak", w0 + 8.2, w0 + 8.2 + 0.2, d0 - 743.5, d1 - 743.5, 0.3, 7.3)
    car.box("oak", w0 + 8.2, w1 + 8.2, d0 - 743.5, d0 - 743.5 + 0.2, 0.3, 7.3)
    car.box("oak", w0 + 8.2, w1 + 8.2, d1 - 743.5 - 0.2, d1 - 743.5, 0.3, 7.3)
    car.box("plaster_ceiling", w0 + 8.2, w1 + 8.2, d0 - 743.5, d1 - 743.5, 7.3, 7.6)
    levels_m = [LEVELS[k] * FT for k in ("walkout", "main", "second")]
    obj = car.to_object("ElevatorCar", col, local_at=(-8.2, 743.5, -11.0),
                        props={"interact": "elevator", "levels": levels_m, "level": 0,
                               "label": "elevator", "collide": 1, "platform": 1})
    # buttons inside the car, parented to it
    bpy.context.view_layer.update()
    names = ["walkout", "main", "second"]
    for i, n in enumerate(names):
        b = Geo()
        b.cylinder("button", 0, 0, 0.12, -0.05, 0.05, seg=10)
        bo = b.to_object(f"ElevatorBtn_{i}", col, local_at=(w0 + 0.3, 742 + i * 0.6, -11 + 3.6 + i * 0.01),
                         props={"interact": "elevator_go", "level": i, "label": f"go to {n} level"})
        bo.rotation_euler = (0, math.radians(90), 0)
        bo.parent = obj
        bo.matrix_parent_inverse = obj.matrix_world.inverted()
    I.light(col, "ElevatorCar_light", -8.2, 743.5, -11 + 7.0, "elevator", intensity=4, range_m=4)
    # landing doors (slide north when the car is here) + call buttons
    for i, n in enumerate(names):
        z = LEVELS[n]
        d = Geo()
        d.box("stainless", -0.08, 0.08, 0, 4.0, 0, 7.2)
        I.sliding(col, d, f"ElevatorDoor_{i}", (-4.0, 741.0, z), f"elevator door ({n})", dy=-3.8,
                  elev_door=i)
        cb = Geo()
        cb.box("bronze_ss", -0.05, 0.05, -0.2, 0.2, -0.35, 0.35)
        cb.to_object(f"ElevatorCall_{i}", col, local_at=(-3.7, 746.2, z + 3.6),
                     props={"interact": "elevator_call", "level": i, "label": "call the elevator"})
        # stainless surround
        g.box("stainless", -3.8, -3.7, 740.6, 741.0, z, z + 7.6)
        g.box("stainless", -3.8, -3.7, 745.0, 745.4, z, z + 7.6)
        g.box("stainless", -3.8, -3.7, 740.6, 745.4, z + 7.2, z + 7.6)
    # hoistway pit floor
    g.box("concrete", -11.75, -4.25, SN + 1, S_HALL - 0.25, -12.5, -11.0)


# --------------------------------------------------------------------------
def roof(g, gn):
    x0, x1 = XW - 2, XE + 2
    zr = L.Z_RIDGE
    slope = 7 / 12
    sn, ss = SN - 2, SS + 2.6
    zn, zs = zr - (760 - sn) * slope, zr - (ss - 760) * slope
    th = 0.8
    # north plane (slate)
    for (sa, za), (sb, zb), mat in (((sn, zn), (760, zr), "slate"), ((760, zr), (ss, zs), "standing_seam")):
        top = [(x0, sa, za), (x1, sa, za), (x1, sb, zb), (x0, sb, zb)]
        if mat == "slate":
            g.face(mat, [(x0, sb, zb), (x1, sb, zb), (x1, sa, za), (x0, sa, za)])
        else:
            g.face(mat, [(x0, sb, zb), (x1, sb, zb), (x1, sa, za), (x0, sa, za)])
        g.face("oak", [(x0, sa, za - th), (x1, sa, za - th), (x1, sb, zb - th), (x0, sb, zb - th)])
        for xx in (x0, x1):
            pts = [(xx, sa, za - th), (xx, sb, zb - th), (xx, sb, zb), (xx, sa, za)]
            if xx == x1:
                pts.reverse()
            g.face("oak", pts)
    # ridge cap and eave fascias / stainless gutters
    g.box("slate", x0, x1, 759.6, 760.4, zr - 0.2, zr + 0.35)
    g.box("oak", x0, x1, sn - 0.2, sn, zn - th - 0.3, zn)
    g.box("oak", x0, x1, ss, ss + 0.2, zs - th - 0.3, zs)
    g.box("stainless", x0, x1, sn - 0.7, sn - 0.2, zn - th - 0.4, zn - th + 0.1)
    g.box("stainless", x0, x1, ss + 0.2, ss + 0.7, zs - th - 0.4, zs - th + 0.1)
    for xx in (-58, -20, 20, 58):
        g.box("stainless", xx - 0.2, xx + 0.2, sn - 0.7, sn - 0.3, 0, zn - th)
        g.box("stainless", xx - 0.2, xx + 0.2, ss + 0.3, ss + 0.7, -11, zs - th)
    # gable ends (oak siding triangles) with Federal lunettes
    for xx, sgn in ((XW, -1), (XE, 1)):
        for off in (0.0, 1.0):
            x = xx - sgn * off
            tri = [(x, SN, L.Z_EAVE), (x, SS, L.Z_EAVE), (x, 760, zr)]
            if (sgn > 0) == (off == 0.0):
                g.face("oak_siding", tri)
            else:
                g.face("oak_siding", list(reversed(tri)))
        for k in range(10):
            a0, a1 = math.pi * k / 10, math.pi * (k + 1) / 10
            pts = [(xx + sgn * 0.05, 760 - 3.2 * math.cos(a0), 25 + 3.2 * math.sin(a0)),
                   (xx + sgn * 0.05, 760 - 3.2 * math.cos(a1), 25 + 3.2 * math.sin(a1)),
                   (xx + sgn * 0.05, 760, 25)]
            if sgn < 0:
                pts.reverse()
            g.face("white_paint", pts)
        g.box("limestone_smooth", xx - 0.3 if sgn > 0 else xx - 0.1, xx + 0.1 if sgn > 0 else xx + 0.3,
              756.3, 763.7, 24.6, 25.0)
    # PV array on the south slope (energy model default ~40-50 kW)
    for row in range(4):
        s_a = 762.0 + row * 5.6
        s_b = s_a + 5.3
        if s_b > SS + 1.5:
            break
        za, zb = zr - (s_a - 760) * slope + 0.3, zr - (s_b - 760) * slope + 0.3
        for col in range(32):
            xa = -54 + col * 3.4
            xb = xa + 3.25
            gn.face("pv", [(xa, s_b, zb), (xb, s_b, zb), (xb, s_a, za), (xa, s_a, za)])
    # snow rail at the PV eave
    g.box("stainless", x0, x1, SS + 1.4, SS + 1.6, zs + 0.2, zs + 0.5)
    # cupola over the stair core, on the axis
    g.box("oak_siding", -5, 5, 755, 765, 31.0, 36.5)
    for (xa, xb, sa, sb) in ((-5, -4.5, 755, 755.5), (4.5, 5, 755, 755.5), (-5, -4.5, 764.5, 765), (4.5, 5, 764.5, 765)):
        g.box("white_paint", xa, xb, sa, sb, 36.5, 40.0)
    for k in range(7):
        zz = 36.8 + k * 0.45
        g.box("white_paint", -4.5, 4.5, 755.1, 755.3, zz, zz + 0.2)
        g.box("white_paint", -4.5, 4.5, 764.7, 764.9, zz, zz + 0.2)
        g.box("white_paint", -4.9, -4.7, 755.5, 764.5, zz, zz + 0.2)
        g.box("white_paint", 4.7, 4.9, 755.5, 764.5, zz, zz + 0.2)
    g.box("oak", -4.4, 4.4, 755.4, 764.6, 36.5, 40.0)  # dark interior behind louvers
    g.box("white_paint", -5.6, 5.6, 754.4, 765.6, 40.0, 40.5)
    for i in range(4):
        ang = [(-6, 754, 6, 754), (6, 754, 6, 766), (6, 766, -6, 766), (-6, 766, -6, 754)][i]
        g.face("slate", [(ang[0], ang[1], 40.5), (ang[2], ang[3], 40.5), (0, 760, 44.0)]
               if i in (1, 3) else [(ang[0], ang[1], 40.5), (ang[2], ang[3], 40.5), (0, 760, 44.0)])
    g.sphere("bronze_ss", 0, 760, 44.7, 0.55, seg=10, rings=6)
    g.cone("bronze_ss", 0, 760, 0.2, 45.1, 47.6, seg=8)
    g.box("bronze_ss", -0.05, 0.05, 759.95, 760.05, 44.0, 47.0)
    # masonry heater chimney (library/great room wall)
    g.box("limestone", -17.5, -14.5, 765, 771, 7.0, 37.0)
    g.box("limestone_smooth", -18.0, -14.0, 764.5, 771.5, 37.0, 37.6)
    g.box("black_iron", -16.6, -15.4, 767.4, 768.6, 37.6, 38.3)


def masonry_heater(g, col):
    g.box("limestone", -18.5, -13.5, 764, 772, 0.0, 7.0)
    g.box("limestone_smooth", -19.0, -13.0, 763.5, 772.5, 7.0, 7.5)
    g.box("black_iron", -13.55, -13.45, 766.5, 769.5, 1.5, 3.8)  # firebox door frame
    fire = Geo()
    for k, (ds, h) in enumerate(((0.0, 1.0), (0.5, 0.8), (-0.5, 0.7), (0.25, 0.6))):
        fire.cone("flame", 0, ds, 0.35 - k * 0.04, 0, h, seg=6)
    fire.box("ember", -0.5, 0.2, -1.1, 1.1, -0.15, 0.0)
    fire.to_object("HeaterFire", col, local_at=(-14.2, 768, 1.7), props={"flame_group": "heater"})
    sw = Geo()
    sw.box("black_iron", -0.05, 0.05, -0.3, 0.3, -0.3, 0.3)
    sw.to_object("HeaterDamper", col, local_at=(-13.45, 770.3, 4.3),
                 props={"interact": "fire", "group": "heater", "label": "light the masonry heater"})
    I.light(col, "HeaterFire_light", -12.5, 768, 2.5, "fire_heater", intensity=6, color="#ff8a3c", range_m=6)


# --------------------------------------------------------------------------
def porches(g, col):
    """North wrap porch, porte-cochere, east/west porches, south deck, patio."""
    from .layout import terrain
    # north porch at grade, limestone pavers
    g.box("limestone_smooth", XW - 10, XE + 10, 726, SN, -1.2, 0.0, top="cobble")
    # east/west porches: limestone plinths down to grade, becoming terraces
    for x0, x1 in ((XW - 10, XW), (XE, XE + 10)):
        g.box("limestone", x0, x1, SN, 790, -13.0, 0.0, top="cobble")
    # porch roofs: slate sheds on oak posts
    def shed_x(xa, xb, s_wall, s_out, z_wall=10.8, z_out=9.4):
        g.face("slate", [(xa, s_out, z_out), (xb, s_out, z_out), (xb, s_wall, z_wall), (xa, s_wall, z_wall)]
               if s_out < s_wall else [(xa, s_wall, z_wall), (xb, s_wall, z_wall), (xb, s_out, z_out), (xa, s_out, z_out)])
        g.face("plaster_ceiling", [(xa, s_wall, z_wall - 0.4), (xb, s_wall, z_wall - 0.4), (xb, s_out, z_out - 0.4), (xa, s_out, z_out - 0.4)]
               if s_out < s_wall else [(xa, s_out, z_out - 0.4), (xb, s_out, z_out - 0.4), (xb, s_wall, z_wall - 0.4), (xa, s_wall, z_wall - 0.4)])
        so = min(s_out, s_wall) if s_out < s_wall else max(s_out, s_wall)
        g.box("oak", xa, xb, so - 0.3 if s_out < s_wall else so, so if s_out < s_wall else so + 0.3, z_out - 1.2, z_out)
    shed_x(XW - 10.5, -15, SN, 725.5)
    shed_x(15, XE + 10.5, SN, 725.5)

    def shed_s(sa, sb, x_wall, x_out, z_wall=10.8, z_out=9.4):
        if x_out < x_wall:
            g.face("slate", [(x_out, sa, z_out), (x_out, sb, z_out), (x_wall, sb, z_wall), (x_wall, sa, z_wall)])
            g.face("plaster_ceiling", [(x_wall, sa, z_wall - 0.4), (x_wall, sb, z_wall - 0.4), (x_out, sb, z_out - 0.4), (x_out, sa, z_out - 0.4)])
            g.box("oak", x_out - 0.3, x_out, sa, sb, z_out - 1.2, z_out)
        else:
            g.face("slate", [(x_wall, sa, z_wall), (x_wall, sb, z_wall), (x_out, sb, z_out), (x_out, sa, z_out)])
            g.face("plaster_ceiling", [(x_out, sa, z_out - 0.4), (x_out, sb, z_out - 0.4), (x_wall, sb, z_wall - 0.4), (x_wall, sa, z_wall - 0.4)])
            g.box("oak", x_out, x_out + 0.3, sa, sb, z_out - 1.2, z_out)
    shed_s(725.5, 790, XW, XW - 10.5)
    shed_s(725.5, 790, XE, XE + 10.5)
    posts = [(x, 726.2) for x in (-69.5, -58, -46, -34, -22) + (22, 34, 46, 58, 69.5)]
    posts += [(-69.5, s) for s in (738, 750, 762, 774, 789.5)] + [(69.5, s) for s in (738, 750, 762, 774, 789.5)]
    for x, s in posts:
        g.box("oak_timber", x - 0.35, x + 0.35, s - 0.35, s + 0.35, 0.0, 9.4)
        g.box("limestone_smooth", x - 0.5, x + 0.5, s - 0.5, s + 0.5, 0.0, 0.6)
    # railings where the terraces stand above grade
    for x in (XW - 9.8, XE + 9.8):
        g.box("oak", x - 0.2, x + 0.2, 752, 790, 3.2, 3.45)
        for k in range(77):
            s = 752 + k * 0.5
            g.box("black_iron", x - 0.03, x + 0.03, s - 0.03, s + 0.03, 0, 3.2)
    # porte-cochere: stone piers, oak beams, slate gable with a lit ceiling
    for x in (-13.5, 13.5):
        for s in (710.5, 725.5):
            g.box("limestone", x - 1.2, x + 1.2, s - 1.2, s + 1.2, 0.0, 14.0)
            g.box("black_iron", x - 0.4, x + 0.4, s - 0.4, s + 0.4, -0.5, 13.5)  # steel core
            g.box("limestone_smooth", x - 1.4, x + 1.4, s - 1.4, s + 1.4, 14.0, 14.6)
    g.box("oak_timber", -15, 15, 709.5, 711.0, 14.6, 16.0)
    g.box("oak_timber", -15, 15, 725.0, 726.5, 14.6, 16.0)
    g.box("oak_timber", -15, -13.5, 709.5, SN, 14.6, 16.0)
    g.box("oak_timber", 13.5, 15, 709.5, SN, 14.6, 16.0)
    zr = 16.0 + 16 * 8 / 12
    g.face("slate", [(-16, 708.5, 16.0), (-16, SN, 16.0), (0, SN, zr), (0, 708.5, zr)])
    g.face("slate", [(16, SN, 16.0), (16, 708.5, 16.0), (0, 708.5, zr), (0, SN, zr)])
    g.face("plaster_ceiling", [(-15, 710, 15.8), (15, 710, 15.8), (15, SN, 15.8), (-15, SN, 15.8)][::-1])
    g.face("oak_siding", [(-16, 708.5, 16.0), (16, 708.5, 16.0), (0, 708.5, zr)][::-1])
    g.face("oak_siding", [(-16, 708.6, 16.0), (16, 708.6, 16.0), (0, 708.6, zr)])
    for k in range(9):
        a0, a1 = math.pi * k / 9, math.pi * (k + 1) / 9
        g.face("white_paint", [(2.6 * math.cos(a1), 708.4, 17.5 + 2.6 * math.sin(a1)),
                               (2.6 * math.cos(a0), 708.4, 17.5 + 2.6 * math.sin(a0)), (0, 708.4, 17.5)])
    I.light(col, "PorteCochere_light1", 0, 716, 15.0, "porte_cochere", intensity=10, range_m=10)
    I.light(col, "PorteCochere_light2", 0, 730, 9.5, "porte_cochere", intensity=6, range_m=8)
    lamp = Geo()
    lamp.box("lamp_warm", -3, 3, -0.4, 0.4, 0, 0.12)
    lamp.to_object("PorteCochere_lamp", col, local_at=(0, 716, 15.65), props={"lamp_group": "porte_cochere"})
    # south: 6-ft dry-under deck + 20x20 corner decks at the main level
    g.box("oak_floor", XW, XE, SS, SS + 6, -0.8, 0.0, bottom="plaster_ceiling")
    g.box("oak_floor", XW, XW + 20, SS + 6, SS + 20, -0.8, 0.0, bottom="plaster_ceiling")
    g.box("oak_floor", XE - 20, XE, SS + 6, SS + 20, -0.8, 0.0, bottom="plaster_ceiling")
    for x in (-59.5, -41, -29, -17, -5, 5, 17, 29, 41, 59.5):
        g.box("limestone", x - 0.7, x + 0.7, SS + 5.3, SS + 6.7, -11.0, -0.8)
    for x in (-59.5, -41, 41, 59.5):
        g.box("limestone", x - 0.7, x + 0.7, SS + 19.3, SS + 20.7, terrain(x, SS + 20) - 0.5, -0.8)
    # deck railings
    def rail_x(xa, xb, s):
        g.box("oak", xa, xb, s - 0.2, s + 0.2, 3.2, 3.45)
        g.box("black_iron", xa, xb, s - 0.04, s + 0.04, 0.3, 0.4)
        n = int((xb - xa) / 0.5)
        for k in range(n + 1):
            x = xa + k * (xb - xa) / n
            g.box("black_iron", x - 0.03, x + 0.03, s - 0.03, s + 0.03, 0.0, 3.2)

    def rail_s(sa, sb, x):
        g.box("oak", x - 0.2, x + 0.2, sa, sb, 3.2, 3.45)
        n = int((sb - sa) / 0.5)
        for k in range(n + 1):
            s = sa + k * (sb - sa) / n
            g.box("black_iron", x - 0.03, x + 0.03, s - 0.03, s + 0.03, 0.0, 3.2)
    rail_x(XW + 20, XE - 20, SS + 6)
    rail_x(XW, XW + 12, SS + 20)
    rail_x(XW + 17, XW + 20, SS + 20)
    rail_x(XE - 20, XE - 17, SS + 20)
    rail_x(XE - 12, XE, SS + 20)
    rail_s(SS + 6, SS + 20, XW + 20)
    rail_s(SS + 6, SS + 20, XE - 20)
    rail_s(SS, SS + 20, XW)
    rail_s(SS, SS + 20, XE)
    # stairs from the corner decks down to the yard (the berm-top path)
    for xa in (XW + 12, XE - 17):
        z_foot = terrain(xa + 2.5, SS + 40)
        n = max(1, int(round((0 - z_foot) / 0.62)))
        r = (0 - z_foot) / n
        for i in range(1, n + 1):
            top = -i * r
            s0 = SS + 20 + (i - 1) * TD
            g.box("limestone_smooth", xa, xa + 5, s0, s0 + TD, top - 0.8 if i < n else z_foot - 0.5, top)
        g.box("limestone", xa - 0.5, xa, SS + 20, SS + 20 + n * TD, z_foot - 0.5, 3.0 * 0 + 0.5)
        g.box("limestone", xa + 5, xa + 5.5, SS + 20, SS + 20 + n * TD, z_foot - 0.5, 0.5)
    # walkout patio (limestone) under the deck
    g.box("limestone", XW - 2, XE + 2, SS, SS + 9, -12.8, -11.0, top="cobble")
    for k in range(6):
        x = -50 + k * 20
        I.light(col, f"Patio_light{k}", x, SS + 3, -1.8, "patio", intensity=4, range_m=7)
    I.light(col, "NorthPorch_light1", -40, 731, 9.5, "north_porch", intensity=4, range_m=8)
    I.light(col, "NorthPorch_light2", 40, 731, 9.5, "north_porch", intensity=4, range_m=8)


# --------------------------------------------------------------------------
ROOM_LIGHTS = [
    # (group, label, X, S, Z_ceiling, kind, switch (X, S, Z, facing))
    ("theater", "theater", -48, 744, -1.2, "globe", (-36.8, 750.4, -7.5)),
    ("wine", "wine cellar", -31, 744, -1.2, "globe", (-28.3, 750.4, -7.5)),
    ("parts", "parts library", -19, 744, -1.2, "globe", (-18.3, 750.4, -7.5)),
    ("walkout_hall", "walkout hall", 0, 753.5, -1.2, "globe", (3.5, 752, -7.5)),
    ("safe", "safe room", 18, 744, -1.2, "globe", (19.7, 750.4, -7.5)),
    ("elec", "electrical room", 29, 744, -1.2, "globe", (30.7, 750.4, -7.5)),
    ("mech", "mechanical room", 47, 744, -1.2, "globe", (48.7, 750.4, -7.5)),
    ("guest", "guest suite", -48, 770, -1.2, "bowl", (-36.8, 756.8, -7.5)),
    ("suite5", "suite 5", -24, 770, -1.2, "bowl", (-14.3, 756.8, -7.5)),
    ("gallery", "gallery", 0, 770, -1.2, "lantern", (-11.4, 757, -7.5)),
    ("rec", "rec room", 27, 770, -1.2, "lantern", (19.3, 756.8, -7.5)),
    ("gym", "gym", 51, 770, -1.2, "bowl", (51.7, 756.8, -7.5)),
    ("primary", "primary suite", -47, 770, 10, "lantern", (-35.0, 755.0, 3.5)),
    ("mudroom", "mudroom", -28, 744, 10, "globe", (-26.3, 750.4, 3.5)),
    ("foyer", "foyer", 0, 744, 10, "lantern", (-3.5, 738, 3.5)),
    ("main_hall", "hall", 20, 753.5, 10, "globe", (12.7, 752, 3.5)),
    ("butler", "butler's pantry", 20, 744, 10, "globe", (22.7, 750.4, 3.5)),
    ("scullery", "scullery", 48, 744, 10, "globe", (47.7, 750.4, 3.5)),
    ("library", "library", -25, 770, 10, "lantern", (-26.3, 756.8, 3.5)),
    ("great", "great room", 0, 770, 10, "lantern", (3.8, 756.8, 3.5)),
    ("dining", "dining room", 25, 770, 10, "lantern", (18.5, 756.8, 3.5)),
    ("kitchen", "kitchen", 47, 770, 10, "bowl", (36.5, 756.8, 3.5)),
    ("suite1", "suite 1", -48, 770, 20, "bowl", (-46.3, 756.8, 14.5)),
    ("suite2", "suite 2", -24, 770, 20, "bowl", (-22.3, 756.8, 14.5)),
    ("lounge", "lounge", 0, 770, 20, "lantern", (-11.4, 757, 14.5)),
    ("suite3", "suite 3", 24, 770, 20, "bowl", (25.7, 756.8, 14.5)),
    ("suite4", "suite 4", 48, 770, 20, "bowl", (49.7, 756.8, 14.5)),
    ("second_hall", "upper hall", -20, 753.5, 20, "globe", (-3.5, 752, 14.5)),
    ("dressing", "dressing rooms", -48, 744, 20, "globe", (-46.3, 750.4, 14.5)),
]


def lights(g, col):
    for group, label, X, S, zc, kind, sw in ROOM_LIGHTS:
        drop = {"lantern": 3.0, "bowl": 1.2, "globe": 0.8}[kind]
        I.pendant(col, g, f"Lamp_{group}", X, S, zc, drop, group, shade=1.4 if kind == "lantern" else 1.0,
                  kind=kind, intensity=14 if kind == "lantern" else 9, range_m=12)
        I.switch(col, f"Switch_{group}", sw[0], sw[1], sw[2], group, f"{label} lights")


def build(col, g, gn):
    exterior(g, col)
    exterior_doors(col, g)
    partitions(g, col)
    floors(g)
    stairs(g)
    elevator(g, col)
    roof(g, gn)
    masonry_heater(g, col)
    porches(g, col)
    lights(g, col)
