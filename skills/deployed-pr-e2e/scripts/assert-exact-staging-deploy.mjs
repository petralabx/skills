#!/usr/bin/env node
/**
 * Resolve-then-record proof for https://staging.plxcustomer.io.
 * Reads the live alias first (HTML data-dpl-id + persona-qa SHA).
 * Optionally cross-checks Vercel when VERCEL_TOKEN is set.
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
      headers: {
        Accept: "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
    });
  } catch {
    return { ok: false, status: 0, body: null, text: "" };
  }
  const text = await response.text();
  let body = null;
  try {
    body = JSON.parse(text);
  } catch {
    body = null;
  }
  return { ok: response.ok, status: response.status, body, text };
}

async function resolveFromLiveAlias() {
  const page = await fetch(CANONICAL_ORIGIN, { redirect: "follow" });
  const html = await page.text();
  const finalHost = new URL(page.url).host;
  if (finalHost !== CANONICAL_HOST) {
    fail("WRONG_HOST", `Live fetch resolved to ${finalHost}`);
  }
  const dplMatch = html.match(/data-dpl-id="(dpl_[A-Za-z0-9]+)"/)
    || html.match(/[?&]dpl=(dpl_[A-Za-z0-9]+)/);
  const deploymentId = dplMatch?.[1] || "";
  const diag = await fetchJson(
    `${CANONICAL_ORIGIN}/api/internal/persona-qa/deployment-diagnostics`,
  );
  const sha = diag.body?.expectedSha || "";
  return {
    source: "live-alias",
    status: page.status,
    deploymentId,
    sha,
    diagStatus: diag.status,
  };
}

async function resolveFromVercel(token) {
  const scope = process.env.VERCEL_SCOPE || process.env.VERCEL_TEAM_ID || "";
  const project = process.env.VERCEL_PROJECT || process.env.VERCEL_PROJECT_ID || "";
  const aliasUrl = new URL(
    `https://api.vercel.com/v4/aliases/${encodeURIComponent(CANONICAL_HOST)}`,
  );
  if (project) aliasUrl.searchParams.set("projectId", project);
  addScope(aliasUrl, scope);
  const alias = await fetchJson(aliasUrl, token);
  if (!alias.ok || !alias.body) {
    return { ok: false, reason: `Vercel alias lookup failed (${alias.status})` };
  }
  const deploymentId =
    alias.body.deploymentId || alias.body.deployment?.id || alias.body.uid || "";
  const depUrl = new URL(`https://api.vercel.com/v13/deployments/${deploymentId}`);
  addScope(depUrl, scope);
  const dep = await fetchJson(depUrl, token);
  if (!dep.ok || !dep.body) {
    return { ok: false, reason: `Deployment lookup failed (${dep.status})` };
  }
  const sha =
    dep.body.gitSource?.sha ||
    dep.body.meta?.githubCommitSha ||
    dep.body.meta?.gitlabCommitSha ||
    "";
  const aliases = []
    .concat(dep.body.aliases || [])
    .concat(dep.body.alias || [])
    .map((a) => String(a).replace(/^https?:\/\//, ""));
  if (aliases.length && !aliases.includes(CANONICAL_HOST)) {
    return { ok: false, reason: "Deployment is not aliased to staging.plxcustomer.io" };
  }
  return { ok: true, deploymentId, sha, source: "vercel-api" };
}

const token = process.env.VERCEL_TOKEN || "";
const requireSha = arg("--require-sha", "REQUIRE_SHA");
const requireDpl = arg("--require-dpl", "REQUIRE_DPL");
const outPath = arg("--out", "DEPLOY_PROOF_OUT");

const live = await resolveFromLiveAlias();
let deploymentId = live.deploymentId;
let sha = live.sha;
let source = live.source;

if (token.trim()) {
  const vercel = await resolveFromVercel(token);
  if (!vercel.ok) fail("VERCEL_CROSSCHECK_FAILED", vercel.reason);
  if (deploymentId && vercel.deploymentId !== deploymentId) {
    fail("DPL_SOURCE_MISMATCH", "Live HTML dpl does not match Vercel alias dpl");
  }
  if (sha && vercel.sha !== sha) {
    fail("SHA_SOURCE_MISMATCH", "Live diagnostics SHA does not match Vercel deployment SHA");
  }
  deploymentId = vercel.deploymentId;
  sha = vercel.sha;
  source = "live-alias+vercel-api";
}

if (!DPL.test(deploymentId)) {
  fail("ALIAS_MISSING_DPL", "Live alias HTML had no data-dpl-id");
}
if (!FULL_SHA.test(sha)) {
  fail("DEPLOYMENT_MISSING_SHA", "Live diagnostics had no 40-char git SHA");
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
  source,
  aliasCheckedAt: new Date().toISOString(),
};
console.log(JSON.stringify(proof, null, 2));
if (outPath) writeFileSync(outPath, `${JSON.stringify(proof, null, 2)}\n`, "utf8");
