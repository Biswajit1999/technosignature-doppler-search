# Fixed-centre Doppler injection sensitivity (1 November 2026)

The committed real Green Bank Telescope waterfall is **not** a blind technosignature detection: the selected 16-integration excerpt is centred on the known Voyager 1 engineering carrier. The existing drift-grid, jackknife and circular-shift null studies are unchanged. This separate audit adds three *synthetic* conditional checks without reinterpreting the real-data null.

1. **Power-track injection/recovery.** Generate a Gaussian-in-channel drifting feature with additive independent Gaussian residuals. For each amplitude, use 80 deterministic noise realizations, scan a fixed known centre across -0.5 to -0.1 Hz/s and count recovery within 0.015 Hz/s of the injected -0.3 Hz/s. Wilson intervals describe finite-simulation uncertainty, not detection completeness in real radio interference.
2. **Trial-grid phase.** Compare drift grids centred on truth with grids displaced by half a step at three declared spacings. Linear interpolation samples the predicted channel; the result depends on line width, time span, grid alignment and noise realization. The comparison is not a matched coherent-voltage search.
3. **Stationary RFI mask.** Add a bright constant-frequency contaminant, then explicitly exclude its channel from both interpolation endpoints. Report best trial and retained integration counts with and without masking. This is an idealized, externally supplied mask, not a learned RFI classifier.

The noise model is Gaussian *power residuals*, not exponential raw power or real telescope noise. The central frequency is fixed and supplied; no look-elsewhere correction over frequency, empirical false-alarm calibration, telescope bandpass correction or barycentric drift is included. Do not use recovery fraction as a SETI detection probability.

Reproduce with python scripts/run_injection_audit.py --output /tmp/injection.json --figure /tmp/injection.png; tests: python -m unittest discover -s tests -p test_injection_audit.py.

AI assistance was used in preparing this research code; Git authorship is attributed only to the authenticated repository owner.
