"""Run convergence, jackknife, and scrambled-null tests on real Voyager data."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import h5py
import hdf5plugin  # noqa: F401 - register the source file's bitshuffle filter
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from research.voyager_validation import (  # noqa: E402
    circular_shift_null,
    grid_convergence,
    integration_jackknife,
)


def write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    payload = json.loads(
        (ROOT / "public/data/voyager1-waterfall.json").read_text(encoding="utf-8")
    )
    source = ROOT / "data" / "Voyager1.single_coarse.fine_res.h5"
    if not source.is_file():
        raise FileNotFoundError(
            "Run scripts/build_voyager_slice.py to fetch the verified source HDF5 first"
        )
    with source.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    if digest != payload["source"]["sha256"]:
        raise ValueError("source HDF5 SHA-256 does not match the committed receipt")
    start, stop = (
        payload["selection"]["channelStart"],
        payload["selection"]["channelStop"],
    )
    with h5py.File(source, "r") as handle:
        waterfall = np.asarray(handle["data"][:, 0, start:stop], dtype=float)
    row_median = np.median(waterfall, axis=1, keepdims=True)
    row_mad = np.median(np.abs(waterfall - row_median), axis=1, keepdims=True)
    waterfall = (waterfall - row_median) / np.maximum(
        1.4826 * row_mad, np.finfo(float).eps
    )
    times = np.asarray(payload["timesSeconds"], dtype=float)
    width = float(payload["selection"]["channelWidthHz"])
    trials = np.linspace(-0.6, -0.2, 81)
    convergence = grid_convergence(waterfall, times, width)
    jackknife = integration_jackknife(waterfall, times, width, trials)
    null = circular_shift_null(waterfall, times, width, trials)
    write_csv(ROOT / "research/voyager-grid-convergence.csv", convergence)
    write_csv(ROOT / "research/voyager-integration-jackknife.csv", jackknife)
    result = {
        "data_kind": "real Green Bank Telescope Voyager 1 engineering-carrier HDF5 excerpt",
        "source_sha256": payload["source"]["sha256"],
        "grid_convergence": convergence,
        "integration_jackknife": jackknife,
        "circular_shift_null": null,
        "limitations": "The excerpt was deliberately selected around a known human transmitter. The scrambled null is a pipeline diagnostic, not a survey-calibrated false-alarm probability or technosignature claim.",
    }
    (ROOT / "research/voyager-drift-validation.json").write_text(
        json.dumps(result, indent=2), encoding="utf-8"
    )
    figure, axes = plt.subplots(1, 2, figsize=(11, 4.5), constrained_layout=True)
    axes[0].plot(
        [row["spacing_hz_per_s"] for row in convergence],
        [row["best_drift_hz_per_s"] for row in convergence],
        marker="o",
    )
    axes[0].invert_xaxis()
    axes[0].set(
        xlabel="Trial spacing (Hz/s)",
        ylabel="Recovered drift (Hz/s)",
        title="Drift-grid convergence",
    )
    axes[1].scatter(
        range(len(jackknife)),
        [row["best_drift_hz_per_s"] for row in jackknife],
        color="#b85d00",
    )
    axes[1].axhline(
        convergence[-1]["best_drift_hz_per_s"], color="#334155", linestyle="--"
    )
    axes[1].set(
        xlabel="Omitted integration",
        ylabel="Recovered drift (Hz/s)",
        title="Leave-one-integration-out stability",
    )
    figure.suptitle("Voyager 1 carrier drift validation", fontweight="bold")
    figure.savefig(ROOT / "research/voyager-drift-validation.png", dpi=180)
    plt.close(figure)
    print(
        json.dumps(
            {
                "bestDrift": convergence[-1]["best_drift_hz_per_s"],
                "jackknifeRange": [
                    min(r["best_drift_hz_per_s"] for r in jackknife),
                    max(r["best_drift_hz_per_s"] for r in jackknife),
                ],
                "nullPUpper": null["empirical_p_upper"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
