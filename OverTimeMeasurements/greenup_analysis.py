"""
Greenup Analysis — Over-Time Measurements
==========================================
Formula:
    Greenup = (Tϕ · Pϕ) / (To · Po) = Eϕ / Eo

Where:
    Tϕ  — total execution time of the non-optimized code
    To  — total execution time of the optimized code
    Pϕ  — average power of the non-optimized code
    Po  — average power of the optimized code
    Eϕ  — total energy of the non-optimized code  (= Tϕ · Pϕ)
    Eo  — total energy of the optimized code       (= To · Po)

Greenup > 1  →  optimized code is more energy-efficient.
Greenup < 1  →  optimized code actually consumes more total energy.

Data:
    Each CSV row represents a 50 ms sample window.
    The 'Package' column gives the RAPL package energy (Joules) for that window.
    → Total energy E = Σ Package_i
    → Total time   T = N_rows × 0.05 s
    → Avg power    P = E / T  (Watts)

Three dimensions evaluated:
    (a) Input pair      : ϕ = A(4,1)/input 41,  o = A(3,12)/input 312
    (b) Language        : ϕ = each language,     o = C  (fastest / baseline)
    (c) Power capping   : ϕ = no powercap,       o = 7 W powercap
"""

import csv
from pathlib import Path

BASE_DIR          = Path(__file__).parent
NO_POWERCAP_DIR   = BASE_DIR / "No powercap"
WITH_POWERCAP_DIR = BASE_DIR / "With powercap"

LANG_NAMES = {"c": "C", "hs": "Haskell", "js": "JavaScript", "py": "Python"}
LANG_ORDER  = ["c", "hs", "js", "py"]
INPUT_ORDER = ["41", "312"]
SAMPLE_INTERVAL = 0.05   # seconds per row

# ── data extraction ──────────────────────────────────────────────────────────

