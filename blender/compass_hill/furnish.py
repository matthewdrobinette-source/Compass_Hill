"""Furniture, vehicles, deer. Kept simple (boxes), scaled to real sizes (feet)."""

import math
import random

from . import interact as I
from . import layout as L
from .common import Geo

rnd = random.Random(1788)  # the Ohio Company lands at Marietta


def rug(gn, x0, x1, s0, s1, z, mat="rug_wool"):
    gn.box(mat, x0, x1, s0, s1, z, z + 0.04, skip=("bottom",))


def bed(g, gn, x, s, z, head="n", w=6.5, l=7.0, blanket="fabric_green"):
    if head in ("n", "s"):
        hs = s - l / 2 if head == "n" else s + l / 2
        g.box("oak", x - w / 2, x + w / 2, s - l / 2, s + l / 2, z, z + 1.3)
        g.box("fabric_linen", x - w / 2 + 0.2, x + w / 2 - 0.2, s - l / 2 + 0.2, s + l / 2 - 0.2, z + 1.3, z + 2.2)
        g.box(blanket, x - w / 2 + 0.1, x + w / 2 - 0.1, s - l / 2 + 2.5 if head == "n" else s - l / 2 + 0.1,
              s + l / 2 - 0.1 if head == "n" else s + l / 2 - 2.5, z + 2.2, z + 2.35)
        g.box("oak", x - w / 2, x + w / 2, hs - 0.25, hs + 0.25, z, z + 4.5)
        for dx in (-1.5, 1.5):
            ps = s - l / 2 + 1.0 if head == "n" else s + l / 2 - 1.0
            g.box("fabric_linen", x + dx - 1.1, x + dx + 1.1, ps - 0.6, ps + 0.6, z + 2.2, z + 2.8)
        for dx in (-w / 2 - 1.6, w / 2 + 0.2):
            g.box("oak", x + dx, x + dx + 1.4, hs - 0.8 if head == "n" else hs - 0.7, hs + 0.7 if head == "n" else hs + 0.8,
                  z, z + 2.0)
    else:
        hx = x - l / 2 if head == "w" else x + l / 2
        g.box("oak", x - l / 2, x + l / 2, s - w / 2, s + w / 2, z, z + 1.3)
        g.box("fabric_linen", x - l / 2 + 0.2, x + l / 2 - 0.2, s - w / 2 + 0.2, s + w / 2 - 0.2, z + 1.3, z + 2.2)
        g.box(blanket, x - l / 2 + 2.5 if head == "w" else x - l / 2 + 0.1, x + l / 2 - 0.1 if head == "w" else x + l / 2 - 2.5,
              s - w / 2 + 0.1, s + w / 2 - 0.1, z + 2.2, z + 2.35)
        g.box("oak", hx - 0.25, hx + 0.25, s - w / 2, s + w / 2, z, z + 4.5)
        for ds in (-1.5, 1.5):
            px = x - l / 2 + 1.0 if head == "w" else x + l / 2 - 1.0
            g.box("fabric_linen", px - 0.6, px + 0.6, s + ds - 1.1, s + ds + 1.1, z + 2.2, z + 2.8)


def sofa(g, x, s, z, facing, length=8.0, mat="fabric_linen"):
    d = 3.0
    if facing in ("n", "s"):
        g.box(mat, x - length / 2, x + length / 2, s - d / 2, s + d / 2, z, z + 1.5)
        bs = s + d / 2 - 0.7 if facing == "n" else s - d / 2
        g.box(mat, x - length / 2, x + length / 2, bs, bs + 0.7, z, z + 2.8)
        for dx in (-length / 2, length / 2 - 0.6):
            g.box(mat, x + dx, x + dx + 0.6, s - d / 2, s + d / 2, z, z + 2.1)
    else:
        g.box(mat, x - d / 2, x + d / 2, s - length / 2, s + length / 2, z, z + 1.5)
        bx = x + d / 2 - 0.7 if facing == "w" else x - d / 2
        g.box(mat, bx, bx + 0.7, s - length / 2, s + length / 2, z, z + 2.8)
        for ds in (-length / 2, length / 2 - 0.6):
            g.box(mat, x - d / 2, x + d / 2, s + ds, s + ds + 0.6, z, z + 2.1)


