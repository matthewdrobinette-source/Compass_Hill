"""Interactive objects. Their custom properties become glTF 'extras', which the
walkthrough reads:

  interact = rotate | slide | switch | elevator | toggle | cart | sit
  label    = text shown in the prompt ("Open front door")
  rotate:  axis ('z' or 'x', Blender local), angle (degrees)
  slide:   dx, dy, dz (meters, Blender axes)
  switch:  group (lights with the same light_group turn on/off)
  toggle:  target (object name) — emissive/visibility toggle (screens, fire)
  pair:    another object's name that moves together (double doors)
  collide: 1 = solid while closed (dynamic collider)
"""

import math

from .common import FT, P, Geo, empty

DOORS = []


def _props(label, **kw):
    d = {"label": label, "collide": 1}
    d.update(kw)
    return d


def hinged_door_x(col, name, hinge_x, s_mid, z0, width, extends, opens_south, label,
                  mat="oak", height=7.0, thick=0.18, glass=False, pair=None):
    """Door in an east-west wall. extends: +1 panel runs east of the hinge, -1 west."""
    g = Geo()
    w = width * extends
    x0, x1 = (0, w) if w > 0 else (w, 0)
    if glass:
        fr = 0.35
        g.box("bronze_frame", x0, x1, -thick / 2, thick / 2, 0, fr)
        g.box("bronze_frame", x0, x1, -thick / 2, thick / 2, height - fr, height)
        g.box("bronze_frame", x0, x0 + fr, -thick / 2, thick / 2, fr, height - fr)
        g.box("bronze_frame", x1 - fr, x1, -thick / 2, thick / 2, fr, height - fr)
        g.box("glass", x0 + fr, x1 - fr, -0.03, 0.03, fr, height - fr)
    else:
        g.box(mat, x0, x1, -thick / 2, thick / 2, 0, height)
        # raised-panel lines (Federal six-panel suggestion)
        for zz in (1.0, 3.6, 5.6):
            for xa, xb in ((0.12, 0.46), (0.54, 0.88)):
                xa2, xb2 = x0 + (x1 - x0) * xa, x0 + (x1 - x0) * xb
                g.box(mat, xa2, xb2, -thick / 2 - 0.03, thick / 2 + 0.03, zz, zz + (1.4 if zz < 5 else 1.0))
    kx = w - 0.25 * extends
    g.sphere("bronze_ss", kx, -thick / 2 - 0.12, 3.1, 0.12, seg=8, rings=4)
    g.sphere("bronze_ss", kx, thick / 2 + 0.12, 3.1, 0.12, seg=8, rings=4)
    angle = 92 * extends * (1 if opens_south else -1) * -1
    props = _props(label, interact="rotate", axis="z", angle=angle)
    if pair:
        props["pair"] = pair
    obj = g.to_object(name, col, local_at=(hinge_x, s_mid, z0), props=props)
    DOORS.append(obj)
    return obj


def hinged_door_s(col, name, x_mid, hinge_s, z0, width, extends, opens_east, label,
                  mat="oak", height=7.0, thick=0.18, glass=False, pair=None):
    """Door in a north-south wall. extends: +1 panel runs south of the hinge."""
    g = Geo()
    w = width * extends
    s0, s1 = (0, w) if w > 0 else (w, 0)
    if glass:
        fr = 0.35
        g.box("bronze_frame", -thick / 2, thick / 2, s0, s1, 0, fr)
        g.box("bronze_frame", -thick / 2, thick / 2, s0, s1, height - fr, height)
        g.box("bronze_frame", -thick / 2, thick / 2, s0, s0 + fr, fr, height - fr)
        g.box("bronze_frame", -thick / 2, thick / 2, s1 - fr, s1, fr, height - fr)
        g.box("glass", -0.03, 0.03, s0 + fr, s1 - fr, fr, height - fr)
    else:
        g.box(mat, -thick / 2, thick / 2, s0, s1, 0, height)
        for zz in (1.0, 3.6, 5.6):
            for sa, sb in ((0.12, 0.46), (0.54, 0.88)):
                sa2, sb2 = s0 + (s1 - s0) * sa, s0 + (s1 - s0) * sb
                g.box(mat, -thick / 2 - 0.03, thick / 2 + 0.03, sa2, sb2, zz, zz + (1.4 if zz < 5 else 1.0))
    ks = w - 0.25 * extends
    g.sphere("bronze_ss", -thick / 2 - 0.12, ks, 3.1, 0.12, seg=8, rings=4)
    g.sphere("bronze_ss", thick / 2 + 0.12, ks, 3.1, 0.12, seg=8, rings=4)
    # panel toward +S is Blender -y; +90 deg about Z swings it toward +x (east)
    angle = 92 * extends * (1 if opens_east else -1)
    props = _props(label, interact="rotate", axis="z", angle=angle)
    if pair:
        props["pair"] = pair
    obj = g.to_object(name, col, local_at=(x_mid, hinge_s, z0), props=props)
    DOORS.append(obj)
    return obj


