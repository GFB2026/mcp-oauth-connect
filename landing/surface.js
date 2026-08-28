const PROOF = "https://mcp.gregfredabytes.com";
const DIAGNOSE = "python skills/mcp-oauth-connect/scripts/diagnose.py";

const HOSTS = {
  claude: {
    label: "Claude Code",
    lines: () => [
      "/plugin marketplace add GFB2026/mcp-oauth-connect",
      "/plugin install mcp-oauth-connect@mcp-oauth-connect",
      "",
      DIAGNOSE + " " + mcpUrl()
    ]
  },
  grok: {
    label: "Grok",
    lines: () => [
      "grok plugin marketplace add GFB2026/mcp-oauth-connect",
      "grok plugin install mcp-oauth-connect --trust",
      "",
      DIAGNOSE + " " + mcpUrl()
    ]
  },
  git: {
    label: "Git",
    lines: () => [
      "git clone https://github.com/GFB2026/mcp-oauth-connect",
      "cd mcp-oauth-connect",
      DIAGNOSE + " " + mcpUrl()
    ]
  }
};

const PROOF_REPORT = {
  url: "https://mcp.gregfredabytes.com",
  mcp_url: "https://mcp.gregfredabytes.com/mcp",
  ok: true,
  warnings: [
    "Origin PRM 404; path-appended form is present. Anthropic also curls /.well-known/oauth-protected-resource"
  ],
  checks: {
    authorization_server_metadata: { ok: true, status: 200 },
    code_challenge_s256: { ok: true },
    protected_resource_metadata: { ok: false, status: 404 },
    protected_resource_metadata_path: { ok: true, status: 200 },
    mcp_no_cross_host_redirect: { ok: true },
    unauthenticated_mcp_get: { ok: true, status: 401 },
    unauthenticated_mcp_post: { ok: true, status: 401 },
    resource_metadata_absolute: { ok: true }
  }
};

function mcpUrl() {
  const el = document.getElementById("mcp-url");
  const raw = (el && el.value ? el.value : PROOF).trim();
  try {
    const u = new URL(raw);
    if (u.protocol === "https:") return u.origin + (u.pathname === "/" ? "" : u.pathname.replace(/\/$/, ""));
  } catch (_err) {
    /* keep proof origin */
  }
  return PROOF;
}

function selectedHost() {
  const on = document.querySelector(".hosts button[aria-selected='true']");
  return (on && on.getAttribute("data-host")) || "claude";
}

function renderInstall() {
  const pre = document.getElementById("install-cmd");
  const host = HOSTS[selectedHost()];
  if (!pre || !host) return;
  pre.textContent = host.lines().join("\n");
}

function formatReport(report, liveNote) {
  const lines = [];
  if (liveNote) lines.push(liveNote, "");
  lines.push("url  " + (report.url || ""));
  if (report.mcp_url) lines.push("mcp  " + report.mcp_url);
  const checks = report.checks || {};
  Object.keys(checks).forEach(function (name) {
    const c = checks[name] || {};
    const mark = c.ok ? "ok  " : "fail";
    const extra = c.status != null ? "  " + c.status : "";
    lines.push(mark + "  " + name + extra);
  });
  (report.warnings || []).forEach(function (w) {
    lines.push("warn " + w);
  });
  lines.push(report.ok ? "exit 0" : "exit 1");
  return lines.join("\n");
}

function showProofFixture() {
  const pre = document.getElementById("demo-out");
  if (!pre) return;
  pre.textContent = formatReport(
    PROOF_REPORT,
    "diagnose.py " + PROOF + "  (captured; GET/POST /mcp is CORS-blocked in the browser)"
  );
}

async function probeProof() {
  const pre = document.getElementById("demo-out");
  const btn = document.getElementById("probe");
  if (!pre) return;
  if (btn) btn.disabled = true;
  pre.textContent = "probing " + PROOF + " …";
  const paths = [
    "/.well-known/oauth-authorization-server",
    "/.well-known/oauth-protected-resource/mcp"
  ];
  const lines = ["live discovery  " + PROOF, "browser cannot read WWW-Authenticate on 401 — that is diagnose.py", ""];
  try {
    for (let i = 0; i < paths.length; i++) {
      const path = paths[i];
      const res = await fetch(PROOF + path, { headers: { Accept: "application/json" } });
      let body = {};
      try {
        body = await res.json();
      } catch (_err) {
        body = {};
      }
      if (path.indexOf("authorization-server") !== -1) {
        const methods = body.code_challenge_methods_supported || [];
        const s256 = methods.indexOf("S256") !== -1;
        lines.push((res.ok && body.issuer ? "ok  " : "fail") + "  " + path + "  " + res.status);
        if (body.issuer) lines.push("     issuer " + body.issuer);
        if (body.registration_endpoint) lines.push("     register " + body.registration_endpoint);
        lines.push("     S256 " + (s256 ? "yes" : "no"));
      } else {
        lines.push((res.ok && body.resource ? "ok  " : "fail") + "  " + path + "  " + res.status);
        if (body.resource) lines.push("     resource " + body.resource);
      }
    }
    lines.push("");
    lines.push("full checklist is " + DIAGNOSE + " " + PROOF);
    pre.textContent = lines.join("\n");
  } catch (err) {
    pre.textContent = "probe failed: " + (err && err.message ? err.message : String(err)) + "\n\n" + formatReport(PROOF_REPORT, "fixture");
  }
  if (btn) btn.disabled = false;
}

async function copyInstall() {
  const pre = document.getElementById("install-cmd");
  const btn = document.getElementById("copy-install");
  if (!pre) return;
  try {
    await navigator.clipboard.writeText(pre.textContent || "");
    if (btn) {
      const prev = btn.textContent;
      btn.textContent = "Copied";
      setTimeout(function () {
        btn.textContent = prev;
      }, 1200);
    }
  } catch (_err) {
    if (btn) btn.textContent = "Select the block";
  }
}

(function bind() {
  const tabs = document.querySelectorAll(".hosts button[data-host]");
  tabs.forEach(function (btn) {
    btn.addEventListener("click", function () {
      tabs.forEach(function (t) {
        t.setAttribute("aria-selected", t === btn ? "true" : "false");
      });
      renderInstall();
    });
  });
  const url = document.getElementById("mcp-url");
  if (url) url.addEventListener("input", renderInstall);
  const copy = document.getElementById("copy-install");
  if (copy) copy.addEventListener("click", copyInstall);
  const probe = document.getElementById("probe");
  if (probe) probe.addEventListener("click", probeProof);
  renderInstall();
  showProofFixture();
})();
