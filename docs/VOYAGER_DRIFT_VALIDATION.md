# Voyager carrier drift validation

The validation reopens the verified Green Bank Telescope HDF5 source and uses
the same 16 × 1024 excerpt selected around the known Voyager 1 engineering
carrier. It is a human
transmitter used as pipeline ground truth, never an extraterrestrial candidate.

The validation measures drift-grid convergence between 0.1 and 0.005 Hz/s,
leave-one-integration-out stability across all 16 integrations, and a
deterministic circular-shift null. The null independently rolls each spectrum,
destroying any coherent cross-time track while preserving each integration's
channel distribution. Its maximum over 81 searched drifts is compared with the
observed maximum, including the local trials factor.

Run `python scripts/validate_voyager_drift.py`.

The fine grids recover -0.380 Hz/s, but omission of integration 12 moves the
best trial to -0.535 Hz/s. The circular-shift maximum exceeds the observed
score in most replicates (`p_upper = 0.938`), demonstrating that this simple
maximum score is not a calibrated detection statistic even for a known carrier.
That negative result is retained rather than converted into a significance
claim.

The runner uses the unclipped robust-normalized powers rather than the browser's
display-clipped copy and hard-fails if the HDF5 SHA-256 differs from the
committed receipt. The scrambled null calibrates this excerpt and algorithm
only; it is not a
survey-scale false-alarm probability, RFI rejection result, or technosignature
detection statistic.

