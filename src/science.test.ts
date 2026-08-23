import { describe, expect, it } from 'vitest'
import { driftSearch } from './science'

const baseline = { signalSnr: 12, driftRate: 1.25, observation: 180, channelWidth: 2.8, trialStep: .05 }

describe('de-Doppler search', () => {
  it('peaks near the injected drift', () => {
    const data = driftSearch(baseline)
    const best = data.reduce((a, b) => b.model > a.model ? b : a)
    expect(Math.abs(best.x - baseline.driftRate)).toBeLessThanOrEqual(baseline.trialStep + .001)
  })
  it('exact match retains full coherent S/N', () => {
    const best = Math.max(...driftSearch(baseline).map((row) => row.model))
    expect(best).toBeCloseTo(baseline.signalSnr, 8)
  })
  it('longer integrations narrow the response', () => {
    const fine = { ...baseline, trialStep: .005 }
    const short = driftSearch({ ...fine, observation: 60 }).filter((row) => row.model > baseline.signalSnr / 2).length
    const long = driftSearch({ ...fine, observation: 300 }).filter((row) => row.model > baseline.signalSnr / 2).length
    expect(long).toBeLessThan(short)
  })
})