def chair(g, x, s, z, mat="leather", facing="n", size=2.6):
    h = size / 2
    g.box(mat, x - h, x + h, s - h, s + h, z, z + 1.5)
    if facing == "n":
        g.box(mat, x - h, x + h, s + h - 0.5, s + h, z, z + 3.0)
    elif facing == "s":
        g.box(mat, x - h, x + h, s - h, s - h + 0.5, z, z + 3.0)
    elif facing == "e":
        g.box(mat, x - h, x - h + 0.5, s - h, s + h, z, z + 3.0)
    else:
        g.box(mat, x + h - 0.5, x + h, s - h, s + h, z, z + 3.0)


def table(g, x0, x1, s0, s1, z, h=2.5, mat="oak"):
    g.box(mat, x0, x1, s0, s1, z + h - 0.2, z + h)
    for x in (x0 + 0.3, x1 - 0.6):
        for s in (s0 + 0.3, s1 - 0.6):
            g.box(mat, x, x + 0.3, s, s + 0.3, z, z + h - 0.2)


def dining_chair(g, x, s, z, facing):
    g.box("oak", x - 0.8, x + 0.8, s - 0.8, s + 0.8, z + 1.5, z + 1.65)
    for dx in (-0.7, 0.55):
        for ds in (-0.7, 0.55):
            g.box("oak", x + dx, x + dx + 0.15, s + ds, s + ds + 0.15, z, z + 1.5)
    if facing == "n":
        g.box("oak", x - 0.8, x + 0.8, s + 0.65, s + 0.8, z + 1.65, z + 3.4)
    elif facing == "s":
        g.box("oak", x - 0.8, x + 0.8, s - 0.8, s - 0.65, z + 1.65, z + 3.4)
    elif facing == "e":
        g.box("oak", x - 0.8, x - 0.65, s - 0.8, s + 0.8, z + 1.65, z + 3.4)
    else:
        g.box("oak", x + 0.65, x + 0.8, s - 0.8, s + 0.8, z + 1.65, z + 3.4)


def shelves_x(g, x0, x1, s0, s1, z, h=8.0, mat="oak", fill="book_mix"):
    g.box(mat, x0, x1, s0, s1, z, z + h)
    n = int(h / 1.3)
    for k in range(1, n):
        zz = z + k * 1.3
        g.box(fill, x0 + 0.1, x1 - 0.1, s0 - 0.05, s1 + 0.05, zz - 1.0, zz - 0.1)