def read_metrics(filepath: Path) -> dict:
    """
    Returns {total_energy_J, total_time_s, avg_power_W}
    from a single CSV file.
    """
    total_energy = 0.0
    n_rows = 0
    with open(filepath, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            total_energy += float(row["Package"].strip())
            n_rows += 1
    total_time = n_rows * SAMPLE_INTERVAL
    avg_power  = total_energy / total_time if total_time > 0 else float("nan")
    return {
        "energy": total_energy,
        "time":   total_time,
        "power":  avg_power,
        "rows":   n_rows,
    }


def parse_filename(name: str):
    parts = Path(name).stem.split("_")
    return (parts[1], parts[3]) if len(parts) >= 4 else None


def collect_metrics(directory: Path) -> dict:
    """Returns {(lang, input_size): metrics_dict}"""
    result = {}
    for fp in sorted(directory.glob("*.csv")):
        parsed = parse_filename(fp.name)
        if parsed:
            result[parsed] = read_metrics(fp)
    return result


def avg(values):
    v = [x for x in values if x == x]
    return sum(v) / len(v) if v else float("nan")


# ── formatting helpers ────────────────────────────────────────────────────────

def section(title: str, width: int = 79):
    print(f"\n{'═' * width}")
    print(f"  {title}")
    print(f"{'═' * width}")


def table_row(cells, widths, aligns):
    parts = [f"{c:{a}{w}}" for c, w, a in zip(cells, widths, aligns)]
    print("  " + "  ".join(parts))


def sep_row(widths):
    print("  " + "  ".join("-" * w for w in widths))


def greenup_fmt(g):
    if g != g:
        return "    N/A"
    marker = "▲" if g >= 1.0 else "▼"
    return f"{g:>7.4f}x {marker}"


# ── (a) Greenup by Input Pair ─────────────────────────────────────────────────

def greenup_by_input(np_m, p7_m):
    section("(a)  Greenup by Input Pair  —  Eϕ=E(41) / Eo=E(312)")
    print("     ϕ = A(4,1) [input 41]  |  o = A(3,12) [input 312]")
    print("     Greenup > 1 → A(4,1) consumes more energy than A(3,12)\n")

    widths  = [14, 12, 12, 12, 12]
    aligns  = ["<", ">", ">", ">", ">"]
    table_row(["Language", "Condition", "E(41) J", "E(312) J", "Greenup"],
              widths, aligns)
    sep_row(widths)

    gs_np, gs_p7 = [], []
    for lang in LANG_ORDER:
        m_np_41  = np_m.get((lang, "41"))
        m_np_312 = np_m.get((lang, "312"))
        m_p7_41  = p7_m.get((lang, "41"))
        m_p7_312 = p7_m.get((lang, "312"))

        g_np = m_np_41["energy"] / m_np_312["energy"] if (m_np_41 and m_np_312) else float("nan")
        g_p7 = m_p7_41["energy"] / m_p7_312["energy"] if (m_p7_41 and m_p7_312) else float("nan")
        gs_np.append(g_np); gs_p7.append(g_p7)

        name = LANG_NAMES.get(lang, lang)
        table_row([name, "No cap",
                   f"{m_np_41['energy']:.2f}", f"{m_np_312['energy']:.2f}",
                   greenup_fmt(g_np)], widths, aligns)
        table_row(["",   "Powercap",
                   f"{m_p7_41['energy']:.2f}", f"{m_p7_312['energy']:.2f}",
                   greenup_fmt(g_p7)], widths, aligns)
        sep_row(widths)

    table_row(["Average", "No cap",   "", "", greenup_fmt(avg(gs_np))], widths, aligns)
    table_row(["Average", "Powercap", "", "", greenup_fmt(avg(gs_p7))], widths, aligns)


# ── (b) Greenup by Language ───────────────────────────────────────────────────

def greenup_by_language(np_m, p7_m):
    section("(b)  Greenup by Language  —  Eϕ=E(lang) / Eo=E(C)  [C = baseline]")
    print("     Greenup > 1 → language consumes more energy than C\n")

    widths  = [14, 12, 8, 8, 8, 10]
    aligns  = ["<", ">", ">", ">", ">", ">"]
    table_row(["Language", "Condition", "Input",
               "E(J)", "T(s)", "Greenup vs C"], widths, aligns)
    sep_row(widths)

    for cond_lbl, rows_dict in [("No cap", np_m), ("Powercap", p7_m)]:
        for inp in INPUT_ORDER:
            base = rows_dict.get(("c", inp))
            first = True
            for lang in LANG_ORDER:
                m = rows_dict.get((lang, inp))
                if not m or not base:
                    continue
                g = m["energy"] / base["energy"]
                name = LANG_NAMES.get(lang, lang)
                table_row([name,
                           cond_lbl if first else "",
                           inp       if first else "",
                           f"{m['energy']:.3f}",
                           f"{m['time']:.2f}",
                           greenup_fmt(g)], widths, aligns)
                first = False
            sep_row(widths)


# ── (c) Greenup by Power Capping ──────────────────────────────────────────────

def greenup_by_powercap(np_m, p7_m):
    section("(c)  Greenup by Power Capping  —  Eϕ=E(no cap) / Eo=E(powercap)")
    print("     ϕ = no powercap  |  o = 7 W powercap")
    print("     Greenup > 1 → powercap saves energy  |  < 1 → powercap wastes energy\n")

    widths  = [14, 8, 9, 7, 9, 7, 10]
    aligns  = ["<", ">", ">", ">", ">", ">", ">"]
    table_row(["Language", "Input",
               "E np (J)", "T np (s)",
               "E p7 (J)", "T p7 (s)",
               "Greenup"], widths, aligns)
    sep_row(widths)

    all_g = []
    for inp in INPUT_ORDER:
        inp_g = []
        for lang in LANG_ORDER:
            m_np = np_m.get((lang, inp))
            m_p7 = p7_m.get((lang, inp))
            if not m_np or not m_p7:
                continue
            g = m_np["energy"] / m_p7["energy"]
            inp_g.append(g); all_g.append(g)
            name = LANG_NAMES.get(lang, lang)
            table_row([name, inp,
                       f"{m_np['energy']:.3f}", f"{m_np['time']:.2f}",
                       f"{m_p7['energy']:.3f}", f"{m_p7['time']:.2f}",
                       greenup_fmt(g)], widths, aligns)
        sep_row(widths)
        table_row([f"Avg input {inp}", "", "", "", "", "", greenup_fmt(avg(inp_g))],
                  widths, aligns)
        sep_row(widths)

    table_row(["Overall avg", "", "", "", "", "", greenup_fmt(avg(all_g))],
              widths, aligns)


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    np_m = collect_metrics(NO_POWERCAP_DIR)
    p7_m = collect_metrics(WITH_POWERCAP_DIR)

    print("\nGreenup Analysis — Over-Time Measurements")
    print("Formula : Greenup = (Tϕ · Pϕ) / (To · Po)  =  Eϕ / Eo")
    print("Energy  : Σ Package column (Joules, RAPL)  per 50 ms sample window")
    print("▲ = optimized code is greener  |  ▼ = optimized code uses more energy")

    greenup_by_input(np_m, p7_m)
    greenup_by_language(np_m, p7_m)
    greenup_by_powercap(np_m, p7_m)
    print()


if __name__ == "__main__":
    main()
