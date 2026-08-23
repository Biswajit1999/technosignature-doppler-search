import { describe, expect, it } from "vitest";
import record from "../public/data/voyager1-waterfall.json";

describe("real Voyager 1 observation receipt", () => {
  it("retains source integrity and filterbank geometry", () => {
    expect(record.source.actualBytes).toBe(record.source.expectedBytes);
    expect(record.source.sha256).toMatch(/^[a-f0-9]{64}$/);
    expect(record.source.url).toContain("berkeley.edu/Voyager_data/");
    expect(record.waterfallRobustZ).toHaveLength(16);
    expect(record.waterfallRobustZ[0]).toHaveLength(1024);
    expect(record.selection.channelWidthHz).toBeCloseTo(2.7939677, 5);
  });

  it("reproduces the published strongest-hit drift rate", () => {
    expect(record.driftSearch.bestDriftHzPerSecond).toBeCloseTo(-0.373093, 1);
    expect(Math.abs(record.driftSearch.bestDriftHzPerSecond + 0.373093)).toBeLessThan(0.02);
  });
});
