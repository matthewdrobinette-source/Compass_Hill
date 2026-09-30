"""Entrance complex: separator berm, lay-by, teardrop, gate, gate buildings, mailbox."""

import math

from . import interact as I
from . import layout as L
from .common import Geo, wall_s, wall_x


def gable_building(g, x0, x1, s0, s1, z0, h, pitch=10 / 12, ridge="s", doors=(), windows=(), name=""):
    """Limestone building with an S1 slate gable roof. ridge runs along S ('s') or X ('x')."""
    t = 1.2
    wall_x(g, "limestone", x0, x1, s0, s0 + t, z0, z0 + h, [o[1:] for o in doors + windows if o[0] == "n"], fmat={"s": "plaster"})
    wall_x(g, "limestone", x0, x1, s1 - t, s1, z0, z0 + h, [o[1:] for o in doors + windows if o[0] == "s"], fmat={"n": "plaster"})
    wall_s(g, "limestone", s0 + t, s1 - t, x0, x0 + t, z0, z0 + h, [o[1:] for o in doors + windows if o[0] == "w"], fmat={"e": "plaster"})
    wall_s(g, "limestone", s0 + t, s1 - t, x1 - t, x1, z0, z0 + h, [o[1:] for o in doors + windows if o[0] == "e"], fmat={"w": "plaster"})
    g.box("cobble", x0 + t, x1 - t, s0 + t, s1 - t, z0 - 0.5, z0 + 0.05, skip=("bottom",))
    e = 1.5
    zt = z0 + h
    if ridge == "s":
        half = (x1 - x0) / 2 + e
        zr = zt + half * pitch
        xm = (x0 + x1) / 2
        g.face("slate", [(x0 - e, s1 + e, zt), (x0 - e, s0 - e, zt), (xm, s0 - e, zr), (xm, s1 + e, zr)][::-1])
        g.face("slate", [(x1 + e, s0 - e, zt), (x1 + e, s1 + e, zt), (xm, s1 + e, zr), (xm, s0 - e, zr)][::-1])
        g.face("plaster_ceiling", [(x0, s0, zt), (x1, s0, zt), (x1, s1, zt), (x0, s1, zt)])
        for s, rev in ((s0, False), (s1, True)):
            tri = [(x0, s, zt), (x1, s, zt), (xm, s, zr - 0.6)]
            g.face("limestone", tri if rev else tri[::-1])
    else:
        half = (s1 - s0) / 2 + e
        zr = zt + half * pitch
        sm = (s0 + s1) / 2
        g.face("slate", [(x0 - e, s0 - e, zt), (x1 + e, s0 - e, zt), (x1 + e, sm, zr), (x0 - e, sm, zr)][::-1])
        g.face("slate", [(x1 + e, s1 + e, zt), (x0 - e, s1 + e, zt), (x0 - e, sm, zr), (x1 + e, sm, zr)][::-1])
        g.face("plaster_ceiling", [(x0, s0, zt), (x1, s0, zt), (x1, s1, zt), (x0, s1, zt)])
        for x, rev in ((x0, True), (x1, False)):
            tri = [(x, s0, zt), (x, s1, zt), (x, sm, zr - 0.6)]
            g.face("limestone", tri if rev else tri[::-1])


