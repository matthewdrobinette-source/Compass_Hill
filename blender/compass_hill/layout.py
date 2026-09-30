"""Key dimensions from the master plan (feet, site coordinates; see common.py)."""

import math

from .common import smoothstep
from .textures import periodic_noise

PARCEL_X = (-450.0, 450.0)
PARCEL_S = (-40.0, 1300.0)

# Levels (Z, feet)
Z_WALKOUT = -11.0
Z_MAIN = 0.0
Z_SECOND = 11.0
Z_EAVE = 21.0
Z_RIDGE = Z_EAVE + 24 * 7 / 12  # 7:12 gable over 48 ft
Z_TUNNEL = Z_WALKOUT
TUNNEL_CLEAR = 9.0

# House (plan x 0..120 from west wall -> X = x - 60)
HOUSE_X = (-60.0, 60.0)
HOUSE_S = (736.0, 784.0)
NORTH_BAND = (736.0, 751.0)   # rooms (15 ft) + 5-ft hall
HALL = (751.0, 756.0)
SOUTH_BAND = (756.0, 784.0)

# Entrance complex
ROAD_S = (-24.0, 0.0)
LAYBY_S = (45.0, 73.0)
LAYBY_X = (-157.0, 157.0)
STEM = (-12.0, 12.0, 73.0, 130.0)
TEARDROP_C = (0.0, 178.0)
TEARDROP_R = 48.0
GATE_S = 222.0
GATE_BUILDING_S = (202.0, 262.0)

# Court
COURT_C = (0.0, 591.0)
COURT_R_OUT = 75.0
COURT_R_IN = 51.0
CISTERN_R = 20.0
LOOP_R = (21.0, 31.0)
PAVILION_POST_R = 17.0
PAVILION_ROOF_R = 25.0

# Garage
GARAGE = (-190.0, -142.0, 612.0, 642.0)

# Berm Ring
YARD = (-70.0, 70.0, 790.0, 864.0)
BASIN = (-70.0, 70.0, 864.0, 889.0)

_noise = None


def _n(X, S):
    global _noise
    if _noise is None:
        _noise = periodic_noise(n=256, scale=4, octaves=3, seed=5)
    i = int((X + 1000) / 12) % 256
    j = int((S + 1000) / 12) % 256
    return _noise[j, i] - 0.5


def natural(X, S):
    """Grade before the Berm Ring is shaped."""
    if S < 90:
        z = -8.0
    elif S < 250:
        z = -8.0 + 8.0 * smoothstep(90, 250, S)
    elif S < 736:
        z = 0.0
    elif S < 790:
        z = -12.0 * smoothstep(736, 790, S)
    else:
        z = -12.0 - 0.085 * (S - 790)
    # gentle roll away from the built areas
    far = smoothstep(200, 330, abs(X))
    if S > 800:
        far = max(far, smoothstep(800, 980, S) * smoothstep(90, 160, abs(X)))
    z += far * 3.0 * _n(X, S)
    # the side lands fall away a little toward the property lines
    z -= 4.0 * smoothstep(300, 450, abs(X)) * smoothstep(300, 700, S)
    return z


def berm_profile(X, S):
    """Height of the Berm Ring and basin relative to the yard (None if outside)."""
    x0, x1, s0, _ = YARD
    s1 = BASIN[3]
    # signed distance outside the yard+basin rounded rectangle
    cx = (x0 + x1) / 2
    hx = (x1 - x0) / 2
    if S < s0:
        return None
    dx = abs(X - cx) - hx
    ds = S - s1
    r = 30.0
    qx, qs = dx + r, ds + r
    d = math.hypot(max(qx, 0), max(qs, 0)) + min(max(qx, qs), 0) - r
    return d


def terrain(X, S):
    """Finished grade. The hilltop sits 0.2 ft below the main floor so that
    pavement laid on it comes out flush with the floor."""
    return _terrain(X, S) - 0.2


PAVE = 0.2  # pavement thickness above grade


def pave_z(X, S):
    return terrain(X, S) + PAVE


POOL = (0.0, 1020.0, 36.0, 22.0)  # seasonal pool: center, radii


def pool_level():
    return natural(0.0, POOL[1] + POOL[3]) + 0.6


def _terrain(X, S):
    z = natural(X, S)
    # seasonal pool: a shallow dish cut into the slope, with a low downhill rim
    px, ps, rx, rs = POOL
    d2 = ((X - px) / rx) ** 2 + ((S - ps) / rs) ** 2
    if d2 < 1.0:
        z = min(z, pool_level() - 1.8 * (1 - d2) ** 0.7)
    elif d2 < 1.8 and S > ps:
        z = max(z, pool_level() + 0.3 - 1.2 * (d2 - 1.0))
    d = berm_profile(X, S)
    if d is None:
        return z
    yard_z = -12.0 - 0.5 * smoothstep(790, 864, S)
    if d <= 0:
        # inside: yard, then basin (3 ft deep, dished)
        if S > BASIN[2]:
            depth = 3.2 * math.sin(math.pi * min(1, (S - BASIN[2]) / (BASIN[3] - BASIN[2]))) ** 0.6
            edge = smoothstep(0, 10, -d)
            return yard_z - 0.3 - depth * edge
        return yard_z
    # the berm: 3:1 inside, 10-ft crest, 2:1 outside, never below natural
    crest = yard_z + 7.0
    if d < 21:
        h = yard_z + 7.0 * d / 21
    elif d < 31:
        h = crest
    else:
        h = crest - (d - 31) / 2.0
    # arch notch on the axis through the south berm (the arch fills it)
    if abs(X) < 9 and S > BASIN[3]:
        h = min(h, yard_z - 1.0 + 0.3 * max(0, abs(X) - 4))
    # berm dies into the brow near the house corners
    if S < 800:
        h = min(h, z + 7.0 * smoothstep(790, 812, S))
    return max(z, h)
