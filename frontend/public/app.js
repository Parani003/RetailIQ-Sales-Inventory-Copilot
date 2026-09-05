/* RetailIQ Copilot Interactive Frontend Script */

let currentRules = {};

document.addEventListener('DOMContentLoaded', () => {
    lucide.createIcons();
    fetchRules();
    loadDashboard();
});

// TAB SWITCHING
function switchTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
    document.querySelectorAll('.nav-btn').forEach(el => el.classList.remove('active'));

    const targetTab = document.getElementById(`tab-${tabId}`);
    const targetNav = document.getElementById(`nav-${tabId}`);

    if (targetTab) targetTab.classList.remove('hidden');
    if (targetNav) targetNav.classList.add('active');

    // Trigger tab-specific loaders
    if (tabId === 'dashboard') loadDashboard();
    else if (tabId === 'inventory') loadInventoryTable();
    else if (tabId === 'anomalies') loadAnomalies();
    else if (tabId === 'stores') loadStoreComparison();
    else if (tabId === 'products') loadProductsTable();

    setTimeout(() => lucide.createIcons(), 50);
}

// FETCH & EDIT RULES
async function fetchRules() {
    try {
        const res = await fetch('/api/config/rules');
        currentRules = await res.json();
    } catch (e) {
        console.error("Failed to fetch rules:", e);
    }
}

function openRulesModal() {
    document.getElementById('rule-stockout').value = currentRules.stockout_days_threshold || 3.0;
    document.getElementById('rule-overstock').value = currentRules.overstock_days_threshold || 45.0;
    document.getElementById('rule-slow').value = currentRules.slow_moving_threshold_days || 14;
    document.getElementById('rule-spike').value = currentRules.spike_threshold_pct || 50.0;
    document.getElementById('rule-drop').value = currentRules.drop_threshold_pct || -40.0;
    document.getElementById('rules-modal').classList.remove('hidden');
}

function closeRulesModal() {
    document.getElementById('rules-modal').classList.add('hidden');
}

