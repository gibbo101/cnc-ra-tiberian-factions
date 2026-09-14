#!/usr/bin/env python3
"""Plan Tiberium/Ore hybrids for every official RA skirmish map the gem rules allow.

For each official map with pure-Ore fields, the planner picks which of them turn to Tiberium and
writes the picks to scripts/official_map_hybrids.json, which official_map_hybrid.py builds from.
The hand-picked HYBRIDS entries in official_map_hybrid.py win over the plan, and a map with no
pure-Ore field stays stock. A summary table goes to docs/official-map-hybrids-list.md.

Fairness is measured per start. Every resource field counts towards every start, weighted by how
near it is (a field REACH cells away counts half), with Gems counted at twice Ore's value. A
start's Tiberium share is the weighted Tiberium it can reach over all the weighted resources it
can reach, and the start gap is how far apart the best- and worst-off start's shares land. A
plan must keep the start gap within MAX_GAP and the map's overall Tiberium share between
MIN_SHARE and MAX_SHARE; among those, the planner picks the one that lands closest to the target
with the smallest start gap, leaning away from each start's nearest field and towards fields
with a mine (a blossom). A map with no such plan stays stock.

The target rotates through the pool (about 50/50, Tiberium-heavy, Ore-heavy) so the pool as a
whole keeps a spread. A map whose turn comes up with a target it cannot get within TARGET_SLACK
of takes whichever target it can hit best.

Usage: official_map_hybrid_plan.py [--game <CnCRemastered dir>]
"""
import argparse
import itertools
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import official_map_hybrid as h  # noqa: E402

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
PLAN_PATH = os.path.join(SCRIPTS, "official_map_hybrids.json")
LIST_PATH = os.path.join(os.path.dirname(SCRIPTS), "docs", "official-map-hybrids-list.md")

MIN_FIELD = 8  # smaller scraps of Ore stay Ore
REACH = 20.0  # cells: a field this far from a start counts half as much as one beside it
GEM_VALUE = 2.0  # Gems pay twice what Ore pays
# The most a plan may leave between the best- and worst-off start. Tiberium pays what Ore pays,
# so the gap is in which resource a start mines, not in its income.
MAX_GAP = 0.35
MIN_SHARE, MAX_SHARE = 0.12, 0.85  # a hybrid keeps some of each resource
GAP_WEIGHT = 0.5  # cost of the start gap, against missing the target
HOME_PENALTY = 0.03  # per converted field that is some start's nearest field
BLOSSOM_BONUS = 0.005  # per converted field fed by a mine
TARGET_SLACK = 0.15  # how far off its rotation target a map may land before it takes another
MAX_EXHAUSTIVE = 18  # candidate fields; a map with more is searched from a greedy start
TARGETS = [("about 50/50", 0.50), ("Tiberium-heavy", 0.70), ("Ore-heavy", 0.25)]


def official_names(game_dir):
    """Every scm??ea / scm???ea map in general.mix."""
    alphabet = "0123456789abcdefghijklmnopqrstuvwxyz"
    with open(os.path.join(game_dir, h.MAIN_MIX), "rb") as f:
        general, _ = h._mix_locate(f, 0, "general.mix")
        entries, _ = h._mix_index(f, general)
    names = []
    for a, b in itertools.product(alphabet, repeat=2):
        for mid in [a + b] + [a + b + c for c in alphabet]:
            name = f"scm{mid}ea.ini"
            if h.ww_crc(name.upper()) in entries:
                names.append(name)
    return sorted(names)


