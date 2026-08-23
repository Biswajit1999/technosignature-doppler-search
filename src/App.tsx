import { useEffect, useRef, useState } from "react";
import "./styles.css";

type VoyagerRecord = {
  source: { url: string; expectedBytes: number; sha256: string; archive: string; tutorial: string; credit: string };
  header: { source_name: string; tstart: number; tsamp: number; foff: number; nchans: number; rawdatafile: string };
  selection: { sourceShape: number[]; channelStart: number; channelStop: number; publishedHitFrequencyMHz: number; frequencyStartMHz: number; frequencyStopMHz: number; channelWidthHz: number; integrationSeconds: number; timeSamples: number; normalization: string };
  timesSeconds: number[];
  frequenciesMHz: number[];
  waterfallRobustZ: number[][];
  driftSearch: { method: string; trialsHzPerSecond: number[]; score: number[]; bestDriftHzPerSecond: number; bestScore: number; warning: string };
};

const DATA_URL = `${import.meta.env.BASE_URL}data/voyager1-waterfall.json`;

function palette(value: number): [number, number, number] {
  const t = Math.max(0, Math.min(1, (value + 3) / 23));
  const stops = [[10, 8, 26], [39, 24, 82], [123, 45, 104], [238, 108, 61], [255, 239, 151]];
  const scaled = t * (stops.length - 1);
  const index = Math.min(stops.length - 2, Math.floor(scaled));
  const fraction = scaled - index;
  return stops[index].map((channel, i) => Math.round(channel + (stops[index + 1][i] - channel) * fraction)) as [number, number, number];
}

function Waterfall({ record, selected, onSelect }: { record: VoyagerRecord; selected: number; onSelect: (row: number) => void }) {
  const canvas = useRef<HTMLCanvasElement>(null);
  useEffect(() => {
    const node = canvas.current;
    if (!node) return;
    const context = node.getContext("2d");
    if (!context) return;
    const rows = record.waterfallRobustZ.length;
    const columns = record.waterfallRobustZ[0].length;
    node.width = columns;
    node.height = rows;
    const pixels = context.createImageData(columns, rows);
    record.waterfallRobustZ.forEach((row, y) => row.forEach((value, x) => {
      const [red, green, blue] = palette(value);
      const offset = (y * columns + x) * 4;
      pixels.data.set([red, green, blue, 255], offset);
    }));
    context.putImageData(pixels, 0, 0);
  }, [record]);
  return <div className="waterfall-frame"><canvas ref={canvas} aria-label="Real Voyager 1 radio power as frequency versus time" onClick={(event) => { const box = event.currentTarget.getBoundingClientRect(); onSelect(Math.min(record.timesSeconds.length - 1, Math.floor((event.clientY - box.top) / box.height * record.timesSeconds.length))); }} /><div className="row-cursor" style={{ top: `${(selected + .5) / record.timesSeconds.length * 100}%` }} /><span className="axis frequency">frequency →</span><span className="axis time">time →</span></div>;
}

function DriftCurve({ record }: { record: VoyagerRecord }) {
  const width = 900, height = 220, pad = 28;
  const min = Math.min(...record.driftSearch.score), max = Math.max(...record.driftSearch.score);
  const points = record.driftSearch.score.map((score, index) => {
    const x = pad + index / (record.driftSearch.score.length - 1) * (width - pad * 2);
    const y = height - pad - (score - min) / (max - min || 1) * (height - pad * 2);
    return `${x},${y}`;
  }).join(" ");
  const bestIndex = record.driftSearch.trialsHzPerSecond.indexOf(record.driftSearch.bestDriftHzPerSecond);
  const bestX = pad + bestIndex / (record.driftSearch.score.length - 1) * (width - pad * 2);
  return <svg className="drift-curve" viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Shift-and-average score versus trial drift rate"><line x1={pad} x2={width-pad} y1={height-pad} y2={height-pad} /><polyline points={points} /><line className="best-line" x1={bestX} x2={bestX} y1={pad} y2={height-pad} /><text x={pad} y={height-6}>−2 Hz s⁻¹</text><text x={width-pad} y={height-6} textAnchor="end">+2 Hz s⁻¹</text></svg>;
}