async function saveBusinessRules() {
    const payload = {
        stockout_days_threshold: parseFloat(document.getElementById('rule-stockout').value),
        overstock_days_threshold: parseFloat(document.getElementById('rule-overstock').value),
        slow_moving_threshold_days: parseInt(document.getElementById('rule-slow').value),
        spike_threshold_pct: parseFloat(document.getElementById('rule-spike').value),
        drop_threshold_pct: parseFloat(document.getElementById('rule-drop').value)
    };

    try {
        const res = await fetch('/api/config/rules', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        currentRules = data.updated_rules;
        closeRulesModal();
        alert("Business rules updated successfully!");
        location.reload();
    } catch (e) {
        alert("Failed to save rules.");
    }
}

// DASHBOARD LOADER
async function loadDashboard() {
    try {
        const res = await fetch('/api/dashboard/summary');
        const data = await res.json();

        const s = data.summary;
        const kpiContainer = document.getElementById('kpi-cards-container');
        kpiContainer.innerHTML = `
            ${renderKPICard("Total Sales", `$${s.total_revenue.toLocaleString()}`, "dollar-sign", "blue")}
            ${renderKPICard("Units Sold", s.total_units_sold.toLocaleString(), "shopping-cart", "indigo")}
            ${renderKPICard("Catalogue", `${s.total_products} Products`, "package", "slate")}
            ${renderKPICard("Stock-out Risk", s.stockout_risk_count, "alert-triangle", "rose")}
            ${renderKPICard("Overstocked", s.overstocked_count, "archive", "amber")}
            ${renderKPICard("Sales Spikes", s.sales_spikes_count, "trending-up", "emerald")}
            ${renderKPICard("Sales Drops", s.sales_drops_count, "trending-down", "purple")}
        `;

        const attnContainer = document.getElementById('needs-attention-container');
        attnContainer.innerHTML = data.needs_attention_today.map(item => renderNeedsAttentionCard(item)).join('');

        lucide.createIcons();
    } catch (e) {
        console.error("Error loading dashboard:", e);
    }
}

function renderKPICard(title, value, icon, color) {
    const colorClasses = {
        blue: "text-blue-400 bg-blue-500/10 border-blue-500/20",
        indigo: "text-indigo-400 bg-indigo-500/10 border-indigo-500/20",
        slate: "text-slate-400 bg-slate-500/10 border-slate-500/20",
        rose: "text-rose-400 bg-rose-500/10 border-rose-500/20",
        amber: "text-amber-400 bg-amber-500/10 border-amber-500/20",
        emerald: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
        purple: "text-purple-400 bg-purple-500/10 border-purple-500/20"
    };
    const c = colorClasses[color] || colorClasses.blue;

    return `
        <div class="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-2">
            <div class="flex items-center justify-between text-xs text-slate-400">
                <span>${title}</span>
                <div class="w-7 h-7 rounded-lg ${c} flex items-center justify-center border">
                    <i data-lucide="${icon}" class="w-4 h-4"></i>
                </div>
            </div>
            <div class="text-xl font-bold text-white font-mono tracking-tight">${value}</div>
        </div>
    `;
}

function renderNeedsAttentionCard(item) {
    const sevColors = {
        CRITICAL: "border-rose-500/40 bg-rose-950/10 text-rose-400",
        WARNING: "border-amber-500/40 bg-amber-950/10 text-amber-400",
        INFO: "border-blue-500/40 bg-blue-950/10 text-blue-400"
    };
    const badgeStyle = sevColors[item.severity] || sevColors.CRITICAL;

    // Escaped JSON for evidence modal
    const evJson = JSON.stringify(item.evidence).replace(/'/g, "&apos;").replace(/"/g, "&quot;");

    return `
        <div class="bg-slate-950/80 border ${badgeStyle.split(' ')[0]} rounded-xl p-4 space-y-3">
            <div class="flex items-start justify-between">
                <div>
                    <div class="flex items-center space-x-2">
                        <span class="text-xs px-2.5 py-0.5 rounded-full font-bold border ${badgeStyle}">${item.severity}</span>
                        <h4 class="font-bold text-white text-base">${item.product_name}</h4>
                        <span class="text-xs text-slate-400">at ${item.store_name}</span>
                    </div>
                    <p class="text-sm font-semibold text-slate-200 mt-1">${item.problem}</p>
                </div>
                <button onclick='showEvidenceModal(${evJson})' class="text-xs bg-blue-600/20 hover:bg-blue-600/30 text-blue-300 border border-blue-500/30 px-3 py-1.5 rounded-lg flex items-center space-x-1.5 transition">
                    <i data-lucide="search" class="w-3.5 h-3.5"></i>
                    <span>Why am I seeing this?</span>
                </button>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs bg-slate-900/90 p-3 rounded-lg border border-slate-800">
                <div>
                    <span class="text-slate-500 block font-medium">Supporting Numbers</span>
                    <span class="text-slate-200 font-mono">${item.metrics_summary}</span>
                </div>
                <div>
                    <span class="text-slate-500 block font-medium">Why It Matters</span>
                    <span class="text-slate-300">${item.why_it_matters}</span>
                </div>
                <div>
                    <span class="text-slate-500 block font-medium">Recommended Action</span>
                    <span class="text-emerald-400 font-semibold">${item.recommended_action}</span>
                </div>
            </div>

            <div class="text-[11px] text-slate-500 flex items-center justify-between">
                <span>Confidence: ${item.confidence_evidence}</span>
                <span class="italic">Source: Application business rule</span>
            </div>
        </div>
    `;
}

// AI COPILOT CHAT
function sendQuickPrompt(promptText) {
    document.getElementById('chat-input').value = promptText;
    sendChatMessage();
}

async function sendChatMessage() {
    const inputEl = document.getElementById('chat-input');
    const query = inputEl.value.trim();
    if (!query) return;

    inputEl.value = '';
    const history = document.getElementById('chat-history');

    // Render User Message
    history.innerHTML += `
        <div class="flex justify-end">
            <div class="bg-blue-600 text-white rounded-2xl px-4 py-3 text-sm max-w-xl shadow-lg">
                ${escapeHtml(query)}
            </div>
        </div>
    `;

    // Render Loading Indicator
    const loadId = `load-${Date.now()}`;
    history.innerHTML += `
        <div id="${loadId}" class="flex items-center space-x-2 text-slate-400 text-xs py-2">
            <div class="w-4 h-4 rounded-full border-2 border-blue-500 border-t-transparent animate-spin"></div>
            <span>Evaluating deterministic evidence & generating grounded response...</span>
        </div>
    `;
    history.scrollTop = history.scrollHeight;

    try {
        const res = await fetch('/api/copilot/query', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({query: query})
        });
        const data = await res.json();

        document.getElementById(loadId).remove();

        // Render Fallback Banner if applicable
        if (data.is_gemini_fallback) {
            document.getElementById('copilot-fallback-banner').classList.remove('hidden');
            document.getElementById('copilot-fallback-msg').innerText = data.fallback_message;
        }

        const answerHtml = marked.parse(data.answer_markdown);

        // Render Recommendations Cards if any
        let recsHtml = '';
        if (data.recommendations && data.recommendations.length > 0) {
            recsHtml = '<div class="mt-4 space-y-3 font-sans">' + data.recommendations.map(r => {
                const evJson = JSON.stringify(r.evidence).replace(/'/g, "&apos;").replace(/"/g, "&quot;");
                return `
                    <div class="bg-slate-950 border border-slate-800 rounded-xl p-4 text-xs space-y-2">
                        <div class="flex items-center justify-between">
                            <span class="font-bold text-amber-400 text-sm">${r.title}</span>
                            <button onclick='showEvidenceModal(${evJson})' class="text-blue-400 hover:text-blue-300 underline font-medium">Why am I seeing this?</button>
                        </div>
                        <p class="text-slate-300"><strong>Why?</strong> ${r.why_reason}</p>
                        <p class="text-slate-400 italic"><strong>Assumption:</strong> ${r.assumption}</p>
                        <p class="text-emerald-400 font-semibold"><strong>Action:</strong> ${r.recommended_action}</p>
                    </div>
                `;
            }).join('') + '</div>';
        }

        history.innerHTML += `
            <div class="bg-slate-900 border border-slate-800 rounded-2xl p-5 text-sm text-slate-200 space-y-3">
                <div class="flex items-center justify-between border-b border-slate-800 pb-2">
                    <div class="flex items-center space-x-2 text-blue-400 font-semibold">
                        <i data-lucide="bot" class="w-4 h-4"></i>
                        <span>RetailIQ Copilot</span>
                    </div>
                    <span class="text-xs text-slate-500 font-mono">Intent: ${data.parsed_intent}</span>
                </div>

                <div class="prose prose-invert max-w-none text-slate-200 text-sm leading-relaxed">
                    ${answerHtml}
                </div>

                ${recsHtml}
            </div>
        `;
        history.scrollTop = history.scrollHeight;
        lucide.createIcons();

    } catch (e) {
        document.getElementById(loadId).remove();
        history.innerHTML += `
            <div class="bg-rose-950/20 border border-rose-500/30 text-rose-300 p-4 rounded-xl text-xs">
                Failed to execute query. Ensure server is running.
            </div>
        `;
    }
}

// INVENTORY TABLE LOADER
async function loadInventoryTable() {
    const store = document.getElementById('inv-store-filter').value;
    const risk = document.getElementById('inv-risk-filter').value;

    let url = `/api/inventory?`;
    if (store) url += `store_id=${store}&`;
    if (risk) url += `filter_risk=${risk}&`;

    try {
        const res = await fetch(url);
        const data = await res.json();

        const tbody = document.getElementById('inventory-table-body');
        tbody.innerHTML = data.map(m => {
            let riskBadge = `<span class="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-bold">LOW</span>`;
            if (m.stockout_risk === "HIGH") riskBadge = `<span class="px-2 py-0.5 rounded bg-rose-500/10 text-rose-400 border border-rose-500/20 font-bold">HIGH</span>`;
            else if (m.stockout_risk === "MEDIUM") riskBadge = `<span class="px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20 font-bold">MEDIUM</span>`;

            const overBadge = m.overstock_status ? `<span class="text-amber-400 font-bold">YES</span>` : `<span class="text-slate-500">NO</span>`;

            return `
                <tr class="hover:bg-slate-900/50">
                    <td class="p-4 font-semibold text-white">${m.product_name} <span class="text-slate-500 font-mono text-[10px]">(${m.product_id})</span></td>
                    <td class="p-4">${m.store_name}</td>
                    <td class="p-4 font-mono">${m.current_stock} units</td>
                    <td class="p-4 font-mono">${m.avg_daily_sales}/day</td>
                    <td class="p-4 font-mono">${m.days_remaining_str}</td>
                    <td class="p-4">${riskBadge}</td>
                    <td class="p-4 font-mono text-[11px]">${overBadge}</td>
                    <td class="p-4">
                        <button onclick="sendQuickPrompt('Why is ${m.product_name} at ${m.store_name} high risk?')" class="text-blue-400 hover:underline">Inspect</button>
                    </td>
                </tr>
            `;
        }).join('');
    } catch (e) {
        console.error("Error loading inventory:", e);
    }
}

// SALES ANOMALIES LOADER
async function loadAnomalies() {
    try {
        const res = await fetch('/api/anomalies');
        const data = await res.json();

        const container = document.getElementById('anomalies-container');
        container.innerHTML = data.map(a => {
            const isSpike = a.anomaly_type === "SALES_SPIKE";
            const badgeClass = isSpike ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20" : "bg-rose-500/10 text-rose-400 border-rose-500/20";
            const icon = isSpike ? "trending-up" : "trending-down";

            return `
                <div class="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-3">
                    <div class="flex items-center justify-between">
                        <div class="flex items-center space-x-2">
                            <span class="text-xs px-2.5 py-0.5 rounded-full font-bold border ${badgeClass} flex items-center gap-1">
                                <i data-lucide="${icon}" class="w-3.5 h-3.5"></i>
                                ${a.anomaly_type.replace('_', ' ')}
                            </span>
                            <h4 class="font-bold text-white text-base">${a.product_name}</h4>
                        </div>
                        <span class="text-xs font-mono font-bold text-white">${a.pct_change > 0 ? '+' : ''}${a.pct_change}%</span>
                    </div>

                    <p class="text-xs text-slate-300">${a.interpretation}</p>

                    <div class="bg-slate-950 p-3 rounded-xl text-xs font-mono space-y-1 border border-slate-800 text-slate-400">
                        <div>Recent 7-Day Sales: <span class="text-white">${a.recent_7day_sales} units</span> (${a.recent_daily_avg}/day)</div>
                        <div>Historical 30-Day Baseline (excl. 7d): <span class="text-white">${a.historical_baseline_weekly} units/wk</span> (${a.historical_daily_avg}/day)</div>
                    </div>

                    <div class="text-[11px] text-slate-500 italic">
                        Rule: ${a.detection_rule}
                    </div>
                </div>
            `;
        }).join('');

        lucide.createIcons();
    } catch (e) {
        console.error("Error loading anomalies:", e);
    }
}

// STORE COMPARISON LOADER
async function loadStoreComparison() {
    try {
        const res = await fetch('/api/stores/comparison');
        const data = await res.json();

        const container = document.getElementById('store-comparison-container');
        container.innerHTML = data.map(s => {
            return `
                <div class="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-4">
                    <div class="flex items-center justify-between border-b border-slate-800 pb-3">
                        <div>
                            <h3 class="font-bold text-white text-base">${s.store_name}</h3>
                            <span class="text-xs text-slate-400">${s.location} | Manager: ${s.manager}</span>
                        </div>
                        <div class="text-right">
                            <span class="text-xs text-slate-400 block">Health Score</span>
                            <span class="text-lg font-bold text-emerald-400 font-mono">${s.health_score}/100</span>
                        </div>
                    </div>

                    <div class="space-y-2 text-xs text-slate-300">
                        <div class="flex justify-between">
                            <span>Total Revenue (90d):</span>
                            <strong class="font-mono text-white">$${s.total_revenue.toLocaleString()}</strong>
                        </div>
                        <div class="flex justify-between">
                            <span>Units Sold:</span>
                            <strong class="font-mono text-white">${s.total_units_sold.toLocaleString()}</strong>
                        </div>
                        <div class="flex justify-between">
                            <span>Top Product:</span>
                            <strong class="text-blue-400">${s.top_product}</strong>
                        </div>
                        <div class="flex justify-between">
                            <span>Stock-out Risks:</span>
                            <strong class="text-rose-400 font-mono">${s.stockout_risk_count}</strong>
                        </div>
                        <div class="flex justify-between">
                            <span>Overstocked Items:</span>
                            <strong class="text-amber-400 font-mono">${s.overstock_count}</strong>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    } catch (e) {
        console.error("Error loading store comparison:", e);
    }
}

// PRODUCT CATALOGUE LOADER
async function loadProductsTable() {
    try {
        const res = await fetch('/api/products');
        const data = await res.json();

        const tbody = document.getElementById('products-table-body');
        tbody.innerHTML = data.map(p => {
            return `
                <tr class="hover:bg-slate-900/50">
                    <td class="p-4 font-mono text-slate-500">${p.product_id}</td>
                    <td class="p-4 font-bold text-white">${p.product_name}</td>
                    <td class="p-4">${p.category}</td>
                    <td class="p-4 font-mono text-emerald-400">$${p.price}</td>
                    <td class="p-4 font-mono text-slate-400">$${p.cost}</td>
                    <td class="p-4">${p.supplier}</td>
                    <td class="p-4 font-mono">${p.lead_time_days} days</td>
                    <td class="p-4">
                        <button onclick="sendQuickPrompt('How did ${p.product_name} perform this month?')" class="text-blue-400 hover:underline">Query AI</button>
                    </td>
                </tr>
            `;
        }).join('');
    } catch (e) {
        console.error("Error loading products:", e);
    }
}

// EVIDENCE EXPLORER MODAL ("Why am I seeing this?")
function showEvidenceModal(ev) {
    const modalBody = document.getElementById('evidence-modal-body');

    modalBody.innerHTML = `
        <div class="space-y-4">
            <div class="bg-blue-950/20 border border-blue-500/30 rounded-xl p-4">
                <span class="text-xs uppercase tracking-wider text-blue-400 font-bold block mb-1">Finding</span>
                <p class="font-bold text-white text-base">${ev.finding}</p>
            </div>

            <div class="bg-slate-950 rounded-xl p-4 border border-slate-800 space-y-2">
                <span class="text-xs uppercase tracking-wider text-slate-400 font-bold block">Supporting Evidence</span>
                <div class="grid grid-cols-2 gap-2 text-xs font-mono">
                    ${Object.entries(ev.metrics).map(([k, v]) => `
                        <div class="bg-slate-900 p-2 rounded">
                            <span class="text-slate-400 block">${k}</span>
                            <span class="text-white font-bold">${v}</span>
                        </div>
                    `).join('')}
                </div>
            </div>

            <div class="bg-slate-950 rounded-xl p-4 border border-slate-800 space-y-2">
                <span class="text-xs uppercase tracking-wider text-slate-400 font-bold block">Configured Business Rule</span>
                <code class="bg-slate-900 text-amber-300 p-2 rounded block text-xs font-mono border border-slate-800">${ev.configured_rule}</code>
                <p class="text-[11px] text-slate-500 italic">Source: ${ev.rule_source}</p>
            </div>

            <div class="bg-slate-950 rounded-xl p-4 border border-slate-800 space-y-2">
                <span class="text-xs uppercase tracking-wider text-slate-400 font-bold block">Step-by-Step Calculation</span>
                <div class="space-y-1 font-mono text-xs text-slate-300">
                    ${ev.calculation_steps.map(step => `<div class="bg-slate-900 p-2 rounded">${step}</div>`).join('')}
                </div>
            </div>

            <div class="bg-emerald-950/20 border border-emerald-500/30 rounded-xl p-4 space-y-1">
                <span class="text-xs uppercase tracking-wider text-emerald-400 font-bold block">Conclusion & Action</span>
                <p class="text-xs text-slate-200"><strong>Conclusion:</strong> ${ev.conclusion}</p>
                <p class="text-xs text-emerald-400 font-semibold"><strong>Action:</strong> ${ev.recommended_action}</p>
            </div>

            <div class="text-xs text-slate-400 space-y-1 border-t border-slate-800 pt-3">
                <span class="font-bold text-slate-300 block">Stated Assumptions:</span>
                ${ev.assumptions.map(a => `<p>- ${a}</p>`).join('')}
            </div>
        </div>
    `;

    document.getElementById('evidence-modal').classList.remove('hidden');
    lucide.createIcons();
}

function closeEvidenceModal() {
    document.getElementById('evidence-modal').classList.add('hidden');
}

function escapeHtml(str) {
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