def build(col, g, gn):
    z = L.pave_z
    # separator berm (planted), ends ~35 ft short of the connectors
    for i in range(22):
        x0 = -107 + i * 10
        x1 = x0 + 10
        zb = -8.0
        g.face("lawn", [(x0, 15, zb), (x1, 15, zb), (x1, 26, zb + 4.5), (x0, 26, zb + 4.5)][::-1])
        g.face("lawn", [(x0, 26, zb + 4.5), (x1, 26, zb + 4.5), (x1, 37, zb), (x0, 37, zb)][::-1])
    # mailbox just east of the exit connector, cast-iron post
    g.box("black_iron", 220, 220.35, 3.0, 3.35, -8, -4.4)
    g.box("mailbox", 219.4, 221.0, 2.4, 3.9, -4.4, -3.4)
    # call boxes at cab height and standing height
    for s, h in ((96, 4.0), (100, 9.0)):
        g.box("stainless", -17.5, -16.5, s, s + 0.8, z(-17, s), z(-17, s) + h)
    zb = z(0, L.GATE_S)
    # gate buildings: carriage house (west) and gatehouse (east), limestone + slate
    s0, s1 = L.GATE_BUILDING_S
    gable_building(g, -40, -14, s0, s1, zb, 10.0, ridge="s",
                   doors=[("e", 236, 246, zb, zb + 8.5), ("n", -38, -16, zb, zb + 8.5)], windows=[("w", 226, 232, zb + 3, zb + 7), ("w", 244, 250, zb + 3, zb + 7)])
    gable_building(g, 14, 40, s0, s1, zb, 10.0, ridge="s",
                   doors=[("w", 240, 243.5, zb, zb + 7.2), ("n", 16, 38, zb, zb + 8.5)], windows=[("e", 232, 238, zb + 3, zb + 7), ("e", 246, 252, zb + 3, zb + 7)])
    # outer 20 ft of each: open porch/alcove (north end opened up)
    for x0, x1 in ((-40, -14), (14, 40)):
        g.box("cobble", x0, x1, s0 - 0.01, s0 + 20, zb - 0.4, zb + 0.06, skip=("bottom",))
    # gatehouse alcove: pass-through parcel lockers on the back wall, intercom
    for k in range(6):
        g.box("bronze_frame", 17 + k * 3.6, 19.8 + k * 3.6, s0 + 19.3, s0 + 19.9, zb + 0.5, zb + 6.5)
    g.box("stainless", 15.3, 15.9, s0 + 10, s0 + 11, zb + 4, zb + 5.2)
    g.box("oak", -38, -30, s0 + 3, s0 + 4.5, zb, zb + 1.5)   # porch bench
    # interior dividers between outer 20 and inner 40
    wall_x(g, "limestone", -38.8, -15.2, s0 + 19.4, s0 + 20.4, zb, zb + 10, [(-30, -24, zb, zb + 7.5)])
    wall_x(g, "limestone", 15.2, 38.8, s0 + 19.4, s0 + 20.4, zb, zb + 10, [])
    I.hinged_door_s(col, "GatehouseDoor", 14.6, 240, zb, 3.5, +1, opens_east=True, label="gatehouse equipment room")
    I.hinged_door_s(col, "CarriageHouseDoorL", -14.6, 236, zb, 5, +1, opens_east=False, label="carriage house doors",
                    height=8.5, pair="CarriageHouseDoorR")
    I.hinged_door_s(col, "CarriageHouseDoorR", -14.6, 246, zb, 5, -1, opens_east=False, label="carriage house doors",
                    height=8.5, pair="CarriageHouseDoorL")
    # gate: 24-ft trackless cantilever, retracts west into the carriage house wall pocket
    gate = Geo()
    gate.box("black_iron", 0, 24, -0.2, 0.2, 0.3, 0.6)
    gate.box("black_iron", 0, 24, -0.2, 0.2, 6.2, 6.5)
    gate.box("black_iron", 0, 24, -0.15, 0.15, 3.2, 3.4)
    for k in range(49):
        x = k * 0.5
        gate.box("black_iron", x - 0.05, x + 0.05, -0.06, 0.06, 0.3, 7.0 if k % 2 == 0 else 6.5)
        if k % 2 == 0:
            gate.cone("black_iron", x, 0, 0.12, 7.0, 7.35, seg=4)
    I.sliding(col, gate, "EntryGate", (-12, L.GATE_S, zb), "the gate", dx=-23.5, collide=1)
    g.box("limestone", -15.0, -12.2, L.GATE_S - 1.4, L.GATE_S + 1.4, zb, zb + 8.2)   # pocket pier
    g.box("limestone", 12.2, 15.0, L.GATE_S - 1.4, L.GATE_S + 1.4, zb, zb + 8.2)
    g.box("limestone_smooth", -15.3, -11.9, L.GATE_S - 1.7, L.GATE_S + 1.7, zb + 8.2, zb + 8.8)
    g.box("limestone_smooth", 11.9, 15.3, L.GATE_S - 1.7, L.GATE_S + 1.7, zb + 8.2, zb + 8.8)
    btn = Geo()
    btn.box("stainless", -0.3, 0.3, -0.3, 0.3, 0, 4.2)
    btn.box("button", -0.18, 0.18, -0.31, -0.3, 3.2, 3.6)
    btn.to_object("GateCallBox", col, local_at=(17.5, L.GATE_S - 6, zb),
                  props={"interact": "operate", "target": "EntryGate", "label": "open the gate"})
    btn2 = Geo()
    btn2.box("stainless", -0.3, 0.3, -0.3, 0.3, 0, 4.2)
    btn2.box("button", -0.18, 0.18, 0.3, 0.31, 3.2, 3.6)
    btn2.to_object("GateExitButton", col, local_at=(17.5, L.GATE_S + 8, zb),
                   props={"interact": "operate", "target": "EntryGate", "label": "open the gate"})
    # shielded motion lights
    for x in (-27, 27):
        I.light(col, f"GateLight_{x}", x, L.GATE_S - 12, zb + 9.0, "gate", intensity=5, range_m=10)
    # teardrop island planting: limestone boulders
    tc = L.TEARDROP_C
    for k in range(5):
        a = k * 72
        gn.sphere("fieldstone", tc[0] + 9 * math.cos(math.radians(a)), tc[1] - 9 * math.sin(math.radians(a)),
                  z(tc[0], tc[1]) + 0.3, 2.2, 1.6, 1.2, seg=8, rings=5)
    # four-board black horse fence along the frontage (Warren County farm idiom)
    for x0 in range(-445, 445, 10):
        if -215 < x0 < 215:
            continue
        for k in range(4):
            zz = -8 + 1.1 + k * 1.05
            g.box("board_fence", x0, x0 + 10, 16.0, 16.15, zz, zz + 0.5)
        g.box("board_fence", x0 - 0.2, x0 + 0.2, 15.9, 16.3, -8, -3.3)
