"""Numerical validation for the committed real Voyager waterfall excerpt."""

from __future__ import annotations

import numpy as np


def drift_scores(
    waterfall: np.ndarray,
    times_s: np.ndarray,
    channel_width_hz: float,
    trials: np.ndarray,
) -> np.ndarray:
    """Return the maximum shift-and-average track score for each drift trial."""
    data = np.asarray(waterfall, dtype=float)
    x = np.arange(data.shape[1])
    scores = []
    for drift in trials:
        shifts = drift * times_s / channel_width_hz
        aligned = np.asarray(
            [
                np.interp(x, x - shift, row, left=np.nan, right=np.nan)
                for row, shift in zip(data, shifts, strict=True)
            ]
        )
        counts = np.sum(np.isfinite(aligned), axis=0)
        means = np.divide(
            np.nansum(aligned, axis=0),
            counts,
            out=np.full(aligned.shape[1], np.nan),
            where=counts > 0,
        )
        scores.append(np.nanmax(means))
    return np.asarray(scores)


def grid_convergence(
    waterfall, times_s, channel_width_hz, spacings=(0.1, 0.05, 0.02, 0.01, 0.005)
):
    rows = []
    for spacing in spacings:
        trials = np.arange(-0.6, -0.2 + spacing / 2, spacing)
        scores = drift_scores(waterfall, times_s, channel_width_hz, trials)
        best = int(np.nanargmax(scores))
        rows.append(
            {
                "spacing_hz_per_s": float(spacing),
                "trial_count": int(trials.size),
                "best_drift_hz_per_s": float(trials[best]),
                "best_score": float(scores[best]),
            }
        )
    return rows


def integration_jackknife(waterfall, times_s, channel_width_hz, trials):
    rows = []
    for omitted in range(len(times_s)):
        keep = np.arange(len(times_s)) != omitted
        scores = drift_scores(waterfall[keep], times_s[keep], channel_width_hz, trials)
        best = int(np.nanargmax(scores))
        rows.append(
            {
                "omitted_integration": omitted,
                "best_drift_hz_per_s": float(trials[best]),
                "best_score": float(scores[best]),
            }
        )
    return rows


def circular_shift_null(
    waterfall, times_s, channel_width_hz, trials, *, replicates=500, seed=20261012
):
    """Destroy cross-time tracks by independently rolling every integration."""
    rng = np.random.default_rng(seed)
    observed = float(np.max(drift_scores(waterfall, times_s, channel_width_hz, trials)))
    maxima = []
    for _ in range(replicates):
        shifted = np.stack(
            [np.roll(row, rng.integers(0, row.size)) for row in waterfall]
        )
        maxima.append(
            float(np.max(drift_scores(shifted, times_s, channel_width_hz, trials)))
        )
    exceedances = sum(value >= observed for value in maxima)
    return {
        "replicates": replicates,
        "seed": seed,
        "observed_max_score": observed,
        "null_median_max_score": float(np.median(maxima)),
        "null_p95_max_score": float(np.percentile(maxima, 95)),
        "exceedances": exceedances,
        "empirical_p_upper": float((exceedances + 1) / (replicates + 1)),
    }
