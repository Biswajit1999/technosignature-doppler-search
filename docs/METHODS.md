# Methods

## Drift grid

The search spans ±6 Hz s⁻¹. The user controls grid spacing; the number of points is `floor(12/step)+1`. For display safety, only the densest grids are downsampled, while metrics use every trial.

## Mismatch kernel

The sinc response is the coherent-amplitude loss for the repository's simplified rectangular integration picture. Real incoherent power sums, channelisation, windowing, and discrete track traversal have different responses and must be benchmarked by injection.

## Synthetic noise

Three incommensurate sinusoids generate a deterministic, approximately unit-scale search structure. This makes screenshots and tests reproducible but is not statistically independent Gaussian noise.

## False-alarm bound

`N exp(-z²/2)` is an illustrative union-bound approximation. Adjacent drift trials are correlated, and real spectral backgrounds are non-Gaussian. A production search must calibrate thresholds empirically.

## Tests

The exact-match model peak must recover the injected S/N, the peak drift must fall within one trial step, and increasing observation time must narrow the half-height trial response.
