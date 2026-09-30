"""Draw the Compass Hill house plans at 1 character = 1 ft (east-west).

Every level uses the same 120-ft grid, so anything that must stack
(the stair-and-elevator core, the service stair) lines up column for column.
Run:  python3 tools/floorplans.py
"""

WIDTH = 120

# (x0, x1, [label lines]) for the north band (20 ft) and south band (28 ft).
# A room listed with band "full" spans both bands (no dividing line).
LEVELS = {
    "WALKOUT LEVEL": {
        "north": [
            (0, 24, ["THEATER", "24x20"]),
            (24, 34, ["WINE", "10x20"]),
            (34, 48, ["PARTS LIB", "14x20"]),
            (48, 56, ["ELEV", "LU/LA"]),
            (56, 64, ["LOBBY", "N->bay"]),
            (64, 72, ["STAIR", "main"]),
            (72, 84, ["SAFE RM", "12x20"]),
            (84, 94, ["ELEC/IT", "10x20"]),
            (94, 120, ["MECHANICAL", "26x20 heat tank"]),
        ],
        "south": [
            (0, 24, ["GUEST SUITE", "24x28"]),
            (24, 48, ["SUITE 5/FLEX", "24x28"]),
            (48, 72, ["GALLERY", "24x28 (axis)"]),
            (72, 102, ["REC ROOM + BAR", "30x28"]),
            (102, 120, ["GYM+BATH", "18x28"]),
        ],
        "full": [],
    },
    "MAIN LEVEL": {
        "north": [
            (26, 38, ["MUDROOM", "12x20"]),
            (38, 48, ["PWDR x2", "10x20"]),
            (48, 56, ["ELEV", "LU/LA"]),
            (56, 64, ["FOYER", "entry"]),
            (64, 72, ["STAIR", "main"]),
            (72, 88, ["BUTLER PANTRY", "16x20"]),
            (88, 96, ["SVC", "STAIR"]),
            (96, 120, ["SCULLERY/PANTRY", "24x20"]),
        ],
        "south": [
            (26, 44, ["LIBRARY/", "OFFICE", "18x28 S"]),
            (44, 76, ["GREAT ROOM", "32x28 (axis)"]),
            (76, 94, ["DINING", "18x28"]),
            (94, 120, ["KITCHEN/BKFST", "26x28"]),
        ],
        "full": [
            (0, 26, ["PRIMARY SUITE", "(west wing)", "26x48", "", "", ""]),
        ],
    },
    "SECOND FLOOR": {
        "north": [
            (0, 24, ["S1 BATH/CLOSET", "24x20"]),
            (24, 48, ["S2 BATH/CLOSET", "24x20"]),
            (48, 56, ["ELEV", "LU/LA"]),
            (56, 64, ["LANDING", "cupola"]),
            (64, 72, ["STAIR", "main"]),
            (72, 88, ["S3 BATH/CL", "16x20"]),
            (88, 96, ["SVC", "STAIR"]),
            (96, 106, ["LAUNDRY", "10x20"]),
            (106, 120, ["S4 BATH/CL", "14x20"]),
        ],
        "south": [
            (0, 24, ["SUITE 1", "24x28"]),
            (24, 48, ["SUITE 2", "24x28"]),
            (48, 72, ["LOUNGE/LOFT", "24x28 (axis)"]),
            (72, 96, ["SUITE 3", "24x28"]),
            (96, 120, ["SUITE 4", "24x28"]),
        ],
        "full": [],
    },
}

NORTH_ROWS = 2
SOUTH_ROWS = 3


def boundaries(rooms):
    xs = set()
    for x0, x1, _ in rooms:
        xs.add(x0)
        xs.add(x1)
    return xs


def rule(xs, fill, spans_open=()):
    """Horizontal rule with '+' at room boundaries; spans_open stay blank."""
    row = [fill] * (WIDTH + 1)
    for x in xs:
        row[x] = "+"
    for x0, x1 in spans_open:
        for x in range(x0 + 1, x1):
            row[x] = " "
    return "".join(row)


def body_rows(rooms, nrows, row_offset=0):
    rows = [[" "] * (WIDTH + 1) for _ in range(nrows)]
    for x0, x1, labels in rooms:
        for r in range(nrows):
            rows[r][x0] = "|"
            rows[r][x1] = "|"
            idx = r + row_offset
            if idx < len(labels):
                text = labels[idx]
                inner = x1 - x0 - 1
                if len(text) > inner:
                    raise ValueError(f"label {text!r} too wide for {x0}-{x1}")
                start = x0 + 1 + (inner - len(text)) // 2
                for i, ch in enumerate(text):
                    rows[r][start + i] = ch
    return ["".join(r) for r in rows]


def draw(name, spec):
    full = spec["full"]
    north = spec["north"] + full
    south = spec["south"] + full
    top = boundaries(north)
    mid = boundaries(spec["north"]) | boundaries(spec["south"])
    for x0, x1, _ in full:
        mid |= {x0, x1}
    bottom = boundaries(south)
    lines = []
    lines.append(rule(top, "-"))
    n_rows = body_rows(spec["north"], NORTH_ROWS)
    f_rows = body_rows(full, NORTH_ROWS)
    lines += [merge(a, b) for a, b in zip(n_rows, f_rows)]
    lines.append(rule(mid, "-", [(x0, x1) for x0, x1, _ in full]))
    s_rows = body_rows(spec["south"], SOUTH_ROWS)
    f_rows = body_rows(full, SOUTH_ROWS, row_offset=NORTH_ROWS)
    lines += [merge(a, b) for a, b in zip(s_rows, f_rows)]
    lines.append(rule(bottom, "="))
    return lines


def merge(a, b):
    return "".join(y if y != " " else x for x, y in zip(a, b))


def ruler():
    marks = [" "] * (WIDTH + 1)
    for x in range(0, WIDTH + 1, 24):
        s = str(x)
        pos = x if x < WIDTH else x - len(s) + 1
        for i, ch in enumerate(s):
            marks[pos + i] = ch
    return "".join(marks)


def check_widths():
    for name, spec in LEVELS.items():
        for band in ("north", "south"):
            rooms = sorted(spec[band] + spec["full"])
            x = 0
            for x0, x1, _ in rooms:
                assert x0 == x, f"{name} {band}: gap/overlap at {x} vs {x0}"
                x = x1
            assert x == WIDTH, f"{name} {band}: ends at {x}"


if __name__ == "__main__":
    check_widths()
    for name, spec in LEVELS.items():
        print(name)
        print(ruler())
        for line in draw(name, spec):
            print(line)
        print()
