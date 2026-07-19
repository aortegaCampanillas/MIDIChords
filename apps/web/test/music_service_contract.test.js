const assert = require("node:assert/strict");
const { readFileSync } = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const contractPath = path.resolve(__dirname, "../../../tests/fixtures/music_service_contract.json");
const contract = JSON.parse(readFileSync(contractPath, "utf8"));
const workerModule = import("../worker/_worker.js");

function evaluate(worker, operation, input) {
  const common = {
    language: input.language,
    preferFlat: input.prefer_flat,
  };
  if (operation === "generate_chord") {
    return worker.generateChord({
      ...common,
      rootPc: input.root_pc,
      suffix: input.suffix,
      inversion: input.inversion,
    });
  }
  if (operation === "generate_scale") {
    return worker.generateScale({
      ...common,
      tonicPc: input.tonic_pc,
      patternName: input.pattern_name,
    });
  }
  if (operation === "detect_chord") {
    return worker.detectChord({ ...common, notes: input.notes });
  }
  throw new Error(`Unknown contract operation: ${operation}`);
}

for (const contractCase of contract.cases) {
  test(`worker music contract: ${contractCase.id}`, async () => {
    const worker = await workerModule;
    const result = evaluate(worker, contractCase.operation, contractCase.input);
    const actual = Object.fromEntries(
      Object.keys(contractCase.expected).map((field) => [field, result[field]]),
    );
    assert.deepEqual(actual, contractCase.expected);
  });
}