def house(g, gn, col):
    zw, zm, z2 = -11.0, 0.0, 11.0
    # --- walkout
    # theater: screen (toggle) on the west wall, two rows of leather seats
    scr = Geo()
    scr.box("screen_off", 0, 0.15, -4.8, 4.8, 0, 5.4)
    scr.to_object("TheaterScreen", col, local_at=(-58.9, 744, zw + 2.5),
                  props={"interact": "toggle", "label": "theater screen", "emit": "#9ec3ff"})
    for row, x in enumerate((-49, -43)):
        for s in (740.5, 744.0, 747.5):
            chair(g, x, s, zw + row * 0.8, mat="leather", facing="e", size=3.0)
        if row:
            g.box("oak", -47, -44.5, 738, 750, zw, zw + 0.8)
    rug(gn, -58, -37, 738, 750, zw, "fabric_rust")
    # wine cellar racks
    for s0 in (737.2, 749.3):
        shelves_x(g, -35.5, -26.5, s0, s0 + 1.4, zw, 7.5, "oak", "brick")
    # parts library: steel shelving with labeled blue bins
    for s0 in (737.2, 741.5, 745.8):
        shelves_x(g, -25.5, -12.8, s0, s0 + 1.6, zw, 7.5, "steel_shelf", "bin_blue")
    # safe room
    g.box("oak", 13, 23, 737.3, 739, zw, zw + 1.6)
    shelves_x(g, 22.2, 23.7, 740, 750, zw, 7, "steel_shelf", "tank_white") if False else None
    # electrical/IT: panels and a rack
    for k in range(3):
        g.box("steel_shelf", 24.6 + k * 3, 26.8 + k * 3, 737.2, 738.2, zw + 1, zw + 7)
    g.box("black_iron", 31.5, 33.5, 745, 748, zw, zw + 7)
    # mechanical: heat storage tank, heat pumps, ERVs, pipe runs
    g.cylinder("tank_white", 47, 743.5, 4.5, zw, zw + 9.2, seg=24)
    for k in range(3):
        g.box("tank_white", 36 + k * 3.5, 38.8 + k * 3.5, 737.3, 740, zw, zw + 4.5)
    g.box("steel_shelf", 55, 59, 737.5, 742, zw, zw + 6)
    g.box("pipe_red", 36, 58, 749.6, 750.1, zw + 8.5, zw + 9)
    g.box("pipe_blue", 36, 58, 749.6, 750.1, zw + 7.6, zw + 8.1)
    # guest suite, suite 5
    bed(g, gn, -48, 772, zw, head="n", blanket="fabric_green")
    rug(gn, -55, -41, 764, 781, zw)
    bed(g, gn, -24, 772, zw, head="n", blanket="fabric_rust")
    rug(gn, -31, -17, 764, 781, zw)
    # gallery: long bench, rug
    g.box("oak", -6, 6, 764, 766, zw, zw + 1.5)
    rug(gn, -9, 9, 760, 780, zw, "fabric_rust")
    # rec room: billiards (Ohio slate bed), bar with stools, sofa
    g.box("oak", 22, 30, 765, 769.5, zw, zw + 2.4)
    g.box("felt_green", 22.3, 29.7, 765.3, 769.2, zw + 2.4, zw + 2.5)
    g.box("oak", 38, 41, 758, 781, zw, zw + 3.5)
    g.box("soapstone", 37.8, 41.2, 758, 781, zw + 3.5, zw + 3.7)
    for s in range(760, 781, 4):
        g.cylinder("leather", 36.5, s, 0.8, zw, zw + 2.6, seg=10)
    sofa(g, 16.5, 772, zw, "e", 9)
    # gym
    rug(gn, 44, 58, 760, 781, zw, "rubber")
    g.box("black_iron", 45, 50, 776, 778, zw, zw + 1.2)
    # --- main level
    # primary suite
    bed(g, gn, -47, 773, zm, head="w", w=7, l=7.5, blanket="fabric_green")
    rug(gn, -56, -38, 764, 782, zm)
    chair(g, -38.5, 760, zm, facing="w")
    g.box("white_paint", -58, -52, 740, 743, zm, zm + 2)   # cast-iron tub
    g.box("oak", -44, -36, 737.3, 739.3, zm, zm + 3)      # vanity
    g.box("soapstone", -44.1, -35.9, 737.2, 739.4, zm + 3, zm + 3.15)
    # mudroom: oak lockers and bench
    g.box("oak", -33.5, -22.5, 737.3, 739, zm, zm + 7.5)
    g.box("oak", -33.5, -22.5, 739, 741, zm, zm + 1.5)
    # foyer: round table + rug
    g.cylinder("oak", 0, 745, 2.2, zm + 2.6, zm + 2.8, seg=20)
    g.cylinder("oak", 0, 745, 0.4, zm, zm + 2.6, seg=8)
    rug(gn, -3.5, 3.5, 739, 750, zm + 0.02, "fabric_rust")
    # butler's pantry and scullery
    g.box("oak", 12.5, 27.5, 737.3, 739.3, zm, zm + 3)
    g.box("soapstone", 12.4, 27.6, 737.2, 739.4, zm + 3, zm + 3.15)
    g.box("oak", 12.5, 27.5, 737.3, 738.5, zm + 5, zm + 8)
    g.box("oak", 36.5, 59, 737.3, 739.3, zm, zm + 3)
    g.box("soapstone", 36.4, 59, 737.2, 739.4, zm + 3, zm + 3.15)
    g.box("oak", 57, 58.8, 739.5, 750.5, zm, zm + 7.5)
    # library: shelves on the north and west walls, desk, leather chairs
    shelves_x(g, -33.6, -16.4, 756.3, 757.8, zm, 9.5)
    g.box("oak", -33.6, -32.1, 758, 782, zm, zm + 9.5)
    for k in range(7):
        zz = zm + 1.3 * (k + 1)
        g.box("book_mix", -32.2, -32.0, 758.2, 781.8, zz - 1.0, zz - 0.1)
    g.box("oak", -28, -22, 772, 775, zm + 2.3, zm + 2.5)
    g.box("oak", -28, -22, 772, 775, zm, zm + 2.3) if False else None
    for x in (-27.7, -22.4):
        g.box("oak", x, x + 0.3, 772.2, 774.8, zm, zm + 2.3)
    chair(g, -25, 776.5, zm, facing="n", size=2.2)
    chair(g, -29, 765, zm, facing="e")
    chair(g, -21, 765, zm, facing="w")
    rug(gn, -31, -19, 760, 780, zm, "fabric_rust")
    # great room: sofas around a coffee table facing the heater, grand piano
    rug(gn, -12, 6, 760, 778, zm)
    sofa(g, -2, 769, zm, "w", 9, "fabric_linen")
    sofa(g, -7, 776.5, zm, "n", 8, "fabric_green")
    sofa(g, -7, 761.5, zm, "s", 8, "fabric_green")
    g.box("oak", -9, -5, 766, 772, zm, zm + 1.4)
    g.box("black_iron", 8, 14, 762, 768, zm + 2.3, zm + 3.2)    # piano case
    for x, s in ((8.5, 762.5), (13, 762.5), (10.5, 767.2)):
        g.box("black_iron", x, x + 0.4, s, s + 0.4, zm, zm + 2.3)
    # dining: long white-oak table seating twelve
    table(g, 19, 31, 766.5, 772.5, zm, 2.5)
    for x in (20.5, 23, 25.5, 28, 30.5):
        dining_chair(g, x, 765.2, zm, "n")
        dining_chair(g, x, 773.8, zm, "s")
    dining_chair(g, 17.7, 769.5, zm, "e")
    dining_chair(g, 32.3, 769.5, zm, "w")
    rug(gn, 17, 33, 763, 776, zm, "fabric_rust")
    # kitchen: white-oak cabinets from site oak, soapstone, induction cooktop (toggle), island
    g.box("oak", 57.3, 59, 757, 782, zm, zm + 3)
    g.box("soapstone", 57.1, 59, 757, 782, zm + 3, zm + 3.15)
    g.box("oak", 57.8, 59, 757, 782, zm + 5, zm + 8)
    g.box("oak", 42, 52, 765, 770, zm, zm + 3)
    g.box("soapstone", 41.8, 52.2, 764.8, 770.2, zm + 3, zm + 3.15)
    ck = Geo()
    ck.box("screen_off", -1.4, 1.4, -1.0, 1.0, 0, 0.05)
    ck.to_object("InductionCooktop", col, local_at=(47, 767.5, zm + 3.15),
                 props={"interact": "toggle", "label": "induction cooktop", "emit": "#ff4d1a"})
    g.box("stainless", 44.5, 49.5, 765.5, 769.5, zm + 7.5, zm + 9.99)   # hood (make-up air interlocked)
    for x in (43, 46, 49, 51.5):
        g.cylinder("leather", x, 771.5, 0.7, zm, zm + 2.6, seg=10)
    g.box("white_paint", 57.2, 59, 773, 776, zm, zm + 6.5)   # fridge panel
    # --- second floor
    for x, blanket in ((-48, "fabric_green"), (-24, "fabric_rust"), (24, "fabric_green"), (48, "fabric_rust")):
        bed(g, gn, x, 773, z2, head="n", blanket=blanket)
        rug(gn, x - 8, x + 8, 764, 782, z2)
        chair(g, x + 7, 761, z2, facing="s")
        g.box("oak", x - 9, x - 5, 757, 758.8, z2, z2 + 3.2)   # dresser
    sofa(g, 0, 777, z2, "n", 10, "fabric_linen")
    chair(g, -6, 766, z2, facing="e")
    chair(g, 6, 766, z2, facing="w")
    table(g, -2, 2, 764, 768, z2, 2.4)
    rug(gn, -10, 10, 760, 782, z2, "fabric_rust")
    # laundry: washer, dryer, folding counter
    for x in (36.6, 39.4):
        g.box("white_paint", x, x + 2.6, 737.3, 740, z2, z2 + 3.2)
    g.box("oak", 42.3, 45.6, 737.3, 745, z2, z2 + 3)
    # dressing rooms: closets + tubs
    for x0 in (-59, -35, 12.5, 46.5):
        g.box("oak", x0, x0 + 10, 737.3, 739.3, z2, z2 + 7.5)
        g.box("white_paint", x0 + 1, x0 + 6, 744, 747.5, z2, z2 + 2)


