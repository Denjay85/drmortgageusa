import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";
import ts from "typescript";

const source = await readFile(new URL("../app/rate-model.ts", import.meta.url), "utf8");
const output = ts.transpileModule(source, { compilerOptions: { target: ts.ScriptTarget.ES2022, module: ts.ModuleKind.ES2022 } }).outputText;
const model = await import(`data:text/javascript;base64,${Buffer.from(output).toString("base64")}`);
const fixture = {
  verified: true, status: "verified", asOf: "2026-10-13",
  source: { name: "Mortgage News Daily", url: "https://www.mortgagenewsdaily.com/mortgage-rates" },
  rates: { "Conventional 30-year": "7.46%", "Conventional 15-year": "7.14%", "FHA 30-year": "7.13%", "VA 30-year": "7.15%", "Jumbo 30-year": "7.62%" },
};

for (const [id, label, mode, years, rate] of [
  ["conventional-30", "Conventional 30-year", "purchase", 30, 7.46],
  ["conventional-15", "Conventional 15-year", "purchase", 15, 7.14],
  ["fha-30", "FHA 30-year", "fha", 30, 7.13],
  ["va-30", "VA 30-year", "va-purchase", 30, 7.15],
  ["jumbo-30", "Jumbo 30-year", "purchase", 30, 7.62],
]) {
  test(`${label} carries its selector, calculator, rate and loan term`, () => {
    const definition = model.rateModelIndexes.find((item) => item.id === id);
    assert.ok(definition);
    assert.equal(model.modelPaymentHref(definition), `/tools?rateIndex=${id}#${mode}`);
    const selected = model.readRateIndexSelection(`?rateIndex=${id}&rate=1&term=5`);
    assert.equal(selected.id, id);
    const assumption = model.resolveIndexAssumption(selected, fixture);
    assert.equal(assumption.rate, rate);
    assert.equal(assumption.years, years);
    assert.equal(assumption.mode, mode);
    assert.equal(assumption.asOf, fixture.asOf);
    assert.equal(assumption.label, label);
  });
}

test("URLs select the program, never supply unverified rates or dates", () => {
  assert.equal(model.readRateIndexSelection("?rate=3&asOf=2099-01-01"), null);
  assert.equal(model.readRateIndexSelection("?rateIndex=__proto__"), null);
  assert.equal(model.readRateIndexSelection("?rateIndex=javascript:alert(1)"), null);
  assert.equal(model.readRateIndexSelection("?rateIndex=unknown"), null);
});

test("failed, incomplete or undated source data never becomes an index assumption", () => {
  const index = model.rateModelIndexes[0];
  for (const payload of [null, {}, { ...fixture, verified: false }, { ...fixture, status: "unavailable" }, { ...fixture, asOf: "" }, { ...fixture, asOf: "not a date" }, { ...fixture, rates: {} }]) {
    assert.equal(model.resolveIndexAssumption(index, payload), null);
  }
});

test("invalid rates never enter payment math", () => {
  const index = model.rateModelIndexes[0];
  for (const rate of ["0%", "-7%", "99%", "NaN%", "7% junk", "7.46", "<script>", 7.46, null]) {
    assert.equal(model.resolveIndexAssumption(index, { ...fixture, rates: { ...fixture.rates, [index.label]: rate } }), null);
  }
});

test("a new source snapshot replaces old hardcoded assumptions without changing the selector", () => {
  const selected = model.readRateIndexSelection("?rateIndex=conventional-15&rate=2");
  const changed = model.resolveIndexAssumption(selected, { ...fixture, asOf: "2026-10-14", rates: { ...fixture.rates, "Conventional 15-year": "7.01%" } });
  assert.equal(changed.rate, 7.01);
  assert.equal(changed.years, 15);
  assert.equal(changed.asOf, "2026-10-14");
});
