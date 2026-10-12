import numpy as np
import pytest

from research.voyager_validation import drift_scores, grid_convergence


def synthetic_track(drift=-0.3, integrations=16, channels=128, width=3.0, dt=10.0):
    time = np.arange(integrations) * dt
    data = np.zeros((integrations, channels))
    center = channels // 2
    for index, seconds in enumerate(time):
        channel = int(round(center + drift * seconds / width))
        data[index, channel] = 10
    return data, time, width


def test_drift_scan_recovers_synthetic_track():
    data, time, width = synthetic_track()
    trials = np.linspace(-0.5, -0.1, 81)
    scores = drift_scores(data, time, width, trials)
    assert trials[np.argmax(scores)] == pytest.approx(-0.3, abs=0.02)


def test_grid_convergence_is_finite():
    data, time, width = synthetic_track()
    rows = grid_convergence(data, time, width, spacings=(0.1, 0.02))
    assert len(rows) == 2
    assert all(np.isfinite(row["best_score"]) for row in rows)