def car(g, x, s, ang, color="car_paint"):
    """Simple sedan/SUV, in the static Geo at (x, s) facing ang (deg)."""
    loc = Geo()
    loc.box(color, -8.0, 8.0, -3.1, 3.1, 1.2, 3.6)
    loc.box(color, -4.5, 3.5, -2.8, 2.8, 3.6, 5.6)
    loc.box("glass", -4.4, 3.4, -2.85, 2.85, 3.8, 5.4)
    for wx in (-5.2, 5.2):
        for ws in (-2.9, 2.9):
            loc.cylinder("rubber", wx, ws, 1.1, 0, 0.1, seg=10) if False else None
            loc.box("rubber", wx - 1.1, wx + 1.1, ws - 0.45, ws + 0.45, 0.0, 2.2)
    loc.box("lamp_warm", 7.95, 8.05, -2.6, -1.6, 2.6, 3.1)
    loc.box("lamp_warm", 7.95, 8.05, 1.6, 2.6, 2.6, 3.1)
    return loc


def golf_cart(col, name, x, s, z, ang, label="drive the golf cart"):
    """Drivable electric cart (forward = local +X)."""
    c = Geo()
    c.box("cart_white", -4.0, 4.0, -1.9, 1.9, 1.0, 2.2)
    c.box("cart_white", 2.2, 4.0, -1.9, 1.9, 2.2, 3.0)
    c.box("leather", -2.4, 0.8, -1.7, 1.7, 2.2, 3.0)
    c.box("leather", -2.4, -1.9, -1.7, 1.7, 3.0, 4.6)
    c.box("black_iron", 1.3, 1.5, -0.1, 0.1, 2.2, 4.2)
    c.cylinder("black_iron", 1.4, 0, 0.7, 4.1, 4.25, seg=12)  # steering wheel
    for px in (-3.8, 3.4):
        for ps in (-1.8, 1.8):
            c.box("black_iron", px - 0.1, px + 0.1, ps - 0.1, ps + 0.1, 2.2, 6.4)
    c.box("canvas_blue", -4.4, 4.2, -2.2, 2.2, 6.4, 6.7)
    c.box("glass", 3.5, 3.6, -1.7, 1.7, 3.2, 6.3)
    for wx in (-2.8, 2.8):
        for ws in (-1.85, 1.85):
            c.box("rubber", wx - 0.8, wx + 0.8, ws - 0.35, ws + 0.35, 0.0, 1.6)
    return c.to_object(name, col, local_at=(x, s, z), rot_deg=ang,
                       props={"interact": "cart", "label": label, "collide": 1})


