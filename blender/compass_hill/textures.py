"""Procedural, seamless textures for Compass Hill (numpy + Pillow).

Palette notes (southwest Ohio): Ordovician fossil limestone weathers blue-gray
to buff; site white oak silvers to gray-brown; Vermont unfading green slate;
dark-bronze window cladding; crushed local limestone for paths and aggregate.
"""

from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

N = 1024
RNG = np.random.default_rng(1827)  # Warren County founded 1803; Lebanon platted 1802


def periodic_noise(n=N, scale=8, octaves=5, persistence=0.5, seed=0):
    """Tileable fractal value noise in [0, 1]."""
    rng = np.random.default_rng(seed)
    out = np.zeros((n, n))
    amp, total = 1.0, 0.0
    for o in range(octaves):
        cells = scale * 2 ** o
        grid = rng.random((cells, cells))
        # bilinear upsample with wrap-around
        coords = np.arange(n) * cells / n
        i0 = np.floor(coords).astype(int)
        f = coords - i0
        f = f * f * (3 - 2 * f)
        i1 = (i0 + 1) % cells
        a = grid[i0][:, i0]
        b = grid[i0][:, i1]
        c = grid[i1][:, i0]
        d = grid[i1][:, i1]
        fx = f[None, :]
        fy = f[:, None]
        out += amp * ((a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy)
        total += amp
        amp *= persistence
    return out / total


def to_img(arr):
    return Image.fromarray(np.clip(arr * 255, 0, 255).astype(np.uint8))


def colorize(v, c0, c1):
    c0 = np.array(c0) / 255.0
    c1 = np.array(c1) / 255.0
    return c0[None, None, :] * (1 - v[..., None]) + c1[None, None, :] * v[..., None]


def limestone_ashlar():
    """Coursed split-face limestone, random stone lengths, fossil flecks."""
    img = np.zeros((N, N, 3))
    base = periodic_noise(scale=6, seed=11)
    fine = periodic_noise(scale=64, octaves=3, seed=12)
    courses = [96, 128, 80, 112, 96, 128, 80, 112, 96, 96]  # px heights, sum 1024
    y = 0
    mortar = np.zeros((N, N), bool)
    tone = np.zeros((N, N))
    for ci, h in enumerate(courses):
        x = int(RNG.integers(0, 200))
        while True:
            w = int(RNG.integers(160, 420))
            t = RNG.normal(0, 0.08)
            xs = (np.arange(x, x + w) % N)
            tone[y:y + h][:, xs] = t
            mortar[y:y + h, xs[0]] = True
            mortar[y:y + h, (xs[0] + 1) % N] = True
            x += w
            if x >= N + 200:
                break
        mortar[y:y + 3, :] = True
        y += h
    v = 0.55 + 0.25 * (base - 0.5) + 0.18 * (fine - 0.5) + tone
    stone = colorize(np.clip(v, 0, 1), (132, 128, 116), (214, 204, 182))
    # fossil flecks (brachiopod/bryozoan hash)
    fleck = periodic_noise(scale=128, octaves=1, seed=13) > 0.82
    stone[fleck] = stone[fleck] * 0.82
    img = stone
    m = Image.fromarray(mortar.astype(np.uint8) * 255).filter(ImageFilter.MaxFilter(5))
    mm = np.array(m) > 0
    img[mm] = np.array([168, 160, 146]) / 255.0 * (0.9 + 0.1 * fine[mm])[..., None]
    shade = to_img(np.array(Image.fromarray((mm * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(4))) / 255.0)
    img = img * (1 - 0.25 * (np.array(shade) / 255.0)[..., None])
    return to_img(img)


def slate():
    """Vermont unfading green slate, 12-in exposure courses, staggered."""
    img = np.zeros((N, N, 3))
    fine = periodic_noise(scale=48, octaves=3, seed=21)
    rows = 8
    rh = N // rows
    for r in range(rows):
        off = (r % 2) * 64
        widths = []
        x = off
        while x < N + off:
            w = int(RNG.integers(96, 160))
            t = RNG.normal(0, 0.07)
            xs = np.arange(x, x + w) % N
            v = 0.5 + t + 0.15 * (fine[r * rh:(r + 1) * rh][:, xs] - 0.5)
            img[r * rh:(r + 1) * rh][:, xs] = colorize(np.clip(v, 0, 1), (58, 72, 64), (112, 128, 116))
            img[r * rh:(r + 1) * rh, xs[0]] *= 0.45
            x += w
        grad = np.linspace(1.0, 0.72, rh)[:, None, None]
        img[r * rh:(r + 1) * rh] *= grad
    return to_img(img)


def oak_siding():
    """Weathered white-oak lap boards, 8-in exposure (8 per 1024 px)."""
    boards = 8
    bh = N // boards
    grain = periodic_noise(scale=4, octaves=4, seed=31)
    streak = np.tile(periodic_noise(n=N, scale=96, octaves=2, seed=32).mean(axis=0, keepdims=True), (N, 1))
    img = np.zeros((N, N, 3))
    for b in range(boards):
        t = RNG.normal(0, 0.06)
        v = 0.5 + t + 0.25 * (streak[b * bh:(b + 1) * bh] - 0.5) + 0.1 * (grain[b * bh:(b + 1) * bh] - 0.5)
        img[b * bh:(b + 1) * bh] = colorize(np.clip(v, 0, 1), (104, 92, 78), (176, 164, 146))
        img[b * bh:(b + 1) * bh] *= np.linspace(0.8, 1.0, bh)[:, None, None]
        img[b * bh:b * bh + 4] *= 0.5
        # butt joints
        for j in RNG.integers(0, N, 2):
            img[b * bh:(b + 1) * bh, j:j + 3] *= 0.6
    return to_img(img)


def standing_seam():
    img = np.zeros((N, N, 3)) + np.array([62, 64, 66]) / 255.0
    n = periodic_noise(scale=16, octaves=2, seed=41)
    img *= (0.92 + 0.12 * n)[..., None]
    for x in range(0, N, 128):  # 16-in panels at 1024px = 128 in
        img[:, x:x + 10] *= 1.35
        img[:, x + 10:x + 14] *= 0.6
    return to_img(img)


def pv_panel():
    img = np.zeros((N, N, 3)) + np.array([22, 30, 52]) / 255.0
    cell = N // 8
    for i in range(8):
        img[i * cell:i * cell + 3, :] = 0.75
        img[:, i * cell:i * cell + 3] = 0.75
        for k in range(1, 4):
            img[:, i * cell + k * cell // 4] = np.array([60, 66, 84]) / 255.0
    img[:6, :] = img[:, :6] = 0.55
    return to_img(img)


def grass():
    a = periodic_noise(scale=8, seed=51)
    b = periodic_noise(scale=96, octaves=3, seed=52)
    v = 0.55 * a + 0.45 * b
    img = colorize(v, (58, 82, 34), (122, 146, 68))
    blades = periodic_noise(scale=256, octaves=1, seed=53) > 0.7
    img[blades] *= 1.12
    return to_img(img)


def gravel(raked=False):
    a = periodic_noise(scale=160, octaves=2, seed=61)
    b = periodic_noise(scale=10, seed=62)
    v = 0.6 * a + 0.4 * b
    img = colorize(v, (150, 146, 136), (222, 218, 206))
    if raked:
        y = np.arange(N)
        rake = 0.5 + 0.5 * np.sin(y / N * 2 * np.pi * 32)
        img *= (0.85 + 0.15 * rake)[:, None, None]
    return to_img(img)


def aggregate_concrete():
    a = periodic_noise(scale=200, octaves=2, seed=71)
    b = periodic_noise(scale=6, seed=72)
    img = colorize(0.5 * a + 0.5 * b, (150, 144, 132), (206, 198, 184))
    stones = periodic_noise(scale=180, octaves=1, seed=73)
    img[stones > 0.78] *= 0.78
    img[stones < 0.2] *= 1.08
    for x in (0, 511):  # control joints every 10 ft at 1024 px = 20 ft
        img[:, x:x + 3] *= 0.7
        img[x:x + 3, :] *= 0.7
    return to_img(img)


def asphalt():
    a = periodic_noise(scale=220, octaves=2, seed=81)
    b = periodic_noise(scale=5, seed=82)
    return to_img(colorize(0.6 * a + 0.4 * b, (44, 44, 46), (92, 92, 94)))


def plaster():
    a = periodic_noise(scale=6, seed=91)
    b = periodic_noise(scale=120, octaves=2, seed=92)
    return to_img(colorize(0.6 * a + 0.4 * b, (224, 214, 196), (244, 238, 226)))


def oak_floor():
    planks = 16  # 4-in strips across 64 in
    ph = N // planks
    grain = periodic_noise(scale=3, octaves=4, seed=101)
    img = np.zeros((N, N, 3))
    for p in range(planks):
        off = int(RNG.integers(0, N))
        g = np.roll(grain[p * ph:(p + 1) * ph], off, axis=1)
        t = RNG.normal(0, 0.07)
        img[p * ph:(p + 1) * ph] = colorize(np.clip(0.5 + t + 0.35 * (g - 0.5), 0, 1), (138, 100, 62), (200, 160, 112))
        img[p * ph:p * ph + 2] *= 0.55
        j = int(RNG.integers(0, N))
        img[p * ph:(p + 1) * ph, j:j + 2] *= 0.55
    return to_img(img)


def polished_concrete():
    a = periodic_noise(scale=5, seed=111)
    b = periodic_noise(scale=150, octaves=2, seed=112)
    img = colorize(0.7 * a + 0.3 * b, (150, 148, 142), (190, 186, 178))
    return to_img(img)


def cobble():
    img = np.zeros((N, N, 3))
    s = 64
    tone = periodic_noise(scale=64, octaves=2, seed=121)
    for r in range(N // s):
        off = (r % 2) * s // 2
        for c in range(N // s + 1):
            t = RNG.normal(0, 0.08)
            x0 = (c * s + off) % N
            xs = np.arange(x0, x0 + s) % N
            v = 0.5 + t + 0.2 * (tone[r * s:(r + 1) * s][:, xs] - 0.5)
            img[r * s:(r + 1) * s][:, xs] = colorize(np.clip(v, 0, 1), (110, 104, 94), (178, 170, 156))
            img[r * s:(r + 1) * s, x0] *= 0.4
        img[r * s:r * s + 4] *= 0.45
    return to_img(img)


def bark():
    a = periodic_noise(scale=4, octaves=4, seed=131)
    v = np.tile(periodic_noise(scale=48, octaves=2, seed=132).mean(axis=0, keepdims=True), (N, 1))
    return to_img(colorize(0.5 * a + 0.5 * v, (58, 50, 42), (128, 118, 102)))


def foliage():
    a = periodic_noise(scale=24, octaves=4, seed=141)
    b = periodic_noise(scale=160, octaves=1, seed=142)
    img = colorize(0.6 * a + 0.4 * b, (34, 58, 24), (98, 128, 52))
    return to_img(img)


def brick():
    img = np.zeros((N, N, 3))
    bh, bw = 64, 192
    for r in range(N // bh):
        off = (r % 2) * bw // 2
        for c in range(N // bw + 1):
            t = RNG.normal(0, 0.07)
            x0 = (c * bw + off) % N
            xs = np.arange(x0, x0 + bw) % N
            img[r * bh:(r + 1) * bh][:, xs] = np.clip(np.array([150, 78, 58]) / 255.0 * (1 + t), 0, 1)
            img[r * bh:(r + 1) * bh, x0:x0 + 6] = 0.72
        img[r * bh:r * bh + 6] = 0.72
    return to_img(img)


def meadow():
    """Early-October southwest Ohio meadow: little bluestem, goldenrod, asters."""
    a = periodic_noise(scale=10, seed=151)
    b = periodic_noise(scale=140, octaves=2, seed=152)
    img = colorize(0.5 * a + 0.5 * b, (120, 104, 58), (196, 170, 96))
    gold = periodic_noise(scale=90, octaves=1, seed=153) > 0.74
    img[gold] = img[gold] * 0.5 + np.array([214, 176, 42]) / 255.0 * 0.5
    aster = periodic_noise(scale=110, octaves=1, seed=154) > 0.8
    img[aster] = img[aster] * 0.6 + np.array([150, 130, 190]) / 255.0 * 0.4
    green = periodic_noise(scale=30, octaves=2, seed=155)
    img *= (0.9 + 0.2 * green)[..., None]
    return to_img(img)


def leaf_litter():
    a = periodic_noise(scale=90, octaves=3, seed=161)
    b = periodic_noise(scale=8, seed=162)
    img = colorize(0.6 * a + 0.4 * b, (70, 54, 36), (146, 110, 64))
    moss = periodic_noise(scale=12, octaves=2, seed=163) > 0.66
    img[moss] = img[moss] * 0.6 + np.array([74, 92, 44]) / 255.0 * 0.4
    return to_img(img)


def autumn_foliage():
    a = periodic_noise(scale=24, octaves=4, seed=171)
    b = periodic_noise(scale=160, octaves=1, seed=172)
    img = colorize(0.6 * a + 0.4 * b, (112, 52, 18), (184, 116, 34))
    return to_img(img)


def dark_foliage():
    a = periodic_noise(scale=30, octaves=4, seed=181)
    return to_img(colorize(a, (22, 40, 30), (70, 96, 64)))


TEXTURES = {
    "meadow": meadow,
    "leaf_litter": leaf_litter,
    "autumn_foliage": autumn_foliage,
    "dark_foliage": dark_foliage,
    "limestone": limestone_ashlar,
    "slate": slate,
    "oak_siding": oak_siding,
    "standing_seam": standing_seam,
    "pv": pv_panel,
    "grass": grass,
    "gravel": lambda: gravel(False),
    "raked_gravel": lambda: gravel(True),
    "aggregate": aggregate_concrete,
    "asphalt": asphalt,
    "plaster": plaster,
    "oak_floor": oak_floor,
    "polished_concrete": polished_concrete,
    "cobble": cobble,
    "bark": bark,
    "foliage": foliage,
    "brick": brick,
}


def build_all(out_dir: Path, size=512):
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = {}
    for name, fn in TEXTURES.items():
        p = out_dir / f"{name}.jpg"
        if not p.exists():
            img = fn().resize((size, size), Image.LANCZOS)
            img.save(p, quality=86)
        paths[name] = p
    return paths


if __name__ == "__main__":
    import sys
    out = Path(__file__).resolve().parent.parent / "textures"
    for name, p in build_all(out).items():
        print(name, p.stat().st_size)
