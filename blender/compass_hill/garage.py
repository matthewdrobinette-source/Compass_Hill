"""Garage (48 x 30), west loop, covered cart ramp down to the garage lobby, vault stair."""

from . import interact as I
from . import layout as L
from .common import Geo, wall_s, wall_x
from .site import rect

X0, X1, S0, S1 = L.GARAGE  # -190, -142, 612, 642


def build(col, g, gn):
    z0 = 0.0
    h = 11.0
    t = 1.2
    # east and west: big drive-through doors; north and south: walk-in doors on the 6-ft cart aisle
    xm = (X0 + X1) / 2  # -166
    wall_s(g, "limestone", S0 + t, S1 - t, X0, X0 + t, z0, z0 + h, [(617, 637, z0, z0 + 9)], fmat={"e": "plaster"})
    wall_s(g, "limestone", S0 + t, S1 - t, X1 - t, X1, z0, z0 + h, [(617, 637, z0, z0 + 9)], fmat={"w": "plaster"})
    wall_x(g, "limestone", X0, X1, S0, S0 + t, z0, z0 + h, [(xm - 1.5, xm + 1.5, z0, z0 + 7.5), (-186, -180, 4, 8), (-152, -146, 4, 8)], fmat={"s": "plaster"})
    wall_x(g, "limestone", X0, X1, S1 - t, S1, z0, z0 + h, [(xm - 1.5, xm + 1.5, z0, z0 + 7.5)], fmat={"n": "plaster"})
    g.box("polished_concrete", X0, X1, S0, S1, -1.0, 0.0, skip=("bottom",))
    g.box("safety_yellow", xm - 3, xm - 2.8, S0 + t, S1 - t, 0.0, 0.02)
    g.box("safety_yellow", xm + 2.8, xm + 3, S0 + t, S1 - t, 0.0, 0.02)
    # roof: slate north, standing seam + PV south; ridge east-west
    e = 2.0
    zt = z0 + h
    sm = (S0 + S1) / 2
    zr = zt + (15 + e) * 8 / 12
    g.face("slate", [(X0 - e, S0 - e, zt), (X1 + e, S0 - e, zt), (X1 + e, sm, zr), (X0 - e, sm, zr)][::-1])
    g.face("standing_seam", [(X1 + e, S1 + e, zt), (X0 - e, S1 + e, zt), (X0 - e, sm, zr), (X1 + e, sm, zr)][::-1])
    g.face("plaster_ceiling", [(X0, S0, zt), (X1, S0, zt), (X1, S1, zt), (X0, S1, zt)])
    for x, rev in ((X0, True), (X1, False)):
        tri = [(x, S0, zt), (x, S1, zt), (x, sm, zr - 0.6)]
        g.face("limestone", tri if rev else tri[::-1])
    slope = (zr - zt) / (15 + e)
    for row in range(3):
        sa, sb = sm + 1 + row * 5.4, sm + 1 + row * 5.4 + 5.1
        za, zb = zr - (sa - sm) * slope + 0.3, zr - (sb - sm) * slope + 0.3
        for c in range(13):
            xa = X0 + 1 + c * 3.6
            gn.face("pv", [(xa, sb, zb), (xa + 3.4, sb, zb), (xa + 3.4, sa, za), (xa, sa, za)])
    # overhead doors (roll up) east and west
    for name, x in (("GarageDoorEast", X1 - 0.6), ("GarageDoorWest", X0 + 0.6)):
        d = Geo()
        for k in range(6):
            d.box("oak", -0.15, 0.15, 0, 20, k * 1.5, k * 1.5 + 1.45)
        I.sliding(col, d, name, (x, 617, z0), "garage door", dz=8.5)
    I.hinged_door_x(col, "GarageDoorNorth", xm - 1.5, S0 + 0.6, z0, 3, +1, False, "garage walk-in door")
    I.hinged_door_x(col, "GarageDoorSouth", xm - 1.5, S1 - 0.6, z0, 3, +1, True, "garage walk-in door")
    I.switch(col, "Switch_garage", xm + 2.0, S1 - 1.3, 4.0, "garage", "garage lights")
    for k, x in enumerate((-180, -166, -152)):
        I.pendant(col, gn, f"GarageLamp_{k}", x, 627, 11.0, 1.0, "garage", kind="bowl", intensity=8)
    # EV chargers on the south wall
    for x in (-184, -150):
        g.box("stainless", x, x + 1.2, S1 - t - 0.5, S1 - t, 3, 5)
    # vault exterior stair (north side): lift-out hatch + stair down to the vault door
    g.box("limestone", -187, -185.8, 598, 612, -11, 1.0)
    g.box("limestone", -180.2, -179, 598, 612, -11, 1.0)
    g.box("limestone", -187, -179, 597, 598.2, -11, 1.0)
    for i in range(1, 19):
        top = -11 + i * 11 / 18
        g.box("limestone_smooth", -185.8, -180.2, 612 - i * 0.72 - 0.8, 612 - (i - 1) * 0.72 - 0.8 + 0.01, top - 0.8, top) if False else None
    for i in range(18):
        top = -11 + (i + 1) * 11 / 18
        sa = 599 + i * 0.68
        g.box("limestone_smooth", -185.8, -180.2, 611.9 - (i + 1) * 0.72, 611.9 - i * 0.72, top - 0.8, top) if False else None
    # (simpler) stair rising north from the vault door at S 611 to grade at S 598
    for i in range(1, 19):
        top = -11 + i * 11 / 18
        s1 = 611.0 - (i - 1) * 0.7
        g.box("limestone_smooth", -185.8, -180.2, s1 - 0.7, s1, top - 0.8, top)
    g.box("concrete", -185.8, -180.2, 611, 612, -12, -11)
    g.box("black_iron", -185.8, -185.7, 598, 611, 1.0, 3.8)
    g.box("black_iron", -180.3, -180.2, 598, 611, 1.0, 3.8)
    # vault door (the vaults open to the outside, never to the tunnel)
    I.hinged_door_x(col, "VaultDoor", -185.4, 612.0, -11, 4.8, +1, True, "LFP battery vault (authorized only)",
                    mat="stainless", height=7)
    # vaults + inverter room box structure below grade (sealed)
    g.box("concrete", X0 + 2, X1 - 2, S0 + 1, S1 + 3, -12.5, -11.8, skip=("top",))
    # covered cart ramp from the garage loop down to the garage lobby (-290 -> -178)
    ra, rb = -290.0, -178.0
    n = 28
    for i in range(n):
        xa = ra + (rb - ra) * i / n
        xb = ra + (rb - ra) * (i + 1) / n
        za = 0.0 - 11.0 * i / n
        zb = 0.0 - 11.0 * (i + 1) / n
        g.face("concrete", [(xa, 685, za), (xb, 685, zb), (xb, 675, zb), (xa, 675, za)])
    for s0, s1 in ((673.8, 675.0), (685.0, 686.2)):
        g.box("limestone", ra, rb, s0, s1, -12.0, 2.5, fmat={"n" if s0 > 680 else "s": "limestone"})
    # ramp roof on oak posts (standing seam to keep it light), drains top and bottom
    for x in range(-288, -178, 12):
        for s in (673.6, 686.4):
            g.box("oak_timber", x - 0.4, x + 0.4, s - 0.4, s + 0.4, 2.5, 11.0)
    g.face("slate", [(ra - 2, 671.5, 11.0), (rb + 2, 671.5, 11.0), (rb + 2, 680, 14.0), (ra - 2, 680, 14.0)][::-1])
    g.face("slate", [(rb + 2, 688.5, 11.0), (ra - 2, 688.5, 11.0), (ra - 2, 680, 14.0), (rb + 2, 680, 14.0)][::-1])
    g.box("black_iron", ra, ra + 1.0, 675, 685, 0.0, 0.05)
    g.box("black_iron", rb - 1.0, rb, 675, 685, -11.0, -10.95)
    for k, x in enumerate((-280, -250, -220, -190)):
        I.light(col, f"RampLight_{k}", x, 680, 9.5, "tunnels", intensity=4, range_m=10)
    # the ramp's east end is enclosed by the lobby's west wall opening (built in court.tunnels)
    # carts
    return [rect(-290, -178, 674.2, 685.8), rect(-186, -180, 598.2, 611.8)]
