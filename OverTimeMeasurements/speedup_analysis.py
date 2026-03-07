"""
Speedup Analysis — Over-Time Measurements
==========================================
Proxy for execution time: number of data rows in each CSV.
A slower execution generates more samples, hence more rows.

Three speedup dimensions are evaluated:
  (a) Input pair      : rows_41   / rows_312   (input 41 vs 312)
  (b) Language        : rows_lang / rows_C     (relative to C as baseline)
  (c) Power capping   : rows_powercap / rows_no_powercap

Convention: Speedup > 1 means the denominator condition is faster.
"""

import csv
from pathlib import Path

BASE_DIR        = Path(__file__).parent
NO_POWERCAP_DIR = BASE_DIR / "No powercap"
WITH_POWERCAP_DIR = BASE_DIR / "With powercap"

LANG_NAMES = {"c": "C", "hs": "Haskell", "js": "JavaScript", "py": "Python"}
LANG_ORDER = ["c", "hs", "js", "py"]
INPUT_ORDER = ["41", "312"]

# ── helpers ────────────────────────────────────────────────────────────────

def count_data_rows(filepath: Path) -> int:
    with open(filepath, newline="") as f:
        return max(0, sum(1 for _ in csv.reader(f)) - 1)  # minus header


def parse_filename(name: str):
    parts = Path(name).stem.split("_")   # ack_c_np_41 → ['ack','c','np','41']
    return (parts[1], parts[3]) if len(parts) >= 4 else None


def collect_rows(directory: Path) -> dict:
    """Returns {(lang, input_size): row_count}"""
    result = {}
    for fp in sorted(directory.glob("*.csv")):
        parsed = parse_filename(fp.name)
        if parsed:
            result[parsed] = count_data_rows(fp)
    return result


def avg(values):
    v = [x for x in values if x == x]   # drop NaN
    return sum(v) / len(v) if v else float("nan")


def section(title: str, width: int = 75):
    print(f"\n{'═' * width}")
    print(f"  {title}")
    print(f"{'═' * width}")


def table_row(cells, widths, alignments):
    parts = []
    for cell, w, a in zip(cells, widths, alignments):
        parts.append(f"{cell:{a}{w}}")
    print("  " + "  ".join(parts))


def sep_row(widths):
    print("  " + "  ".join("-" * w for w in widths))


# ── (a) Speedup by Input Pair ───────────────────────────────────────────────

def speedup_by_input(np_rows, p7_rows):
    section("(a)  Speedup by Input Pair  —  rows(41) / rows(312)")
    print("     (input A(4,1) requires more computation than A(3,12))\n")
    widths = [14, 12, 10, 10, 12]
    aligns = ["<", ">", ">", ">", ">"]
    table_row(["Language", "Condition", "Rows 41", "Rows 312", "Speedup"],
              widths, aligns)
    sep_row(widths)

    speedups_np, speedups_p7 = [], []
    for lang in LANG_ORDER:
        rows_np_41  = np_rows.get((lang, "41"),  float("nan"))
        rows_np_312 = np_rows.get((lang, "312"), float("nan"))
        rows_p7_41  = p7_rows.get((lang, "41"),  float("nan"))
        rows_p7_312 = p7_rows.get((lang, "312"), float("nan"))

        sp_np = rows_np_41 / rows_np_312 if rows_np_312 else float("nan")
        sp_p7 = rows_p7_41 / rows_p7_312 if rows_p7_312 else float("nan")
        speedups_np.append(sp_np)
        speedups_p7.append(sp_p7)

        name = LANG_NAMES.get(lang, lang)
        table_row([name,  "No cap",   rows_np_41, rows_np_312, f"{sp_np:.4f}x"], widths, aligns)
        table_row(["",    "Powercap", rows_p7_41, rows_p7_312, f"{sp_p7:.4f}x"], widths, aligns)
        sep_row(widths)

    table_row(["Average", "No cap",   "", "", f"{avg(speedups_np):.4f}x"], widths, aligns)
    table_row(["Average", "Powercap", "", "", f"{avg(speedups_p7):.4f}x"], widths, aligns)


# ── (b) Speedup by Language ─────────────────────────────────────────────────

def speedup_by_language(np_rows, p7_rows):
    section("(b)  Speedup by Language  —  rows(lang) / rows(C)  [C = baseline]")
    print("     (values > 1 mean lang is that many times slower than C)\n")
    widths = [14, 12, 10, 10, 12]
    aligns = ["<", ">", ">", ">", ">"]
    table_row(["Language", "Condition", "Input", "Rows", "Speedup vs C"],
              widths, aligns)
    sep_row(widths)

    for cond_label, rows_dict in [("No cap", np_rows), ("Powercap", p7_rows)]:
        for inp in INPUT_ORDER:
            base = rows_dict.get(("c", inp), None)
            speedups = []
            rows_for_group = []
            for lang in LANG_ORDER:
                r = rows_dict.get((lang, inp), float("nan"))
                sp = r / base if (base and r == r) else float("nan")
                speedups.append(sp)
                rows_for_group.append((lang, r, sp))

            first = True
            for lang, r, sp in rows_for_group:
                name = LANG_NAMES.get(lang, lang)
                table_row([
                    name if first or lang != "c" else name,
                    cond_label if first else "",
                    inp if first else "",
                    r,
                    f"{sp:.4f}x"
                ], widths, aligns)
                first = False
            sep_row(widths)


# ── (c) Speedup by Power Capping ────────────────────────────────────────────

def speedup_by_powercap(np_rows, p7_rows):
    section("(c)  Speedup by Power Capping  —  rows(powercap) / rows(no cap)")
    print("     (values > 1 mean powercap made execution that many times slower)\n")
    widths = [14, 10, 12, 14, 12]
    aligns = ["<", ">", ">", ">", ">"]
    table_row(["Language", "Input", "Rows no cap", "Rows powercap", "Slowdown"],
              widths, aligns)
    sep_row(widths)

    all_speedups = []
    for inp in INPUT_ORDER:
        inp_speedups = []
        for lang in LANG_ORDER:
            r_np = np_rows.get((lang, inp), float("nan"))
            r_p7 = p7_rows.get((lang, inp), float("nan"))
            sp = r_p7 / r_np if (r_np and r_np == r_np) else float("nan")
            inp_speedups.append(sp)
            all_speedups.append(sp)
            name = LANG_NAMES.get(lang, lang)
            table_row([name, inp, r_np, r_p7, f"{sp:.4f}x"], widths, aligns)
        sep_row(widths)
        table_row(["Avg input " + inp, "", "", "", f"{avg(inp_speedups):.4f}x"],
                  widths, aligns)
        sep_row(widths)

    table_row(["Overall average", "", "", "", f"{avg(all_speedups):.4f}x"],
              widths, aligns)


# ── main ───────────────────────────────────────────────────────────────────

def main():
    np_rows = collect_rows(NO_POWERCAP_DIR)
    p7_rows = collect_rows(WITH_POWERCAP_DIR)

    print("\nSpeedup Analysis — Over-Time Measurements")
    print("Proxy: CSV row count  (each row = one sample ≈ 50 ms interval)")
    print("Reference: ackermann A(4,1) → input '41'  |  A(3,12) → input '312'")

    speedup_by_input(np_rows, p7_rows)
    speedup_by_language(np_rows, p7_rows)
    speedup_by_powercap(np_rows, p7_rows)
    print()


if __name__ == "__main__":
    main()
