"""Build a browser-sized, provenance-rich slice from Berkeley's Voyager 1 HDF5 sample."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

import h5py
import hdf5plugin  # noqa: F401 - registers filters used by Breakthrough Listen HDF5
import numpy as np
import requests


SOURCE_URL = "http://blpd0.ssl.berkeley.edu/Voyager_data/Voyager1.single_coarse.fine_res.h5"
EXPECTED_BYTES = 50_549_227


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fetch(path: Path) -> None:
    if path.exists() and path.stat().st_size == EXPECTED_BYTES:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_suffix(".h5.part")
    with requests.get(SOURCE_URL, stream=True, timeout=120) as response:
        response.raise_for_status()
        with partial.open("wb") as output:
            for chunk in response.iter_content(1024 * 1024):
                output.write(chunk)
    if partial.stat().st_size != EXPECTED_BYTES:
        raise ValueError(f"Unexpected source size: {partial.stat().st_size} != {EXPECTED_BYTES}")
    partial.replace(path)


def scalar(value):
    if isinstance(value, np.ndarray):
        return [scalar(item) for item in value.tolist()]
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    if isinstance(value, np.generic):
        return value.item()
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache", type=Path, default=Path("data/Voyager1.single_coarse.fine_res.h5"))
    parser.add_argument("--output", type=Path, default=Path("public/data/voyager1-waterfall.json"))
    parser.add_argument("--channels", type=int, default=1024)
    args = parser.parse_args()
    fetch(args.cache)

    with h5py.File(args.cache, "r") as source:
        dataset = source["data"]
        raw = np.asarray(dataset[:, 0, :], dtype=np.float32)
        header = {key: scalar(value) for key, value in source["data"].attrs.items()}

    # Reproduce the strongest published turboSETI Voyager hit rather than the
    # coarse-channel DC bin, which is the brightest but scientifically irrelevant.
    target_frequency_mhz = 8419.297028
    peak = int(round((target_frequency_mhz - float(header["fch1"])) / float(header["foff"])))
    half = args.channels // 2
    start = max(0, min(raw.shape[1] - args.channels, peak - half))
    stop = start + args.channels
    sliced = raw[:, start:stop]

    row_median = np.nanmedian(sliced, axis=1, keepdims=True)
    row_mad = np.nanmedian(np.abs(sliced - row_median), axis=1, keepdims=True)
    robust_sigma = np.maximum(1.4826 * row_mad, np.finfo(np.float32).eps)
    normalized_unclipped = (sliced - row_median) / robust_sigma
    normalized = np.clip(normalized_unclipped, -3, 20)

    fch1_mhz = float(header["fch1"])
    foff_mhz = float(header["foff"])
    tsamp = float(header["tsamp"])
    frequencies_mhz = fch1_mhz + (start + np.arange(args.channels)) * foff_mhz
    times_s = np.arange(raw.shape[0]) * tsamp

    trial_drifts = np.linspace(-2, 2, 401)
    x = np.arange(args.channels)
    scores = []
    for drift in trial_drifts:
        channel_shift = drift * times_s / (foff_mhz * 1e6)
        aligned = [np.interp(x, x - shift, row, left=np.nan, right=np.nan) for row, shift in zip(normalized_unclipped, channel_shift)]
        scores.append(float(np.nanmax(np.nanmean(aligned, axis=0))))
    best_index = int(np.nanargmax(scores))

    payload = {
        "schema": "technosignature.voyager-waterfall/1",
        "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
        "source": {
            "url": SOURCE_URL,
            "expectedBytes": EXPECTED_BYTES,
            "actualBytes": args.cache.stat().st_size,
            "sha256": sha256(args.cache),
            "archive": "https://seti.berkeley.edu/opendata/",
            "tutorial": "https://seti.berkeley.edu/listen/data.html",
            "credit": "Breakthrough Listen / UC Berkeley SETI",
        },
        "header": header,
        "selection": {
            "sourceShape": list(raw.shape),
            "channelStart": start,
            "channelStop": stop,
            "publishedHitFrequencyMHz": target_frequency_mhz,
            "frequencyStartMHz": float(frequencies_mhz[0]),
            "frequencyStopMHz": float(frequencies_mhz[-1]),
            "channelWidthHz": abs(foff_mhz * 1e6),
            "integrationSeconds": tsamp,
            "timeSamples": raw.shape[0],
            "normalization": "per-integration median and 1.4826×MAD; clipped to [-3,20] for display",
        },
        "timesSeconds": np.round(times_s, 6).tolist(),
        "frequenciesMHz": np.round(frequencies_mhz, 9).tolist(),
        "waterfallRobustZ": np.round(normalized, 3).tolist(),
        "driftSearch": {
            "method": "brute-force integer-grid interpolation and incoherent shift-and-average",
            "trialsHzPerSecond": np.round(trial_drifts, 4).tolist(),
            "score": np.round(scores, 4).tolist(),
            "bestDriftHzPerSecond": float(trial_drifts[best_index]),
            "bestScore": scores[best_index],
            "warning": "Engineering-carrier recovery on known Voyager telemetry; not an extraterrestrial candidate or survey-calibrated significance.",
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")
    print(json.dumps({"output": str(args.output), "sha256": payload["source"]["sha256"], "bestDrift": payload["driftSearch"]["bestDriftHzPerSecond"]}, indent=2))


if __name__ == "__main__":
    main()
