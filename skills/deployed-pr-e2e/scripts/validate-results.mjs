#!/usr/bin/env node
/**
 * Validate a deployed-pr-e2e RESULTS.json (+ optional pack happy-path).
 */
import { readFileSync, existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const RESULTS = ["PASS", "FAIL", "BLOCKED"];
const DIMENSIONS = [
  "use-cases",
  "edge-cases",
  "workflow-loop",
  "speed",
  "ui-ux",
];

function fail(msg) {
  console.error(`FAIL: ${msg}`);
  process.exit(1);
}

function loadJson(path) {
  try {
    return JSON.parse(readFileSync(path, "utf8"));
  } catch (err) {
    fail(`cannot parse ${path}: ${err.message}`);
  }
}

function parsePackHappyPath(packPath) {
  if (!packPath || !existsSync(packPath)) return [];
  const text = readFileSync(packPath, "utf8");
  const m = text.match(/^---\r?\n([\s\S]*?)\r?\n---/);
  if (!m) return [];
  const ids = [];
  let inHappy = false;
  for (const line of m[1].split(/\r?\n/)) {
    if (/^happy_path:\s*$/.test(line)) {
      inHappy = true;
      continue;
    }
    if (inHappy) {
      const item = line.match(/^\s+-\s+(\S+)/);
      if (item) ids.push(item[1]);
      else if (/^\S/.test(line)) inHappy = false;
    }
  }
  return ids;
}

function validate(doc, happyPath) {
  const errs = [];
  if (!doc || typeof doc !== "object") return ["RESULTS.json must be an object"];
  if (!doc.proof || doc.proof.host !== "https://staging.plxcustomer.io") {
    errs.push("proof.host must be https://staging.plxcustomer.io");
  }
  if (!doc.proof?.sha || !/^[0-9a-f]{40}$/.test(doc.proof.sha)) {
    errs.push("proof.sha must be a 40-char hex");
  }
  if (!doc.proof?.deploymentId || !String(doc.proof.deploymentId).startsWith("dpl_")) {
    errs.push("proof.deploymentId must start with dpl_");
  }
  if (!Array.isArray(doc.rows) || doc.rows.length < 1) {
    errs.push("rows must be a non-empty array");
  }
  const byId = new Map();
  for (const [i, row] of (doc.rows || []).entries()) {
    if (!row.id) errs.push(`rows[${i}] missing id`);
    if (!RESULTS.includes(row.result)) {
      errs.push(`rows[${i}] result must be PASS|FAIL|BLOCKED`);
    }
    if (row.result === "PASS") {
      const proof = (row.evidence && String(row.evidence).trim()) || row.httpProof;
      if (!proof) errs.push(`${row.id || i}: PASS requires evidence or httpProof`);
    }
    if (row.id) byId.set(row.id, row);
  }
  const dim = doc.dimensions || {};
  for (const key of DIMENSIONS) {
    if (!Array.isArray(dim[key]) || dim[key].length < 1) {
      errs.push(`dimensions.${key} must be a non-empty array of row ids`);
    }
  }
  for (const id of happyPath) {
    const row = byId.get(id);
    if (!row) errs.push(`happy-path ${id} is missing from rows`);
    else if (row.result === "FAIL") {
      errs.push(`happy-path ${id} is FAIL — not operator-ready`);
    }
  }
  if (doc.verdict === "operator-ready") {
    const iv = Number(doc.independentVerify?.score);
    if (!(iv > 8)) {
      errs.push("operator-ready requires independentVerify.score > 8");
    }
    for (const id of happyPath) {
      const row = byId.get(id);
      if (row && row.result === "FAIL") {
        errs.push(`verdict operator-ready but happy-path ${id} is FAIL`);
      }
    }
    for (const key of DIMENSIONS) {
      for (const id of dim[key] || []) {
        const row = byId.get(id);
        if (row && row.result === "FAIL") {
          errs.push(`verdict operator-ready but dimension ${key} ${id} is FAIL`);
        }
      }
    }
  }
  return errs;
}

const selftest = process.argv.includes("--selftest");
const packIdx = process.argv.indexOf("--pack");
const packPath = packIdx >= 0 ? process.argv[packIdx + 1] : "";
const target = process.argv.find(
  (a, i) => i > 1 && !a.startsWith("--") && process.argv[i - 1] !== "--pack",
);

if (selftest) {
  const here = dirname(fileURLToPath(import.meta.url));
  const fixture = join(here, "..", "examples", "RESULTS.selftest.json");
  const doc = loadJson(fixture);
  const errs = validate(doc, ["BCOM-01"]);
  if (errs.length) {
    for (const e of errs) console.error(`FAIL: ${e}`);
    process.exit(1);
  }
  const bad = structuredClone(doc);
  bad.rows[0].evidence = "";
  bad.rows[0].httpProof = "";
  const badErrs = validate(bad, ["BCOM-01"]);
  if (!badErrs.some((e) => e.includes("PASS requires"))) {
    fail("selftest expected PASS-without-proof to fail");
  }
  console.log("OK: validate-results selftest");
  process.exit(0);
}

if (!target) {
  console.error("usage: validate-results.mjs <RESULTS.json> [--pack packs/foo.md]");
  console.error("       validate-results.mjs --selftest");
  process.exit(2);
}

const doc = loadJson(target);
const happy = parsePackHappyPath(packPath);
const errs = validate(doc, happy);
if (errs.length) {
  for (const e of errs) console.error(`FAIL: ${e}`);
  process.exit(1);
}
console.log(`OK: RESULTS valid (${doc.rows.length} rows)`);