def analyse(src):
    s = h._sections(src)
    overlay = h._overlay(s)
    m = dict(l.split("=", 1) for l in s["map"] if "=" in l)
    basic = dict(l.split("=", 1) for l in s.get("basic", []) if "=" in l)
    mines = h._mines(s)
    mine_fields = [h._field_cells(overlay, mn) for mn in mines]
    seen, fields = set(), []
    for c in range(len(overlay)):
        if overlay[c] in h.ORE and c not in seen:
            cells = h._grow(overlay, [c])
            seen |= cells
            gems = sum(1 for q in cells if overlay[q] not in h.GOLD)
            fields.append({
                "cells": cells, "n": len(cells), "seed": min(cells),
                "c": (sum(q % 128 for q in cells) / len(cells),
                      sum(q // 128 for q in cells) / len(cells)),
                "value": len(cells) - gems + GEM_VALUE * gems,
                "candidate": gems == 0 and len(cells) >= MIN_FIELD,
                "fed": any(mf and mf <= cells for mf in mine_fields),
            })
    return {"overlay": overlay, "fields": fields, "mines": mines,
            "starts": [(p % 128, p // 128) for p in h._starts(s)],
            "name": basic.get("Name", "").strip(), "theatre": m.get("Theater", "").strip().lower()}


class Options:
    """Every way to pick a map's candidate fields, with its Tiberium share and start gap."""

    def __init__(self, a):
        fields, starts = a["fields"], a["starts"]
        self.cand = [i for i, f in enumerate(fields) if f["candidate"]]
        dist = np.array([[math.dist(s, f["c"]) for f in fields] for s in starts])
        weight = np.array([f["value"] for f in fields]) / (1 + (dist / REACH) ** 2)
        self.reach = weight[:, self.cand] / weight.sum(1)[:, None]  # starts x candidates
        self.value = np.array([fields[i]["value"] for i in self.cand]) / sum(
            f["value"] for f in fields)
        nearest = {int(np.argmin(dist[s])) for s in range(len(starts))}
        self.home = np.array([i in nearest for i in self.cand], float)
        self.fed = np.array([fields[i]["fed"] for i in self.cand], float)
        m = len(self.cand)
        self.exhaustive = m <= MAX_EXHAUSTIVE
        if self.exhaustive:
            codes = np.arange(1, 2 ** m, dtype=np.int64)
            self.bits = ((codes[:, None] >> np.arange(m)) & 1).astype(float)
            self.share, self.gap = self.measure(self.bits)

    def measure(self, bits):
        per_start = bits @ self.reach.T
        return bits @ self.value, per_start.max(1) - per_start.min(1)

    def cost(self, bits, share, gap, target):
        fair = (gap <= MAX_GAP) & (share >= MIN_SHARE) & (share <= MAX_SHARE)
        cost = (np.abs(share - target) + GAP_WEIGHT * gap
                + HOME_PENALTY * (bits @ self.home) - BLOSSOM_BONUS * (bits @ self.fed))
        return np.where(fair, cost, np.inf)

    def best(self, target):
        """(indices of the fields to convert, share, gap), or None if no plan is fair."""
        if self.exhaustive:
            bits, share, gap = self.bits, self.share, self.gap
            cost = self.cost(bits, share, gap, target)
        else:
            bits, share, gap, cost = self.search(target)
        if not np.isfinite(cost).any():
            return None
        k = int(np.argmin(cost))
        return ([self.cand[j] for j in range(len(self.cand)) if bits[k, j]],
                float(share[k]), float(gap[k]))

    def search(self, target):
        """Flip one field at a time from the empty pick while the cost falls; unfair picks
        count by how far they overstep, so the walk can pass through them."""
        m = len(self.cand)
        pick, best = np.zeros(m), None
        while True:
            trial = np.repeat(pick[None, :], m, 0)
            idx = np.arange(m)
            trial[idx, idx] = 1 - trial[idx, idx]
            trial = trial[trial.sum(1) > 0]
            share, gap = self.measure(trial)
            over = (np.maximum(gap - MAX_GAP, 0) + np.maximum(MIN_SHARE - share, 0)
                    + np.maximum(share - MAX_SHARE, 0))
            walk = (np.abs(share - target) + GAP_WEIGHT * gap + 10 * over
                    + HOME_PENALTY * (trial @ self.home) - BLOSSOM_BONUS * (trial @ self.fed))
            k = int(np.argmin(walk))
            if best is not None and walk[k] >= best:
                break
            best, pick = walk[k], trial[k]
        bits = pick[None, :]
        share, gap = self.measure(bits)
        return bits, share, gap, self.cost(bits, share, gap, target)


def entry_for(a, chosen):
    overlay = a["overlay"]
    cells = set().union(*(a["fields"][i]["cells"] for i in chosen))
    mines = [mn for mn in a["mines"]
             if (fc := h._field_cells(overlay, mn)) and fc <= cells]
    covered = set().union(set(), *(h._field_cells(overlay, mn) for mn in mines))
    seeds = [a["fields"][i]["seed"] for i in chosen if not a["fields"][i]["cells"] <= covered]
    ore = sum(1 for v in overlay if v in h.GOLD)
    gems = sum(1 for v in overlay if v in h.ORE and v not in h.GOLD)
    return {"mines": mines, "fields": seeds}, (len(cells), ore - len(cells), gems)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--game", default=h.DEFAULT_GAME)
    args = ap.parse_args()

    plan, rows, stock, queue = {}, [], [], []
    for name in official_names(args.game):
        a = analyse(h.read_official_map(args.game, name))
        if name in h.HYBRIDS:
            rows.append((name, a, None, None, None))
        elif not any(f["candidate"] for f in a["fields"]) or len(a["starts"]) < 2:
            stock.append((name, a, "no field of Ore alone"))
        else:
            queue.append((name, a))

    for k, (name, a) in enumerate(queue):
        options = Options(a)
        plans = {label: (target, options.best(target)) for label, target in TARGETS}
        label, target = TARGETS[k % len(TARGETS)]
        result = plans[label][1]
        if result is None or abs(result[1] - target) > TARGET_SLACK:
            hits = [(abs(p[1] - t), lab) for lab, (t, p) in plans.items() if p is not None]
            if hits:
                label = min(hits)[1]
                result = plans[label][1]
        if result is None:
            stock.append((name, a, f"no fair choice (starts over {int(MAX_GAP * 100)} points "
                                   f"apart, or Tiberium outside {int(MIN_SHARE * 100)}-"
                                   f"{int(MAX_SHARE * 100)}%)"))
            continue
        chosen, share, gap = result
        entry, mix = entry_for(a, chosen)
        plan[name] = {**entry, "name": a["name"], "target": label,
                      "mix": list(mix), "start_gap": round(gap, 3)}
        rows.append((name, a, label, mix, gap))

    with open(PLAN_PATH, "w") as f:
        json.dump(plan, f, indent=1, sort_keys=True)
        f.write("\n")

    lines = ["# Official-map hybrids: the full list",
             "",
             "Generated by `scripts/official_map_hybrid_plan.py`; hand-picked maps come from "
             "`HYBRIDS` in `scripts/official_map_hybrid.py`. Mix = Tiberium / Ore / Gems cells at "
             "map start. Start gap = how far apart the best- and worst-off start's Tiberium "
             "share of the resources within reach lands (0 = every start the same). See "
             "`official-map-hybrids.md` for the rules and the builder.",
             "",
             "| File | Map | Theatre | Players | Target | Mix | Tiberium | Start gap |",
             "|---|---|---|---|---|---|---|---|"]
    for name, a, label, mix, gap in sorted(rows):
        if mix is None:
            lines.append(f"| `{name}` | {a['name']} | {a['theatre']} | {len(a['starts'])} "
                         f"| picked by hand | see `official-map-hybrids.md` | | |")
            continue
        share = 100 * mix[0] / max(1, sum(mix))
        lines.append(f"| `{name}` | {a['name']} | {a['theatre']} | {len(a['starts'])} "
                     f"| {label} | {mix[0]} / {mix[1]} / {mix[2]} | {share:.0f}% "
                     f"| {100 * gap:.0f} |")
    lines += ["", "## Stays stock", "", "| File | Map | Why |", "|---|---|---|"]
    lines += [f"| `{n}` | {a['name']} | {why} |" for n, a, why in sorted(stock)]
    with open(LIST_PATH, "w") as f:
        f.write("\n".join(lines) + "\n")

    print(f"planned {len(plan)} maps, {sum(1 for r in rows if r[3] is None)} picked by hand, "
          f"{len(stock)} stay stock -> {PLAN_PATH}, {LIST_PATH}")


if __name__ == "__main__":
    main()