def double_door_x(col, name, x0, x1, s_mid, z0, opens_south, label, glass=False, height=7.5):
    w = (x1 - x0) / 2
    a = hinged_door_x(col, name + "_L", x0, s_mid, z0, w, +1, opens_south, label, glass=glass, height=height, pair=name + "_R")
    b = hinged_door_x(col, name + "_R", x1, s_mid, z0, w, -1, opens_south, label, glass=glass, height=height, pair=name + "_L")
    return a, b


def sliding(col, g, name, at, label, dx=0.0, dy=0.0, dz=0.0, collide=1, **extra):
    """g is a Geo in LOCAL feet; motion given in feet along site axes (X east, S south, Z up)."""
    props = _props(label, interact="slide", dx=dx * FT, dy=-dy * FT, dz=dz * FT)
    props["collide"] = collide
    props.update(extra)
    return g.to_object(name, col, local_at=at, props=props)


def switch(col, name, X, S, Z, group, label, facing="n"):
    """Light switch plate (brass), toggles every light in `group`."""
    g = Geo()
    if facing in ("n", "s"):
        g.box("bronze_ss", -0.2, 0.2, -0.04, 0.04, -0.3, 0.3)
    else:
        g.box("bronze_ss", -0.04, 0.04, -0.2, 0.2, -0.3, 0.3)
    return g.to_object(name, col, local_at=(X, S, Z),
                       props={"interact": "switch", "group": group, "label": label})


def light(col, name, X, S, Z, group, intensity=12.0, color="#ffd29a", range_m=9.0, on=1, shadow=0):
    return empty(name, col, X, S, Z, props={"light": "point", "light_group": group, "intensity": intensity,
                                             "color": color, "range": range_m, "on": on, "shadow": shadow})


def pendant(col, g_static, name, X, S, z_ceiling, drop, group, shade=1.3, kind="lantern", intensity=10.0,
            range_m=10.0):
    """Hanging lamp: cord in the static Geo, lamp body as its own object so it can glow."""
    z = z_ceiling - drop
    g_static.cylinder("black_iron", X, S, 0.03, z + shade * 0.5, z_ceiling, seg=6, caps=False)
    g = Geo()
    if kind == "lantern":
        g.cylinder("black_iron", 0, 0, shade * 0.55, shade * 0.5, shade * 0.6, seg=8)
        g.cylinder("lamp_shade", 0, 0, shade * 0.45, -shade * 0.5, shade * 0.5, seg=8)
        g.cylinder("black_iron", 0, 0, shade * 0.5, -shade * 0.6, -shade * 0.5, seg=8)
    elif kind == "bowl":
        g.cylinder("lamp_shade", 0, 0, shade * 0.2, -shade * 0.3, 0.0, seg=12, r_top=shade * 0.8)
    else:  # sconce/globe
        g.sphere("lamp_shade", 0, 0, 0, shade * 0.4, seg=10, rings=6)
    obj = g.to_object(name, col, local_at=(X, S, z), props={"lamp_group": group})
    light(col, name + "_light", X, S, z - 0.4, group, intensity=intensity, range_m=range_m)
    return obj
