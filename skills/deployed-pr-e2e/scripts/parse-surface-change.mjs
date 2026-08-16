#!/usr/bin/env node
/**
 * Parse a portal PR Surface-change stamp for deployed-pr-e2e.
 * Does not guess. Missing stamp on --pr exits 2.
 */
import { readFileSync, existsSync, writeFileSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const VIEWPORTS = ["desktop", "tablet", "mobile"];
const VIEWPORT_IDS = {
  desktop: "UX-VP-desktop",
  tablet: "UX-VP-tablet",
  mobile: "UX-VP-mobile",
};

export function parseSurfaceChangeBody(text, labels = []) {
  const raw = String(text || "");
  const labelHit = (labels || []).some((l) => {
    const name = typeof l === "string" ? l : l?.name;
    return String(name || "").toLowerCase() === "surface-change";
  });
  const changeLine = raw.match(/^\s*(?:-\s*)?Surface-change:\s*(yes|no)\s*$/im);
  const surfacesLine = raw.match(/^\s*(?:-\s*)?Surfaces:\s*(.+?)\s*$/im);
  const viewportsLine = raw.match(/^\s*(?:-\s*)?Viewports:\s*(.+?)\s*$/im);

  const missing = !changeLine && !labelHit;
  let declared = false;
  if (changeLine) declared = changeLine[1].toLowerCase() === "yes";
  else if (labelHit) declared = true;

  const surfaces = [];
  if (surfacesLine) {
    for (const part of surfacesLine[1].split(",")) {
      const route = part.trim();
      if (route.startsWith("/")) surfaces.push(route);
    }
  }

  const viewports = [];
  if (viewportsLine) {
    for (const part of viewportsLine[1].split(",")) {
      const name = part.trim().toLowerCase();
      if (VIEWPORTS.includes(name)) viewports.push(name);
    }
  }
  const requiredViewports = viewports.length ? viewports : declared ? [...VIEWPORTS] : [];

  return {
    declared,
    missing,
    source: changeLine ? "pr-body" : labelHit ? "label" : "none",
    surfaces,
    viewports: requiredViewports,
    requiredRowIds: requiredViewports.map((v) => VIEWPORT_IDS[v]),
  };
}

export function requiredViewportRows(surfaceChange) {
  if (!surfaceChange || !surfaceChange.declared) return [];
  const ids = surfaceChange.requiredRowIds || [];
  return ids.length ? ids : VIEWPORTS.map((v) => VIEWPORT_IDS[v]);
}

const API_ROW_IDS = ["API-AUTH", "API-CONTRACT", "API-ERROR"];
const SECURITY_ROW_IDS = [
  "SEC-HOST",
  "SEC-AUTHN",
  "SEC-AUTHZ",
  "SEC-SECRETS",
  "SEC-ISOLATION",
];

function parseYesNo(raw, key, labelName, labels) {
  const re = new RegExp(`^\\s*(?:-\\s*)?${key}:\\s*(yes|no)\\s*$`, "im");
  const line = raw.match(re);
  const labelHit = (labels || []).some((l) => {
    const name = typeof l === "string" ? l : l?.name;
    return String(name || "").toLowerCase() === labelName;
  });
  if (line) {
    return { declared: line[1].toLowerCase() === "yes", missing: false, source: "pr-body" };
  }
  if (labelHit) return { declared: true, missing: false, source: "label" };
  return { declared: false, missing: true, source: "none" };
}

function parsePathList(raw, key) {
  const re = new RegExp(`^\\s*(?:-\\s*)?${key}:\\s*(.+?)\\s*$`, "im");
  const line = raw.match(re);
  const paths = [];
  if (!line) return paths;
  for (const part of line[1].split(",")) {
    const route = part.trim();
    if (route.startsWith("/")) paths.push(route);
  }
  return paths;
}

export function parseApiChangeBody(text, labels = []) {
  const raw = String(text || "");
  const yn = parseYesNo(raw, "Api-change", "api-change", labels);
  const apis = parsePathList(raw, "APIs");
  return {
    declared: yn.declared,
    missing: yn.missing,
    source: yn.source,
    apis,
    requiredRowIds: yn.declared ? [...API_ROW_IDS] : [],
  };
}

export function parseSecurityChangeBody(text, labels = []) {
  const raw = String(text || "");
  const yn = parseYesNo(raw, "Security-change", "security-change", labels);
  return {
    declared: yn.declared,
    missing: yn.missing,
    source: yn.source,
    requiredRowIds: yn.declared ? [...SECURITY_ROW_IDS] : [],
  };
}

export function requiredApiRows(apiChange) {
  if (!apiChange || !apiChange.declared) return [];
  return apiChange.requiredRowIds || [...API_ROW_IDS];
}

export function requiredSecurityRows(securityChange) {
  if (!securityChange || !securityChange.declared) return [];
  return securityChange.requiredRowIds || [...SECURITY_ROW_IDS];
}

export function parseHarnessStamps(text, labels = []) {
  return {
    surfaceChange: parseSurfaceChangeBody(text, labels),
    apiChange: parseApiChangeBody(text, labels),
    securityChange: parseSecurityChangeBody(text, labels),
  };
}

function parseArgs(argv) {
  const out = { pr: "", bodyFile: "", write: "", selftest: false };
  for (let i = 2; i < argv.length; i += 1) {
    const a = argv[i];
    if (a === "--selftest") out.selftest = true;
    else if (a === "--pr") out.pr = argv[++i] || "";
    else if (a === "--body-file") out.bodyFile = argv[++i] || "";
    else if (a === "--write") out.write = argv[++i] || "";
  }
  return out;
}

function selftest() {
  const yes = parseSurfaceChangeBody(
    "## Surface change\n- Surface-change: yes\n- Surfaces: /mrp/project-development, /admin/knowledge\n- Viewports: desktop, mobile\n",
  );
  if (!yes.declared || yes.missing) throw new Error("yes stamp should declare");
  if (yes.surfaces.length !== 2) throw new Error("expected two surfaces");
  if (yes.viewports.join(",") !== "desktop,mobile") throw new Error("viewport parse");
  if (yes.requiredRowIds.join(",") !== "UX-VP-desktop,UX-VP-mobile") {
    throw new Error("row ids");
  }
  const no = parseSurfaceChangeBody("- Surface-change: no\n");
  if (no.declared || no.missing) throw new Error("no stamp");
  const missing = parseSurfaceChangeBody("## Summary\nhello\n");
  if (!missing.missing || missing.declared) throw new Error("missing stamp");
  const labeled = parseSurfaceChangeBody("## Summary\n", ["surface-change"]);
  if (!labeled.declared || labeled.missing) throw new Error("label should declare");
  const apiYes = parseApiChangeBody(
    "- Api-change: yes\n- APIs: /api/agents/chief-of-staff/chat, /api/admin/knowledge/articles\n",
  );
  if (!apiYes.declared || apiYes.apis.length !== 2) throw new Error("api stamp");
  if (apiYes.requiredRowIds.join(",") !== API_ROW_IDS.join(",")) throw new Error("api rows");
  const apiAbsent = parseApiChangeBody("## Summary\n");
  if (apiAbsent.declared || !apiAbsent.missing) throw new Error("api absent");
  const secYes = parseSecurityChangeBody("- Security-change: yes\n");
  if (!secYes.declared || secYes.requiredRowIds.length !== 5) throw new Error("sec stamp");
  console.log("OK: parse-surface-change selftest");
}

function fetchPr(pr) {
  const repo = process.env.MC_REPO || "petralabx/plx-customer-portal";
  const raw = execFileSync(
    "gh",
    ["pr", "view", String(pr), "--repo", repo, "--json", "body,labels,url,number"],
    { encoding: "utf8" },
  );
  return JSON.parse(raw);
}

const isMain =
  Boolean(process.argv[1]) &&
  fileURLToPath(import.meta.url).toLowerCase() === String(process.argv[1]).toLowerCase();
if (isMain) {
  const args = parseArgs(process.argv);
  if (args.selftest) {
    try {
      selftest();
      process.exit(0);
    } catch (err) {
      console.error(`FAIL: ${err.message}`);
      process.exit(1);
    }
  }

  let body = "";
  let labels = [];
  let pr = args.pr || null;
  let url = "";
  if (args.bodyFile) {
    if (!existsSync(args.bodyFile)) {
      console.error(`FAIL: missing body file ${args.bodyFile}`);
      process.exit(2);
    }
    body = readFileSync(args.bodyFile, "utf8");
  } else if (args.pr) {
    try {
      const data = fetchPr(args.pr);
      body = data.body || "";
      labels = data.labels || [];
      pr = data.number || args.pr;
      url = data.url || "";
    } catch (err) {
      console.error(`FAIL: cannot read PR ${args.pr}: ${err.message}`);
      process.exit(2);
    }
  } else {
    console.error("usage: parse-surface-change.mjs --pr <n> | --body-file <path> [--write out.json]");
    console.error("       parse-surface-change.mjs --selftest");
    process.exit(2);
  }

  const parsed = parseHarnessStamps(body, labels);
  const out = { ...parsed, pr, url };
  if (args.write) writeFileSync(args.write, `${JSON.stringify(out, null, 2)}\n`);
  console.log(JSON.stringify(out, null, 2));
  if (args.pr && parsed.surfaceChange.missing) {
    console.error("STOP: named PR has no Surface-change stamp. Ask the operator to add it.");
    process.exit(2);
  }
}
