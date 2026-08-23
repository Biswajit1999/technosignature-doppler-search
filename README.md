# Technosignature Doppler Search

An interactive narrow-band radio de-Doppler experiment for understanding coherent loss, trial spacing, and trials-aware significance.

[![CI](https://github.com/Biswajit1999/technosignature-doppler-search/actions/workflows/ci.yml/badge.svg)](https://github.com/Biswajit1999/technosignature-doppler-search/actions/workflows/ci.yml)
[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## Motivation

A narrow-band extraterrestrial transmitter would not generally remain in one frequency channel during an observation. Relative acceleration between transmitter, receiver, planets, moons, and observatory produces an apparent frequency drift. A de-Doppler search integrates power along many candidate slopes; a mismatch between injected and trial slopes smears the signal and reduces significance.

This repository connects that physical intuition to an inspectable matched-filter response, extending Biswajit Jana's work with Breakthrough Listen tooling and Voyager radio waterfall data.

## Research question

How should drift-trial spacing scale with observation length and channel width, and when does a nominal peak remain interesting after the number of searched trials is considered?

## Implemented experiment

- injected constant linear drift from −5 to +5 Hz s⁻¹;
- configurable coherent peak S/N;
- rectangular-window sinc mismatch response;
- symmetric ±6 Hz s⁻¹ search range;
- deterministic unit-scale search structure;
- recovered drift, mismatch loss, coherence width, trial count, and false-alarm upper bound;
- accessible SVG detection curve and data table;
- deterministic tests for peak location, exact-match S/N, and response narrowing.

## Model

For drift mismatch `Δd`, observation time `T`, and channel width `Δf`, the coherent response is approximated by

```text
R(Δd) = |sinc(π Δd T / Δf)|.
```

The model detection statistic is `S/N_peak × R`. A deterministic, approximately unit-scale oscillatory term makes a repeatable synthetic search surface. The displayed false-alarm bound is

```text
FAP ≤ Ntrial exp[-(S/N)²/2].
```

It is a pedagogical bound, not a calibrated survey detection statistic.

## Run

```bash
git clone https://github.com/Biswajit1999/technosignature-doppler-search.git
cd technosignature-doppler-search
npm install
npm run dev
```

## Verify

```bash
npm run check
```

## Repository map

```text
src/science.ts       drift grid, sinc response, peak, FAP bound
src/science.test.ts  matched-filter invariants
src/project.ts       search controls and assumptions
src/Chart.tsx        accessible statistic-versus-drift view
docs/METHODS.md      signal model and validation boundary
design-system/       persisted UI design contract
```

## Useful experiments

- increase observation length while holding trial spacing fixed;
- reduce channel width and watch the coherence width narrow;
- place the injection halfway between two trial drifts;
- expand trial density and observe the trials penalty;
- lower coherent S/N until a visually obvious local peak is statistically uninteresting.

## Scope and responsible interpretation

The application does **not** search telescope data and does not claim an extraterrestrial signal. It has no real filterbank reader, bandpass normalisation, RFI masking, tree de-Doppler algorithm, barycentric correction, hit clustering, cadence logic, on/off-source comparison, or candidate database.

Any real candidate requires terrestrial-interference rejection, repeat observations, sky-localisation consistency, independent instrumentation, and cautious reporting.

## Research upgrade path

1. Read SIGPROC/filterbank or HDF5 products through a validated backend.
2. Generate seeded complex-voltage or power injections with known drift/width.
3. Compare brute-force, tree, and GPU de-Doppler implementations.
4. Calibrate detection statistics on off-source and scrambled data.
5. Add barycentric/ephemeris context and non-linear drift.
6. Implement cadence-based RFI rejection and hit clustering.
7. Publish completeness as a function of S/N, width, drift, and occupancy.

## References

- Enriquez, J. E. et al. (2017), *The Breakthrough Listen Search for Intelligent Life: 1.1–1.9 GHz observations of 692 nearby stars*, [ApJ 849, 104](https://doi.org/10.3847/1538-4357/aa8d1b).
- Sheikh, S. Z. et al. (2019), *Choosing a maximum drift rate in a SETI search*, [ApJ 884, 14](https://doi.org/10.3847/1538-4357/ab3fa8).
- turboSETI documentation and source: [UCBerkeleySETI/turbo_seti](https://github.com/UCBerkeleySETI/turbo_seti).

## Citation and license

See [`CITATION.cff`](CITATION.cff). Licensed under [MIT](LICENSE).
