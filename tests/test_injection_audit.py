import unittest
import numpy as np
from research.injection_audit import (
    fixed_centre_scan, inject_track, phase_offset_audit, recovery_sweep, wilson_interval,
)


class InjectionAuditTests(unittest.TestCase):
    def setUp(self):
        self.t = np.arange(20, dtype=float) * 10
        self.trials = np.arange(-0.4, -0.19, 0.01)

    def test_noiseless_known_track(self):
        data = inject_track(self.t, 128, 3.0, centre=64, drift=-0.3,
                            amplitude=10, noise_sigma=1e-9, seed=1)
        scores, counts = fixed_centre_scan(data, self.t, 3, 64, self.trials)
        self.assertAlmostEqual(float(self.trials[np.argmax(scores)]), -0.3, places=9)
        self.assertEqual(int(counts.min()), 20)

    def test_injection_seed_is_reproducible(self):
        kw = dict(centre=64, drift=-0.3, amplitude=2, seed=41)
        np.testing.assert_array_equal(inject_track(self.t, 128, 3, **kw),
                                      inject_track(self.t, 128, 3, **kw))

    def test_invalid_track_boundary(self):
        with self.assertRaises(ValueError):
            inject_track(self.t, 128, 3, centre=3, drift=-1, amplitude=3)

    def test_flagged_interpolation_is_excluded(self):
        data = np.zeros((20, 128))
        data[:, 64] = 100
        valid = np.ones_like(data, dtype=bool)
        valid[:, 64] = False
        scores, counts = fixed_centre_scan(data, self.t, 3, 64, [0], mask=valid)
        self.assertEqual(int(counts[0]), 0)
        self.assertTrue(np.isnan(scores[0]))

    def test_masked_stationary_rfi_reduces_false_peak(self):
        data = np.zeros((20, 128))
        data[:, 64] = 30
        valid = np.ones_like(data, dtype=bool)
        valid[:, 64] = False
        raw, _ = fixed_centre_scan(data, self.t, 3, 64, [0, -0.3])
        masked, _ = fixed_centre_scan(data, self.t, 3, 64, [0, -0.3], mask=valid)
        self.assertGreater(raw[0], raw[1])
        self.assertTrue(np.isnan(masked[0]))
        self.assertTrue(np.isfinite(masked[1]))

    def test_wilson_edges(self):
        self.assertGreater(wilson_interval(0, 20)[1], 0)
        self.assertLess(wilson_interval(20, 20)[0], 1)
        with self.assertRaises(ValueError):
            wilson_interval(2, 1)

    def test_sweep_high_amplitude_recovers(self):
        rows = recovery_sweep(self.t, 128, 3, centre=64, true_drift=-0.3,
                              trial_drifts=self.trials, amplitudes=[0, 12],
                              replicates=12, seed=10, tolerance=0.015)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[1]["recovered"], 12)
        self.assertGreater(rows[1]["recovery_fraction"], rows[0]["recovery_fraction"])

    def test_phase_grid_offset(self):
        data = inject_track(self.t, 128, 3, centre=64, drift=-0.3,
                            amplitude=10, noise_sigma=1e-8)
        result = phase_offset_audit(data, self.t, 3, 64, true_drift=-0.3,
                                    spacing=0.1, span=0.2)
        self.assertAlmostEqual(result["aligned_best"], -0.3)
        self.assertLess(result["half_step_peak"], result["aligned_peak"])

    def test_invalid_inputs(self):
        with self.assertRaises(ValueError):
            fixed_centre_scan(np.zeros((3, 16)), [0, 1, 1], 2, 8, [0])
        with self.assertRaises(ValueError):
            fixed_centre_scan(np.zeros((3, 16)), [0, 1, 2], 2, 8, [0], mask=np.ones((3, 15)))


if __name__ == "__main__":
    unittest.main()