export default function App() {
  const [record, setRecord] = useState<VoyagerRecord | null>(null);
  const [error, setError] = useState("");
  const [selected, setSelected] = useState(0);
  useEffect(() => { fetch(DATA_URL).then((response) => { if (!response.ok) throw new Error(`HTTP ${response.status}`); return response.json(); }).then(setRecord).catch((reason) => setError(String(reason))); }, []);
  if (error) return <main className="state">Could not open the observation receipt: {error}</main>;
  if (!record) return <main className="state">Tuning to the archived observation…</main>;
  const selectedSpectrum = record.waterfallRobustZ[selected];
  const peakIndex = selectedSpectrum.indexOf(Math.max(...selectedSpectrum));
  const peakFrequency = record.frequenciesMHz[peakIndex];
  const officialDrift = -.373093;
  return <>
    <header className="topbar"><a href="#observation">BL / VOYAGER 1 / 2016</a><nav><a href="#observation">waterfall</a><a href="#search">de-doppler</a><a href="#receipt">receipt</a></nav></header>
    <main id="observation">
      <section className="signal-hero"><p className="kicker">KNOWN HUMAN TRANSMITTER · GREEN BANK TELESCOPE · REAL FILTERBANK DATA</p><h1>Before searching for <em>them,</em><br/>recover <strong>us.</strong></h1><div className="hero-note"><span>Calibration target</span><p>Voyager 1 is a ground-truth engineering carrier: a narrow, drifting signal whose origin is known. This benchmark asks whether the pipeline recovers it without inventing extraterrestrial significance.</p></div></section>
      <section className="observation-console">
        <div className="console-head"><div><span>WATERFALL / ROBUST Z</span><strong>{record.selection.frequencyStartMHz.toFixed(6)}—{record.selection.frequencyStopMHz.toFixed(6)} MHz</strong></div><div><span>TIME ON SOURCE</span><strong>{record.timesSeconds.at(-1)?.toFixed(1)} s</strong></div><div><span>SELECTED INTEGRATION</span><strong>{record.timesSeconds[selected].toFixed(1)} s</strong></div></div>
        <Waterfall record={record} selected={selected} onSelect={setSelected}/>
        <div className="spectrum-strip"><div><span>brightest selected channel</span><strong>{peakFrequency.toFixed(6)} MHz</strong></div><div><span>resolution</span><strong>{record.selection.channelWidthHz.toFixed(4)} Hz</strong></div><div><span>source matrix</span><strong>{record.selection.sourceShape.join(" × ")}</strong></div><div><span>display crop</span><strong>{record.selection.channelStop-record.selection.channelStart} channels</strong></div></div>
      </section>
      <section className="dedoppler" id="search"><div className="section-index">02 / SHIFT + AVERAGE</div><div className="dedoppler-title"><h2>The diagonal<br/>becomes a peak.</h2><div className="drift-result"><span>RECOVERED DRIFT</span><strong>{record.driftSearch.bestDriftHzPerSecond.toFixed(2)}</strong><small>Hz s⁻¹</small></div></div><DriftCurve record={record}/><div className="comparison"><article><span>THIS REDUCTION</span><strong>{record.driftSearch.bestDriftHzPerSecond.toFixed(3)} Hz s⁻¹</strong><p>brute-force interpolated shift-and-average</p></article><article><span>PUBLISHED TURBOSETI EXAMPLE</span><strong>{officialDrift.toFixed(3)} Hz s⁻¹</strong><p>strongest Voyager sample hit near 8419.297 MHz</p></article><article><span>ABSOLUTE DIFFERENCE</span><strong>{Math.abs(record.driftSearch.bestDriftHzPerSecond-officialDrift).toFixed(3)} Hz s⁻¹</strong><p>a reproducible regression target, not a detection claim</p></article></div></section>
      <section className="receipt" id="receipt"><div><span className="section-index">03 / SOURCE RECEIPT</span><h2>Nothing up<br/>our sleeve.</h2></div><ol><li><b>01</b><div><strong>Berkeley source</strong><a href={record.source.url}>Voyager1.single_coarse.fine_res.h5 ↗</a></div></li><li><b>02</b><div><strong>Transfer integrity</strong><code>{record.source.expectedBytes.toLocaleString()} bytes · {record.source.sha256}</code></div></li><li><b>03</b><div><strong>Observation header</strong><code>MJD {record.header.tstart} · Δt {record.header.tsamp}s · Δf {(record.header.foff*1e6).toFixed(6)}Hz</code></div></li><li><b>04</b><div><strong>Reduction</strong><code>{record.selection.normalization}</code></div></li></ol></section>
      <aside className="validity"><strong>VALIDITY BOUNDARY</strong><p>{record.driftSearch.warning} This single on-source excerpt does not perform RFI rejection, on/off cadence comparison, barycentric correction, survey completeness, or a trials-calibrated false-alarm analysis.</p></aside>
    </main>
    <footer><span>{record.source.credit}</span><a href={record.source.archive}>OPEN DATA ARCHIVE ↗</a></footer>
  </>;
}