def deer(gn, x, s, ang, grazing=False):
    loc = Geo()
    loc.sphere("fabric_rust", 0, 0, 3.2, 2.2, 0.9, 1.0, seg=8, rings=5)
    for lx in (-1.5, 1.4):
        for ls in (-0.45, 0.45):
            loc.cylinder("fabric_rust", lx, ls, 0.15, 0, 3.0, seg=5, caps=False)
    if grazing:
        loc.cylinder("fabric_rust", 2.3, 0, 0.35, 0.8, 3.4, seg=6, r_top=0.3)
        loc.sphere("fabric_rust", 2.6, 0, 0.8, 0.6, 0.35, 0.35, seg=6, rings=4)
    else:
        loc.cylinder("fabric_rust", 2.0, 0, 0.4, 3.4, 5.4, seg=6, r_top=0.3)
        loc.sphere("fabric_rust", 2.5, 0, 5.6, 0.75, 0.38, 0.4, seg=6, rings=4)
        loc.cone("fabric_rust", 2.1, -0.3, 0.15, 5.9, 6.5, seg=4)
        loc.cone("fabric_rust", 2.1, 0.3, 0.15, 5.9, 6.5, seg=4)
    loc.sphere("white_paint", -2.2, 0, 3.6, 0.35, 0.25, 0.3, seg=6, rings=4)
    return loc


def vehicles_and_wildlife(g, gn, col):
    from .court import PADS, polar
    import bpy
    z = 0.0
    for k, ang in enumerate(PADS):
        if k in (0, 2, 4):
            loc = car(g, 0, 0, 0, color=["car_paint", "cart_white", "black_iron"][k // 2])
            x, s = polar(42, ang)
            loc.to_object(f"Car_{k}", col, local_at=(x, s, z), rot_deg=ang + 180, props={"collide": 1})
    car(g, 0, 0, 0, "fabric_rust").to_object("Car_garage", col, local_at=(-173, 622, 0.0), rot_deg=0,
                                             props={"collide": 1})
    golf_cart(col, "GolfCart", 0, 726, -11.0, 90)
    golf_cart(col, "GolfCart2", -120, 640, 0.0, 180, label="drive the golf cart")
    for k, (x, s, a, gr) in enumerate(((-40, 1140, 30, True), (-30, 1152, 200, False), (40, 1195, 120, True))):
        d = deer(gn, 0, 0, a, gr)
        d.to_object(f"Deer_{k}", col, local_at=(x, s, L.terrain(x, s)), rot_deg=a, props={"collide": 0})


def build(col, g, gn):
    house(g, gn, col)
    vehicles_and_wildlife(g, gn, col)
