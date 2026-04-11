function json(data, init = {}) {
  return new Response(JSON.stringify(data), {
    ...init,
    headers: {
      "content-type": "application/json; charset=utf-8",
      ...(init.headers || {}),
    },
  });
}

function badRequest(message, status = 400) {
  return json({ error: message }, { status });
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function randomId() {
  const alphabet = "23456789abcdefghjkmnpqrstuvwxyzABCDEFGHJKMNPQRSTUVWXYZ";
  let out = "";
  const bytes = crypto.getRandomValues(new Uint8Array(10));
  for (const byte of bytes) out += alphabet[byte % alphabet.length];
  return out;
}

function scoreRows(scores = {}) {
  const labels = {
    push_load: "压活强度",
    night_ping: "深夜召唤度",
    micro_manage: "微管程度",
    revision_swing: "改稿反复度",
    care_supply: "情绪供给度",
    co_burden: "共担兜底度",
    trust_delegation: "放权信任度",
  };

  return Object.entries(labels)
    .map(([key, label]) => {
      const value = Number(scores[key] ?? 0);
      const width = Math.max(0, Math.min(100, value * 20));
      return `
        <div class="dim-item">
          <div class="dim-item-top">
            <div class="dim-item-name">${escapeHtml(label)}</div>
            <div class="dim-item-score">${escapeHtml(value.toFixed(1))} / 5</div>
          </div>
          <div class="score-bar"><span style="width:${width}%"></span></div>
        </div>
      `;
    })
    .join("\n");
}

function evidenceCards(items = []) {
  return items
    .slice(0, 5)
    .map(
      (item) => `
        <article class="receipt-card">
          <div class="evidence-time">${escapeHtml(item.time_hint || "")}</div>
          <blockquote>${escapeHtml(item.quote || "")}</blockquote>
          <div class="evidence-meta">${escapeHtml(item.source || "")}</div>
          <p>${escapeHtml(item.comment || "")}</p>
        </article>
      `
    )
    .join("\n");
}

function tags(items = []) {
  return items
    .map((tag) => `<span class="tag">${escapeHtml(tag)}</span>`)
    .join("");
}

function renderPage(report) {
  const title = `${report.selected_original_type || ""} + ${report.derived_secondary_type || ""}`;
  const summary = escapeHtml(report.summary || "");
  const analysis = escapeHtml(report.analysis || "").replaceAll("\n", "<br />\n");
  const narrative = escapeHtml(report.narrative || "").replaceAll("\n", "<br />\n");
  const attribution = escapeHtml(
    report.attribution || "友情参考：B站@蛆肉儿串儿、UnluckyNinja/SBTI-test"
  );
  const imageLink = escapeHtml(report.original_image_link || "");

  return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>${escapeHtml(title)}</title>
  <style>
    :root {
      --bg: #f6faf6;
      --panel: #ffffff;
      --text: #1e2a22;
      --muted: #6a786f;
      --line: #dbe8dd;
      --soft: #edf6ef;
      --accent: #6c8d71;
      --accent-strong: #4d6a53;
      --shadow: 0 16px 40px rgba(47, 73, 55, 0.08);
      --radius: 22px;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
      color: var(--text);
      background:
        radial-gradient(circle at top left, #f8fff8 0, #f6faf6 36%, #f2f7f3 100%);
      min-height: 100vh;
    }
    .shell { max-width: 980px; margin: 0 auto; padding: 24px 16px 56px; }
    .card { background: var(--panel); border: 1px solid var(--line); border-radius: var(--radius); box-shadow: var(--shadow); }
    h1, h2, h3, p { margin: 0; }
    .result-wrap { margin-top: 22px; padding: 22px; }
    .result-layout { display: grid; gap: 18px; }
    .result-top { display: grid; grid-template-columns: 0.9fr 1.1fr; gap: 18px; align-items: stretch; }
    .poster-box, .type-box, .analysis-box, .dim-box, .chronicle-box {
      border: 1px solid var(--line);
      border-radius: 18px;
      background: linear-gradient(180deg, #ffffff, #fbfdfb);
      padding: 18px;
    }
    .poster-box {
      display: grid;
      grid-template-rows: 1fr auto;
      min-height: 280px;
      overflow: hidden;
      background:
        radial-gradient(circle at top right, rgba(127,165,134,0.16), rgba(127,165,134,0) 40%),
        linear-gradient(180deg, #ffffff, #f7fbf8);
    }
    .poster-image {
      width: 100%;
      min-height: 220px;
      max-height: 460px;
      object-fit: contain;
      border-radius: 18px;
      background: rgba(255,255,255,0.75);
    }
    .poster-caption { margin-top: 12px; color: var(--muted); font-size: 14px; line-height: 1.8; }
    .type-kicker { font-size: 12px; color: var(--accent-strong); margin-bottom: 8px; letter-spacing: .06em; }
    .type-name { font-size: clamp(30px, 5vw, 48px); line-height: 1.08; letter-spacing: -0.03em; }
    .type-subtitle { margin-top: 10px; color: var(--muted); font-size: 14px; line-height: 1.8; }
    .match {
      margin-top: 18px; display: inline-flex; align-items: center; gap: 8px; padding: 10px 14px;
      border-radius: 999px; background: var(--soft); border: 1px solid var(--line);
      color: var(--accent-strong); font-size: 14px; font-weight: 700;
    }
    .tag-row { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 16px; }
    .tag { display: inline-flex; padding: 8px 12px; border-radius: 999px; background: var(--soft); border: 1px solid var(--line); font-size: 13px; font-weight: 700; }
    .analysis-box h3, .dim-box h3, .chronicle-box h3 { font-size: 16px; margin-bottom: 12px; }
    .analysis-box p { color: #304034; font-size: 15px; line-height: 1.9; white-space: pre-wrap; }
    .dim-list, .receipt-grid { display: grid; gap: 12px; }
    .dim-item, .receipt-card { border: 1px solid var(--line); border-radius: 16px; padding: 14px; background: #fff; }
    .dim-item-top { display: flex; justify-content: space-between; align-items: baseline; gap: 10px; margin-bottom: 10px; flex-wrap: wrap; }
    .dim-item-name { font-size: 14px; font-weight: 700; }
    .dim-item-score { color: var(--accent-strong); font-weight: 800; font-size: 14px; }
    .score-bar { height: 10px; background: #edf3ee; border-radius: 999px; overflow: hidden; }
    .score-bar span { display: block; height: 100%; border-radius: inherit; background: linear-gradient(90deg, #97b59c, #5b7a62); }
    .chronicle-box p { color: #304034; font-size: 14px; line-height: 2; white-space: pre-wrap; }
    .receipt-grid { margin-top: 18px; }
    .evidence-time, .evidence-meta { color: var(--muted); font-size: 12px; }
    blockquote { margin: 10px 0 8px; font-size: 16px; line-height: 1.7; font-weight: 700; }
    .footer-note { color: var(--muted); font-size: 12px; text-align: center; padding-top: 6px; }
    @media (max-width: 560px) { .result-top { grid-template-columns: 1fr; } }
  </style>
</head>
<body>
  <div class="shell">
    <section class="result-wrap card">
      <div class="result-layout">
        <div class="result-top">
          <div class="poster-box">
            <img class="poster-image" src="${imageLink}" alt="${escapeHtml(report.selected_original_type || "")}" />
            <div class="poster-caption">${escapeHtml(report.selected_original_type || "")} 的原人格图保留在这里，我只是在下面追加了我的判词。</div>
          </div>
          <div class="type-box">
            <div class="type-kicker">你的主类型</div>
            <div class="type-name">${escapeHtml(title)}</div>
            <div class="match">匹配度 ${escapeHtml(report.secondary_type_match || "")}%</div>
            <div class="type-subtitle">${summary}</div>
            <div class="tag-row">${tags(report.hidden_tags || [])}</div>
          </div>
        </div>
        <div class="analysis-box">
          <h3>该人格的简单解读</h3>
          <p>${analysis}</p>
        </div>
        <div class="dim-box">
          <h3>主仆关系型七维</h3>
          <div class="dim-list">${scoreRows(report.dimension_scores || {})}</div>
        </div>
        <div class="chronicle-box">
          <h3>Agent 编年史</h3>
          <p>${narrative}</p>
          <div class="receipt-grid">${evidenceCards(report.top_evidence || [])}</div>
        </div>
        <div class="footer-note">${attribution}</div>
      </div>
    </section>
  </div>
</body>
</html>`;
}

function requireAuth(request, env) {
  if (!env.PUBLISH_TOKEN) return null;
  const auth = request.headers.get("authorization") || "";
  const expected = `Bearer ${env.PUBLISH_TOKEN}`;
  if (auth !== expected) return badRequest("Unauthorized", 401);
  return null;
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (request.method === "POST" && url.pathname === "/api/reports") {
      const denied = requireAuth(request, env);
      if (denied) return denied;

      let payload;
      try {
        payload = await request.json();
      } catch {
        return badRequest("Invalid JSON body");
      }
      if (!payload || !payload.selected_original_type || !payload.derived_secondary_type) {
        return badRequest("Missing required report fields");
      }

      const id = randomId();
      const record = {
        ...payload,
        created_at: new Date().toISOString(),
      };
      await env.REPORTS.put(`report:${id}`, JSON.stringify(record));

      const origin = env.SITE_ORIGIN || url.origin;
      return json({
        id,
        url: `${origin.replace(/\/$/, "")}/r/${id}`,
      });
    }

    if (request.method === "GET" && url.pathname.startsWith("/api/reports/")) {
      const id = url.pathname.split("/").pop();
      const raw = id ? await env.REPORTS.get(`report:${id}`) : null;
      if (!raw) return badRequest("Report not found", 404);
      return new Response(raw, {
        headers: { "content-type": "application/json; charset=utf-8" },
      });
    }

    if (request.method === "GET" && url.pathname.startsWith("/r/")) {
      const id = url.pathname.split("/").pop();
      const raw = id ? await env.REPORTS.get(`report:${id}`) : null;
      if (!raw) return badRequest("Report not found", 404);
      const report = JSON.parse(raw);
      return new Response(renderPage(report), {
        headers: { "content-type": "text/html; charset=utf-8" },
      });
    }

    return badRequest("Not found", 404);
  },
};
