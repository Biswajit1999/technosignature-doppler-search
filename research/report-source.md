# Internal research synthesis and claim ledger

## Decision

Use the known Voyager 1 engineering downlink as an end-to-end de-Doppler calibration target. Preserve the reduced sinc model only as a controlled unit-test layer.

## Primary evidence

1. Berkeley SETI publishes Breakthrough Listen data and explicitly proposes reproducing the Voyager waterfall, carrier frequency, and drift: https://seti.berkeley.edu/listen/data.html
2. The official Breakthrough Listen open-data archive describes the public filterbank/HDF5 route: https://seti.berkeley.edu/opendata/
3. turboSETI's official repository reports the sample's strongest hit near 8419.297028 MHz at −0.373093 Hz/s: https://github.com/UCBerkeleySETI/turbo_seti
4. blimpy documents the HDF5/filterbank data model and lazy spectral access: https://github.com/UCBerkeleySETI/blimpy

## Claim ledger

| Claim | Support | Confidence | Design response |
|---|---|---:|---|
| the bundled excerpt derives from real GBT Voyager data | official Berkeley sample URL, exact byte count, SHA-256 | high | version the receipt and test it |
| the selected line is a known human engineering carrier | Berkeley tutorial and Voyager target header | high | describe it as calibration, never ET evidence |
| the reduced scan reproduces the published drift | turboSETI example vs local −0.380 Hz/s result | high | regression-test absolute difference below 0.02 Hz/s |
| the brightest full-band bin is scientifically useful | contradicted by coarse-channel DC artifact | high | select the published hit frequency, document exclusion |
| one excerpt establishes candidate significance | unsupported | high | show explicit RFI/cadence/trials validity boundary |
