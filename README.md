# Technosignature Doppler Search

A provenance-first recovery of the known Voyager 1 engineering carrier in real Green Bank Telescope data, with a reduced synthetic response retained only as a regression model.

[![CI](https://github.com/Biswajit1999/technosignature-doppler-search/actions/workflows/ci.yml/badge.svg)](https://github.com/Biswajit1999/technosignature-doppler-search/actions/workflows/ci.yml)
[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**[Launch the interactive laboratory →](https://biswajit1999.github.io/technosignature-doppler-search/)**

## Motivation

A narrow-band extraterrestrial transmitter would not generally remain in one frequency channel during an observation. Relative acceleration between transmitter, receiver, planets, moons, and observatory produces an apparent frequency drift. A de-Doppler search integrates power along many candidate slopes; a mismatch between injected and trial slopes smears the signal and reduces significance.

This repository connects that physical intuition to an inspectable **real dynamic spectrum** from the UC Berkeley SETI / Breakthrough Listen Voyager sample. The known human transmitter is treated as a ground-truth pipeline calibration target, not an extraterrestrial candidate.

## Real observation receipt

The data builder downloads `Voyager1.single_coarse.fine_res.h5` from Berkeley's official sample server (`50,549,227` bytes), verifies its size, computes SHA-256 `c9a9a54f4140e3754ffb2455fae4eeb2eb70c8207123116ee953e4fce15c36ac`, and reads the bitshuffle-compressed filterbank HDF5 product.

The published browser bundle contains a 16 × 1024-channel excerpt around the strongest turboSETI sample hit near 8419.297 MHz. A per-integration median/MAD normalization is used for display. A brute-force shift-and-average scan recovers **−0.380 Hz s⁻¹**, within **0.007 Hz s⁻¹** of the published turboSETI example value (−0.373093 Hz s⁻¹).

```bash
python -m pip install -r requirements-data.txt
python scripts/build_voyager_slice.py
```

The 50.5 MB source is ignored by Git; the compact derived waterfall, complete source URL, observation header, reduction contract, and source hash are versioned and tested.

## Research question

How should drift-trial spacing scale with observation length and channel width, and when does a nominal peak remain interesting after the number of searched trials is considered?

## Implemented observation workflow

- real Breakthrough Listen filterbank HDF5 ingestion with compression-filter registration;
- exact byte-count and SHA-256 source receipts;
- filterbank header retention: MJD, frequency resolution, integration time, source shape, and raw filename;
- known-hit selection that explicitly excludes the coarse-channel DC artifact;
- browser-sized real waterfall with selectable integrations;
- brute-force interpolated de-Doppler scan over −2 to +2 Hz s⁻¹;
- direct regression comparison with the published turboSETI Voyager result;
- deterministic tests for source integrity, matrix geometry, and recovered drift.

## Reduced comparison model

For drift mismatch `Δd`, observation time `T`, and channel width `Δf`, the coherent response is approximated by

```text
R(Δd) = |sinc(π Δd T / Δf)|.
```

The model detection statistic is `S/N_peak × R`. A deterministic, approximately unit-scale oscillatory term makes a repeatable synthetic search surface. The displayed false-alarm bound is

```text
FAP ≤ Ntrial exp[-(S/N)²/2].
```

This older synthetic model remains in `src/science.ts` for unit tests and intuition. It is not the product's primary evidence and its bound is not a calibrated survey detection statistic.

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
scripts/build_voyager_slice.py  official HDF5 ingestion and real drift scan
public/data/                   compact real waterfall + source receipt
src/voyager-data.test.ts       data integrity and published-drift regression
src/App.tsx                    canvas waterfall, drift audit, provenance ledger
src/science.ts                 reduced sinc-response comparison model
src/science.test.ts            matched-filter invariants
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

The application searches one deliberately selected excerpt of real telescope data and does not claim an extraterrestrial signal. The selected source is Voyager 1—a known human spacecraft. It does not yet implement survey-scale bandpass calibration, spectral-kurtosis RFI masking, a tree/GPU de-Doppler algorithm, barycentric correction, hit clustering, on/off-source cadence comparison, or a candidate database.

Any real candidate requires terrestrial-interference rejection, repeat observations, sky-localisation consistency, independent instrumentation, and cautious reporting.

## Research upgrade path

1. Add SIGPROC ingestion and a streaming multi-coarse-channel backend.
2. Generate seeded complex-voltage or power injections with known drift/width.
3. Compare this brute-force result with tree, turboSETI, and GPU hyperseti implementations.
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
