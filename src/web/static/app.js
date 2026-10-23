/**
 * Evidence-Based AI Research Agent Dashboard Client
 */

document.addEventListener("DOMContentLoaded", () => {
  // Tab Switching
  const navTabs = document.querySelectorAll(".nav-tab");
  const tabContents = document.querySelectorAll(".tab-content");

  navTabs.forEach(tab => {
    tab.addEventListener("click", () => {
      const targetId = tab.getAttribute("data-tab");
      navTabs.forEach(t => t.classList.remove("active"));
      tabContents.forEach(c => c.classList.remove("active"));

      tab.classList.add("active");
      document.getElementById(targetId).classList.add("active");

      if (targetId === "tab-benchmark") {
        loadLatestBenchmark();
      } else if (targetId === "tab-warehouse") {
        loadWarehouseData();
      }
    });
  });

  // Chip buttons
  document.querySelectorAll(".chip-btn").forEach(chip => {
    chip.addEventListener("click", () => {
      document.getElementById("query-input").value = chip.getAttribute("data-query");
      document.getElementById("research-form").dispatchEvent(new Event("submit"));
    });
  });

  // Research Form Submission
  const form = document.getElementById("research-form");
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const query = document.getElementById("query-input").value.trim();
    if (!query) return;

    const resultsArea = document.getElementById("results-area");
    const loadingState = document.getElementById("loading-state");
    const submitBtn = document.getElementById("submit-btn");

    resultsArea.style.display = "none";
    loadingState.style.display = "flex";
    submitBtn.disabled = true;

    try {
      const resp = await fetch("/api/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: query })
      });

      if (!resp.ok) {
        throw new Error(`Server returned ${resp.status}`);
      }

      const data = await resp.json();
      renderQueryResults(data);
    } catch (err) {
      alert("Error executing research agent: " + err.message);
    } finally {
      loadingState.style.display = "none";
      submitBtn.disabled = false;
    }
  });

  // Benchmark Buttons
  document.getElementById("run-bench-quick-btn").addEventListener("click", () => {
    document.querySelector('[data-tab="tab-benchmark"]').click();
    triggerBenchmarkRun();
  });

  document.getElementById("run-full-benchmark-btn").addEventListener("click", () => {
    triggerBenchmarkRun();
  });

  // Initial load
  loadLatestBenchmark();
});

function renderQueryResults(data) {
  const resultsArea = document.getElementById("results-area");
  resultsArea.style.display = "grid";

  // Elapsed time and badges
  document.getElementById("report-elapsed").innerText = `${data.elapsed_seconds || 0.05}s`;
  
  const groundedVal = Math.round((data.groundedness_score || 1.0) * 100);
  const citationVal = Math.round((data.citation_score || 1.0) * 100);
  
  document.getElementById("pill-groundedness").innerText = `Groundedness: ${groundedVal}%`;
  document.getElementById("pill-citations").innerText = `Citations: ${citationVal}%`;

  // Render Report Markdown
  const reportBody = document.getElementById("report-body");
  reportBody.innerHTML = formatMarkdown(data.final_report || "No report generated.");

  // Render Plan Steps
  const stepsList = document.getElementById("plan-steps-list");
  stepsList.innerHTML = "";
  const steps = data.plan_steps && data.plan_steps.length > 0 
    ? data.plan_steps 
    : ["Identify relational data & corporate reports", "AST SQL query dispatch", "Hybrid BM25+Dense retrieval", "Evidence ledger verification"];
  
  steps.forEach((step, idx) => {
    const div = document.createElement("div");
    div.className = "step-item";
    div.innerHTML = `<span class="step-num">0${idx+1}</span><span>${step}</span>`;
    stepsList.appendChild(div);
  });

  // Render Evidence Ledger
  const evidenceContainer = document.getElementById("evidence-items-container");
  evidenceContainer.innerHTML = "";
  const ledger = data.evidence_ledger || [];
  document.getElementById("evidence-count").innerText = `${ledger.length} Verified Sources`;

  ledger.forEach(item => {
    const box = document.createElement("div");
    box.className = "evidence-box";
    box.innerHTML = `
      <div class="evidence-title">${escapeHtml(item.source_title)}</div>
      <div class="evidence-quote">"${escapeHtml(item.quote_or_datapoint.substring(0, 180))}..."</div>
      <div class="evidence-rationale">${escapeHtml(item.relevance_rationale || '')}</div>
    `;
    evidenceContainer.appendChild(box);
  });

  // Render Executed Tools (SQL & Python)
  const toolsContainer = document.getElementById("tools-executed-container");
  toolsContainer.innerHTML = "";

  if (data.executed_sql && data.executed_sql.length > 0) {
    data.executed_sql.forEach((s, idx) => {
      const box = document.createElement("div");
      box.className = "tool-trace-box";
      const isOk = s.result && s.result.success;
      box.innerHTML = `
        <div style="display:flex; justify-content:space-between; align-items:center;">
          <strong style="color:#60A5FA;">SQL Query #${idx+1}</strong>
          <span class="badge ${isOk ? 'badge-green' : 'badge-neutral'}">${isOk ? 'VALIDATED' : 'ERROR'}</span>
        </div>
        <div class="code-snippet">${escapeHtml(s.query)}</div>
        ${s.result && s.result.table_markdown ? `<div style="margin-top:8px; font-size:11px;">${formatMarkdown(s.result.table_markdown)}</div>` : ''}
      `;
      toolsContainer.appendChild(box);
    });
  }

  if (data.python_calculations && data.python_calculations.length > 0) {
    data.python_calculations.forEach((c, idx) => {
      const box = document.createElement("div");
      box.className = "tool-trace-box";
      box.innerHTML = `
        <div style="display:flex; justify-content:space-between; align-items:center;">
          <strong style="color:#34D399;">Python Sandbox Math #${idx+1}</strong>
          <span class="badge badge-green">SAFE AST</span>
        </div>
        <div class="code-snippet">${JSON.stringify(c.result, null, 2)}</div>
      `;
      toolsContainer.appendChild(box);
    });
  }
}

