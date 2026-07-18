import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

import {
  detectChord,
  generateChord,
  generateScale,
} from "../worker/_worker.js";

const contractUrl = new URL("../../../tests/fixtures/music_service_contract.json", import.meta.url);
const contract = JSON.parse(await readFile(contractUrl, "utf8"));

function evaluate(operation, input) {
  const common = {
    language: input.language,
    preferFlat: input.prefer_flat,
  };
  if (operation === "generate_chord") {
    return generateChord({
      ...common,
      rootPc: input.root_pc,
      suffix: input.suffix,
      inversion: input.inversion,
    });
  }
  if (operation === "generate_scale") {
    return generateScale({
      ...common,
      tonicPc: input.tonic_pc,
      patternName: input.pattern_name,
    });
  }
  if (operation === "detect_chord") {
    return detectChord({ ...common, notes: input.notes });
  }
  throw new Error(`Unknown contract operation: ${operation}`);
}

for (const contractCase of contract.cases) {
  test(`worker music contract: ${contractCase.id}`, () => {
    const result = evaluate(contractCase.operation, contractCase.input);
    const actual = Object.fromEntries(
      Object.keys(contractCase.expected).map((field) => [field, result[field]]),
    );
    assert.deepEqual(actual, contractCase.expected);
  });
}
