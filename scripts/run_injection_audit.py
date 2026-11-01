"""Reproduce fixed-centre Voyager-like synthetic injection diagnostics offline."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from research.injection_audit import (  # noqa: E402
    fixed_centre_scan, inject_track, phase_offset_audit, recovery_sweep,
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--figure", type=Path)
    args = parser.parse_args()
    times = np.arange(20, dtype=float) * 10
    width, centre, drift = 3.0, 64, -0.3
    trials = np.linspace(-0.5, -0.1, 81)
    sweep = recovery_sweep(times, 128, width, centre=centre, true_drift=drift,
                           trial_drifts=trials, amplitudes=[0, 1, 2, 4, 8],
                           replicates=80, tolerance=0.015)
    data = inject_track(times, 128, width, centre=centre, drift=drift,
                        amplitude=8, seed=13)
    phases = [phase_offset_audit(data, times, width, centre, true_drift=drift,
                                 spacing=spacing) for spacing in (0.02, 0.05, 0.1)]
    contaminated = data.copy()
    contaminated[:, centre] += 30
    valid = np.ones(contaminated.shape, dtype=bool)
    valid[:, centre] = False
    raw, raw_n = fixed_centre_scan(contaminated, times, width, centre, trials)
    masked, masked_n = fixed_centre_scan(contaminated, times, width, centre, trials, valid)
    result = {
        "kind": "seeded synthetic power residuals, fixed known-carrier centre",
        "seed": 20261101,
        "assumptions": "independent Gaussian residuals; Gaussian spectral line; 20 integrations; no blind frequency search or real-data calibration",
        "sweep": sweep, "trial_grid_phase": phases,
        "stationary_rfi": {
            "injected_power": 30,
            "unmasked_best_drift_hz_s": float(trials[np.nanargmax(raw)]),
            "masked_best_drift_hz_s": float(trials[np.nanargmax(masked)]),
            "unmasked_peak_power": float(np.nanmax(raw)),
            "masked_peak_power": float(np.nanmax(masked)),
            "minimum_unmasked_coverage": int(raw_n.min()),
            "minimum_masked_coverage": int(masked_n.min()),
        },
    }
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n")
    if args.figure:
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(7, 4.5))
        ax.plot([r["amplitude"] for r in sweep],
                [r["recovery_fraction"] for r in sweep], marker="o")
        ax.set(xlabel="Injected peak power / residual noise σ",
               ylabel="Fraction of trials recovering injected drift",
               ylim=(-0.05, 1.05), title="Conditional synthetic drift recovery")
        fig.tight_layout()
        args.figure.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(args.figure, dpi=150)
        plt.close(fig)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
