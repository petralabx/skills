#!/usr/bin/env node
/**
 * Resolve-then-record proof for https://staging.plxcustomer.io.
 * Fail closed on wrong host, missing Vercel creds, or optional pin mismatch.
 */
import { writeFileSync } from "node:fs";

const CANONICAL_HOST = "staging.plxcustomer.io";
const CANONICAL_ORIGIN = `https://${CANONICAL_HOST}`;
const FULL_SHA = /^[0-9a-f]{40}$/;
const DPL = /^dpl_[A-Za-z0-9]+$/;

function arg(name, fallbackEnv) {
  const idx = process.argv.indexOf(name);
  if (idx >= 0 && process.argv[idx + 1]) return process.argv[idx + 1];
  return process.env[fallbackEnv] || "";
}

function fail(code, message) {
  const out = { ok: false, code, message, host: CANONICAL_ORIGIN };
  console.error(JSON.stringify(out));
  process.exit(1);
}

function addScope(url, scope) {
  if (!scope) return;
  if (scope.startsWith("team_")) url.searchParams.set("teamId", scope);
  else url.searchParams.set("slug", scope);
}

async function fetchJson(url, token) {
  let response;
  try {
    response = await fetch(url.toString(), {
      headers: { Accept: "application/json", Authorization: `Bearer ${token}` },
    });
  } catch {
    return { ok: false, status: 0, body: null };
  }
  const text = await response.text();
  let body = null;
  try {
    body = JSON.parse(text);
  } catch {
    body = null;
  }
  return { ok: response.ok, status: response.status, body };
}

const token = process.env.VERCEL_TOKEN || "";
const scope = process.env.VERCEL_SCOPE || process.env.VERCEL_TEAM_ID || "";
const project = process.env.VERCEL_PROJECT || process.env.VERCEL_PROJECT_ID || "";
const requireSha = arg("--require-sha", "REQUIRE_SHA");
const requireDpl = arg("--require-dpl", "REQUIRE_DPL");
const outPath = arg("--out", "DEPLOY_PROOF_OUT");

if (!token.trim()) fail("MISSING_VERCEL_TOKEN", "VERCEL_TOKEN is required");

const aliasUrl = new URL(
  `https://api.vercel.com/v4/aliases/${encodeURIComponent(CANONICAL_HOST)}`,
);
if (project) aliasUrl.searchParams.set("projectId", project);
addScope(aliasUrl, scope);

const alias = await fetchJson(aliasUrl, token);
if (!alias.ok || !alias.body) {
  fail("ALIAS_LOOKUP_FAILED", `Vercel alias lookup failed (${alias.status})`);
}

const deploymentId =
  alias.body.deploymentId || alias.body.deployment?.id || alias.body.uid || "";
if (!DPL.test(deploymentId)) {
  fail("ALIAS_MISSING_DPL", "Alias response had no dpl_ deployment id");
}

const depUrl = new URL(`https://api.vercel.com/v13/deployments/${deploymentId}`);
addScope(depUrl, scope);
const dep = await fetchJson(depUrl, token);
if (!dep.ok || !dep.body) {
  fail("DEPLOYMENT_LOOKUP_FAILED", `Deployment lookup failed (${dep.status})`);
}

const sha =
  dep.body.gitSource?.sha ||
  dep.body.meta?.githubCommitSha ||
  dep.body.meta?.gitlabCommitSha ||
  "";
if (!FULL_SHA.test(sha)) {
  fail("DEPLOYMENT_MISSING_SHA", "Deployment record had no 40-char git SHA");
}

const aliases = []
  .concat(dep.body.aliases || [])
  .concat(dep.body.alias || [])
  .map((a) => String(a).replace(/^https?:\/\//, ""));
if (aliases.length && !aliases.includes(CANONICAL_HOST)) {
  fail(
    "CANONICAL_ALIAS_MISMATCH",
    "Deployment is not aliased to staging.plxcustomer.io",
  );
}

if (requireSha && requireSha !== sha) {
  fail("SHA_PIN_MISMATCH", "Live alias SHA does not match --require-sha");
}
if (requireDpl && requireDpl !== deploymentId) {
  fail("DPL_PIN_MISMATCH", "Live alias dpl does not match --require-dpl");
}

const proof = {
  ok: true,
  host: CANONICAL_ORIGIN,
  sha,
  deploymentId,
  aliasCheckedAt: new Date().toISOString(),
};
console.log(JSON.stringify(proof, null, 2));
if (outPath) writeFileSync(outPath, `${JSON.stringify(proof, null, 2)}\n`, "utf8");
