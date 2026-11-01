"""Controlled power-spectrum injection tests for a *fixed* known-carrier channel.

This is not a blind survey search: centre frequency is supplied, and independent
Gaussian power residuals are a deliberately simplified noise model.
"""

from __future__ import annotations

import numpy as np


def _geometry(times_s, channels, width_hz):
    t = np.asarray(times_s, dtype=float)
    if t.ndim != 1 or t.size < 3 or not np.all(np.isfinite(t)) or np.any(np.diff(t) <= 0):
        raise ValueError("times must be finite, strictly increasing and have >=3 samples")
    if not isinstance(channels, (int, np.integer)) or channels < 8:
        raise ValueError("at least eight channels required")
    if not np.isfinite(width_hz) or width_hz <= 0:
        raise ValueError("channel width must be positive")
    return t - t[0]


def inject_track(times_s, channels, width_hz, *, centre, drift, amplitude,
                 line_sigma=0.8, noise_sigma=1.0, seed=0):
    """Add a drifting Gaussian-in-channel *power* feature to iid Gaussian noise."""
    t = _geometry(times_s, channels, width_hz)
    if not all(np.isfinite(x) for x in (centre, drift, amplitude, line_sigma, noise_sigma)):
        raise ValueError("non-finite injection parameter")
    if amplitude < 0 or line_sigma <= 0 or noise_sigma <= 0:
        raise ValueError("amplitude >= 0 and positive widths/noise required")
    positions = centre + drift * t / width_hz
    if np.any((positions < 3 * line_sigma) | (positions > channels - 1 - 3 * line_sigma)):
        raise ValueError("track extends beyond the usable channel window")
    rng = np.random.default_rng(seed)
    x = np.arange(channels)
    signal = amplitude * np.exp(-0.5 * ((x[None, :] - positions[:, None]) / line_sigma) ** 2)
    return signal + rng.normal(0.0, noise_sigma, size=signal.shape)


def fixed_centre_scan(waterfall, times_s, width_hz, centre, trials, mask=None):
    """Mean sampled power along each trial, with explicit valid-sample counts.

    Linear interpolation uses both adjacent channels. A flagged channel invalidates
    an interpolated sample touching it; no interpolation across masked RFI occurs.
    """
    data = np.asarray(waterfall, dtype=float)
    if data.ndim != 2 or not np.all(np.isfinite(data)):
        raise ValueError("waterfall must be a finite 2D matrix")
    t = _geometry(times_s, data.shape[1], width_hz)
    if data.shape[0] != len(t):
        raise ValueError("time and waterfall lengths differ")
    d = np.asarray(trials, dtype=float)
    if d.ndim != 1 or not d.size or not np.all(np.isfinite(d)):
        raise ValueError("finite nonempty trial grid required")
    valid = np.ones(data.shape, dtype=bool) if mask is None else np.asarray(mask, dtype=bool)
    if valid.shape != data.shape:
        raise ValueError("valid-mask shape differs from waterfall")
    scores, counts = [], []
    for slope in d:
        p = centre + slope * t / width_hz
        lo = np.floor(p).astype(int)
        hi = np.ceil(p).astype(int)
        inside = (lo >= 0) & (hi < data.shape[1])
        safe_lo = np.clip(lo, 0, data.shape[1] - 1)
        safe_hi = np.clip(hi, 0, data.shape[1] - 1)
        idx = np.arange(len(t))
        use = inside & valid[idx, safe_lo] & valid[idx, safe_hi]
        values = data[idx, safe_lo] * (1 - (p - lo)) + data[idx, safe_hi] * (p - lo)
        counts.append(int(np.sum(use)))
        scores.append(float(np.mean(values[use])) if np.any(use) else float("nan"))
    return np.asarray(scores), np.asarray(counts)


def wilson_interval(successes, trials, z=1.959963984540054):
    if not 0 <= successes <= trials or trials < 1:
        raise ValueError("invalid binomial counts")
    p = successes / trials
    den = 1 + z * z / trials
    mid = (p + z * z / (2 * trials)) / den
    half = z * np.sqrt(p * (1 - p) / trials + z * z / (4 * trials**2)) / den
    return float(mid - half), float(mid + half)


def recovery_sweep(times_s, channels, width_hz, *, centre, true_drift,
                   trial_drifts, amplitudes, replicates=50, seed=20261101,
                   tolerance=None):
    """Seeded conditional drift recovery; does not calibrate false alarms."""
    trials = np.asarray(trial_drifts, dtype=float)
    if tolerance is None:
        tolerance = float(np.max(np.diff(np.sort(trials)))) / 2 if len(trials) > 1 else 0.0
    if not np.isfinite(tolerance) or tolerance < 0 or replicates < 1:
        raise ValueError("invalid recovery settings")
    out = []
    for k, amplitude in enumerate(amplitudes):
        recovered, scores = [], []
        for j in range(replicates):
            data = inject_track(times_s, channels, width_hz, centre=centre,
                                drift=true_drift, amplitude=float(amplitude),
                                seed=seed + k * replicates + j)
            scan, counts = fixed_centre_scan(data, times_s, width_hz, centre, trials)
            if not np.any(np.isfinite(scan)):
                raise ValueError("no valid scan trials")
            best = int(np.nanargmax(scan))
            recovered.append(float(trials[best]))
            scores.append(float(scan[best]))
        hits = sum(abs(v - true_drift) <= tolerance + 1e-12 for v in recovered)
        lo, hi = wilson_interval(hits, replicates)
        out.append({"amplitude": float(amplitude), "replicates": replicates,
                    "recovered": hits, "recovery_fraction": hits / replicates,
                    "wilson_95": [lo, hi],
                    "median_drift_bias_hz_s": float(np.median(recovered) - true_drift),
                    "median_peak_power": float(np.median(scores))})
    return out


def phase_offset_audit(waterfall, times_s, width_hz, centre, *, true_drift, spacing, span=0.2):
    """Compare trial grids centred on truth and shifted by half a trial."""
    if not np.isfinite(spacing) or spacing <= 0 or span <= 0:
        raise ValueError("positive grid spacing/span required")
    n = max(1, int(np.floor(span / spacing)))
    base = true_drift + spacing * np.arange(-n, n + 1)
    offset = base + spacing / 2
    a, ca = fixed_centre_scan(waterfall, times_s, width_hz, centre, base)
    b, cb = fixed_centre_scan(waterfall, times_s, width_hz, centre, offset)
    return {"spacing_hz_s": float(spacing), "aligned_best": float(base[np.nanargmax(a)]),
            "half_step_best": float(offset[np.nanargmax(b)]),
            "aligned_peak": float(np.nanmax(a)), "half_step_peak": float(np.nanmax(b)),
            "half_step_over_aligned": float(np.nanmax(b) / np.nanmax(a)),
            "minimum_coverage": int(min(np.min(ca), np.min(cb)))}
