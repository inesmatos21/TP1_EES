"""
Powerup Analysis — Over-Time Measurements
==========================================
Formula:
    Powerup = Speedup / Greenup
            = (Tϕ / To) / (Eϕ / Eo)
            = (Tϕ · Eo) / (To · Eϕ)
            = Po / Pϕ

Where:
    Tϕ, To  — total execution time of non-optimized / optimized code
    Eϕ, Eo  — total energy    of non-optimized / optimized code
    Pϕ, Po  — average power   of non-optimized / optimized code

Powerup is therefore the ratio of average power draw (optimized ÷ non-optimized).

    Powerup > 1  →  optimized code draws MORE watts  (faster but power-hungry)
    Powerup = 1  →  same average power draw
    Powerup < 1  →  optimized code draws FEWER watts  (doubly efficient)

Data proxies per 50 ms sample window:
    Time   T = N_rows × 0.05 s      (row count ≈ execution time)
    Energy E = Σ Package_i  (J)     (RAPL package energy)
    Power  P = E / T        (W)

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
    """Returns time (s), energy (J), power (W), and row count from a CSV."""
    total_energy = 0.0
    n_rows = 0
    with open(filepath, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            total_energy += float(row["Package"].strip())
            n_rows += 1
    total_time = n_rows * SAMPLE_INTERVAL
    avg_power  = total_energy / total_time if total_time > 0 else float("nan")
    return {"energy": total_energy, "time": total_time,
            "power": avg_power, "rows": n_rows}


def parse_filename(name: str):
    parts = Path(name).stem.split("_")
    return (parts[1], parts[3]) if len(parts) >= 4 else None


def collect_metrics(directory: Path) -> dict:
    result = {}
    for fp in sorted(directory.glob("*.csv")):
        parsed = parse_filename(fp.name)
        if parsed:
            result[parsed] = read_metrics(fp)
    return result


def avg(values):
    v = [x for x in values if x == x]
    return sum(v) / len(v) if v else float("nan")


def compute_powerup(m_phi: dict, m_o: dict) -> tuple[float, float, float]:
    """Returns (speedup, greenup, powerup) for a given phi/o metric pair."""
    speedup = m_phi["time"]   / m_o["time"]   if m_o["time"]   else float("nan")
    greenup = m_phi["energy"] / m_o["energy"] if m_o["energy"] else float("nan")
    powerup = speedup / greenup if greenup else float("nan")
    return speedup, greenup, powerup


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


def fmt(v, marker=True):
    if v != v:
        return "     N/A"
    if not marker:
        return f"{v:>8.4f}x"
    sym = "▲" if v >= 1.0 else "▼"
    return f"{v:>7.4f}x{sym}"


# ── (a) Powerup by Input Pair ─────────────────────────────────────────────────

def powerup_by_input(np_m, p7_m):
    section("(a)  Powerup by Input Pair  —  ϕ=input 41  /  o=input 312")
    print("     Powerup = Speedup / Greenup = P(312) / P(41)")
    print("     Powerup > 1 → A(3,12) runs at higher average watts than A(4,1)\n")

    w = [14, 12, 10, 10, 10, 10]
    a = ["<", ">", ">", ">", ">", ">"]
    table_row(["Language", "Condition", "Speedup", "Greenup", "Powerup", "P(J/s)"], w, a)
    sep_row(w)

    pu_np, pu_p7 = [], []
    for lang in LANG_ORDER:
        for cond_lbl, m_dict, bucket in [("No cap",   np_m, pu_np),
                                          ("Powercap", p7_m, pu_p7)]:
            m41  = m_dict.get((lang, "41"))
            m312 = m_dict.get((lang, "312"))
            if not m41 or not m312:
                continue
            sp, gu, pu = compute_powerup(m41, m312)
            bucket.append(pu)
            name = LANG_NAMES.get(lang, lang) if cond_lbl == "No cap" else ""
            table_row([name, cond_lbl,
                       fmt(sp, False), fmt(gu, False),
                       fmt(pu),
                       f"{m312['power']:.3f}W"], w, a)
        sep_row(w)

    table_row(["Average", "No cap",   "", "", fmt(avg(pu_np)), ""], w, a)
    table_row(["Average", "Powercap", "", "", fmt(avg(pu_p7)), ""], w, a)


# ── (b) Powerup by Language ───────────────────────────────────────────────────

def powerup_by_language(np_m, p7_m):
    section("(b)  Powerup by Language  —  ϕ=language  /  o=C  [C = baseline]")
    print("     Powerup > 1 → language runs at higher average watts than C")
    print("     Powerup < 1 → language is more power-frugal than C\n")

    w = [14, 9, 7, 9, 9, 10, 7]
    a = ["<", ">", ">", ">", ">", ">", ">"]
    table_row(["Language", "Condition", "Input",
               "Speedup", "Greenup", "Powerup", "Pϕ (W)"], w, a)
    sep_row(w)

    for cond_lbl, m_dict in [("No cap", np_m), ("Powercap", p7_m)]:
        for inp in INPUT_ORDER:
            base = m_dict.get(("c", inp))
            if not base:
                continue
            first = True
            for lang in LANG_ORDER:
                m = m_dict.get((lang, inp))
                if not m:
                    continue
                sp, gu, pu = compute_powerup(m, base)
                name = LANG_NAMES.get(lang, lang)
                table_row([name,
                           cond_lbl if first else "",
                           inp       if first else "",
                           fmt(sp, False), fmt(gu, False),
                           fmt(pu),
                           f"{m['power']:.3f}W"], w, a)
                first = False
            sep_row(w)


# ── (c) Powerup by Power Capping ──────────────────────────────────────────────

def powerup_by_powercap(np_m, p7_m):
    section("(c)  Powerup by Power Capping  —  ϕ=no cap  /  o=7 W powercap")
    print("     Powerup > 1 → powercap runs at higher average watts  (unlikely by design)")
    print("     Powerup < 1 → powercap draws fewer average watts  (expected)\n")

    w = [14, 6, 9, 8, 9, 8, 10]
    a = ["<", ">", ">", ">", ">", ">", ">"]
    table_row(["Language", "Input",
               "Speedup", "Pϕ (W)",
               "Greenup", "Po (W)",
               "Powerup"], w, a)
    sep_row(w)

    all_pu = []
    for inp in INPUT_ORDER:
        inp_pu = []
        for lang in LANG_ORDER:
            m_np = np_m.get((lang, inp))
            m_p7 = p7_m.get((lang, inp))
            if not m_np or not m_p7:
                continue
            sp, gu, pu = compute_powerup(m_np, m_p7)
            inp_pu.append(pu); all_pu.append(pu)
            name = LANG_NAMES.get(lang, lang)
            table_row([name, inp,
                       fmt(sp, False), f"{m_np['power']:.3f}W",
                       fmt(gu, False), f"{m_p7['power']:.3f}W",
                       fmt(pu)], w, a)
        sep_row(w)
        table_row([f"Avg input {inp}", "", "", "", "", "", fmt(avg(inp_pu))], w, a)
        sep_row(w)

    table_row(["Overall avg", "", "", "", "", "", fmt(avg(all_pu))], w, a)


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    np_m = collect_metrics(NO_POWERCAP_DIR)
    p7_m = collect_metrics(WITH_POWERCAP_DIR)

    print("\nPowerup Analysis — Over-Time Measurements")
    print("Formula : Powerup = Speedup / Greenup  =  Po / Pϕ  (average power ratio)")
    print("Time    : N_rows × 0.05 s  |  Energy: Σ Package (J, RAPL)")
    print("▲ = optimized code has higher avg power  |  ▼ = optimized code uses less power")

    powerup_by_input(np_m, p7_m)
    powerup_by_language(np_m, p7_m)
    powerup_by_powercap(np_m, p7_m)
    print()


if __name__ == "__main__":
    main()