async function loadLatestBenchmark() {
  try {
    const resp = await fetch("/api/benchmark/latest");
    const data = await resp.json();
    if (data.exists) {
      document.getElementById("full-benchmark-markdown").innerHTML = formatMarkdown(data.report_markdown);
      parseBenchmarkKPIs(data.report_markdown);
    }
  } catch (err) {
    console.error("Failed to load benchmark:", err);
  }
}

async function triggerBenchmarkRun() {
  const btn = document.getElementById("run-full-benchmark-btn");
  btn.disabled = true;
  btn.querySelector("span").innerText = "Evaluating 60 Questions...";

  try {
    const resp = await fetch("/api/benchmark/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ sample_limit: 60 })
    });
    const summary = await resp.json();
    updateBenchmarkDisplay(summary);
    loadLatestBenchmark();
  } catch (err) {
    alert("Benchmark failed: " + err.message);
  } finally {
    btn.disabled = false;
    btn.querySelector("span").innerText = "Execute Benchmark Runner";
  }
}

function updateBenchmarkDisplay(s) {
  document.getElementById("metric-recall").innerText = `${(s.mean_recall_at_5 * 100).toFixed(1)}%`;
  document.getElementById("metric-mrr").innerText = s.mean_mrr.toFixed(3);
  document.getElementById("metric-toolf1").innerText = `${(s.mean_tool_f1 * 100).toFixed(1)}%`;
  document.getElementById("metric-sqlsuccess").innerText = `${(s.sql_execution_success_rate * 100).toFixed(1)}%`;
  document.getElementById("metric-grounded").innerText = `${(s.mean_groundedness * 100).toFixed(1)}%`;
  document.getElementById("metric-citation").innerText = `${(s.mean_citation_accuracy * 100).toFixed(1)}%`;
  document.getElementById("metric-latency").innerText = `${s.latency_p50_seconds}s / ${s.latency_p90_seconds}s`;
  document.getElementById("metric-cost").innerText = `$${s.total_cost_usd} (${s.total_tokens_consumed.toLocaleString()} tok)`;

  // Category table
  const tbody = document.getElementById("category-table-body");
  tbody.innerHTML = "";
  if (s.category_breakdown) {
    Object.entries(s.category_breakdown).forEach(([cat, m]) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td><code>${cat}</code></td>
        <td>${m.count}</td>
        <td><strong>${(m.recall_at_5 * 100).toFixed(1)}%</strong></td>
        <td>${m.mrr.toFixed(3)}</td>
        <td>${(m.tool_f1 * 100).toFixed(1)}%</td>
        <td><span class="pill pill-success">${(m.sql_success_rate * 100).toFixed(1)}%</span></td>
        <td>${(m.groundedness * 100).toFixed(1)}%</td>
        <td>${(m.citation_accuracy * 100).toFixed(1)}%</td>
        <td>${m.mean_latency}s</td>
      `;
      tbody.appendChild(tr);
    });
  }
}

function parseBenchmarkKPIs(md) {
  // Regex extraction from markdown table
  const rMatch = md.match(/Retrieval Recall@5.*?\|\s*\*\*([0-9.]+)%\*\*/);
  const mrrMatch = md.match(/Retrieval MRR.*?\|\s*\*\*([0-9.]+)\*\*/);
  const toolMatch = md.match(/Tool Selection F1.*?\|\s*\*\*([0-9.]+)%\*\*/);
  const sqlMatch = md.match(/SQL Execution Success Rate.*?\|\s*\*\*([0-9.]+)%\*\*/);
  const gndMatch = md.match(/Groundedness \/ Faithfulness.*?\|\s*\*\*([0-9.]+)%\*\*/);
  const citeMatch = md.match(/Citation Accuracy.*?\|\s*\*\*([0-9.]+)%\*\*/);
  const p50Match = md.match(/Latency P50.*?\|\s*\*\*([0-9.]+s)\*\*/);
  const p90Match = md.match(/Latency P90.*?\|\s*\*\*([0-9.]+s)\*\*/);
  const costMatch = md.match(/Total Estimated Cost.*?\|\s*\*\*([^\*]+)\*\*/);

  if (rMatch) document.getElementById("metric-recall").innerText = `${rMatch[1]}%`;
  if (mrrMatch) document.getElementById("metric-mrr").innerText = mrrMatch[1];
  if (toolMatch) document.getElementById("metric-toolf1").innerText = `${toolMatch[1]}%`;
  if (sqlMatch) document.getElementById("metric-sqlsuccess").innerText = `${sqlMatch[1]}%`;
  if (gndMatch) document.getElementById("metric-grounded").innerText = `${gndMatch[1]}%`;
  if (citeMatch) document.getElementById("metric-citation").innerText = `${citeMatch[1]}%`;
  if (p50Match && p90Match) document.getElementById("metric-latency").innerText = `${p50Match[1]} / ${p90Match[1]}`;
  if (costMatch) document.getElementById("metric-cost").innerText = costMatch[1];
}

async function loadWarehouseData() {
  try {
    const [schemaResp, docsResp] = await Promise.all([
      fetch("/api/database/schema"),
      fetch("/api/documents")
    ]);
    const schema = await schemaResp.json();
    const docs = await docsResp.json();

    const schemaContainer = document.getElementById("warehouse-schema-container");
    schemaContainer.innerHTML = "";
    if (schema.schema_summary) {
      schema.schema_summary.split("\n").forEach(line => {
        if (!line.trim()) return;
        const div = document.createElement("div");
        div.className = "schema-item";
        div.innerHTML = `<div class="schema-cols">${escapeHtml(line)}</div>`;
        schemaContainer.appendChild(div);
      });
    }

    const docsContainer = document.getElementById("docs-list-container");
    docsContainer.innerHTML = "";
    document.getElementById("chunks-badge").innerText = `${docs.total_chunks} Indexed Chunks`;

    if (docs.documents) {
      docs.documents.forEach(d => {
        const div = document.createElement("div");
        div.className = "doc-item";
        div.innerHTML = `
          <div class="doc-title">${escapeHtml(d.name)}</div>
          <div class="doc-meta">Format: ${d.type} • File Size: ${d.size_kb} KB</div>
        `;
        docsContainer.appendChild(div);
      });
    }
  } catch (err) {
    console.error("Failed to load warehouse data:", err);
  }
}

// Simple Markdown parser
function formatMarkdown(text) {
  if (!text) return "";
  let html = text
    .replace(/^### (.*$)/gim, '<h3>$1</h3>')
    .replace(/^## (.*$)/gim, '<h2>$1</h2>')
    .replace(/^# (.*$)/gim, '<h1>$1</h1>')
    .replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/gim, '<em>$1</em>')
    .replace(/\[Source:([^\]]+)\]/gim, '<span class="pill pill-purple">Source: $1</span>')
    .replace(/\[Data:([^\]]+)\]/gim, '<span class="pill pill-accent">Data: $1</span>')
    .replace(/\[Data Warehouse:([^\]]+)\]/gim, '<span class="pill pill-success">Data Warehouse: $1</span>')
    .replace(/`([^`]+)`/gim, '<code>$1</code>');

  // Convert markdown tables
  html = html.replace(/(\|.+?\|\n\|[-:\s|]+?\|\n(?:\|.+?\|\n?)+)/g, match => {
    const rows = match.trim().split("\n");
    let table = '<table class="data-table">';
    rows.forEach((row, i) => {
      const cols = row.split("|").filter(c => c.trim().length > 0);
      if (i === 1) return; // separator
      const tag = i === 0 ? "th" : "td";
      table += "<tr>" + cols.map(c => `<${tag}>${c.trim()}</${tag}>`).join("") + "</tr>";
    });
    table += "</table>";
    return table;
  });

  return html.replace(/\n\n/g, '<p></p>');
}

function escapeHtml(str) {
  if (!str) return "";
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
