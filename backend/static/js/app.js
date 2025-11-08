// API Configuration
const API_BASE = window.location.origin;
const API_CHAT = API_BASE + '/api/chat';
const API_HEALTH = API_BASE + '/api/health';
const API_TABLE = API_BASE + '/api/table';

const state = { isLoading: false, currentTable: null, tableData: [], sortColumn: null, sortDirection: 'asc' };
let chatMessages, chatForm, chatInput, sendButton, statusDot, statusText, tableSelect, dataContent;

document.addEventListener('DOMContentLoaded', function() {
    chatMessages = document.getElementById('chatMessages');
    chatForm = document.getElementById('chatForm');
    chatInput = document.getElementById('chatInput');
    sendButton = document.getElementById('sendButton');
    statusDot = document.getElementById('statusDot');
    statusText = document.getElementById('statusText');
    tableSelect = document.getElementById('tableSelect');
    dataContent = document.getElementById('dataContent');
    chatForm.addEventListener('submit', handleChat);
    chatInput.addEventListener('input', autoResize);
    chatInput.addEventListener('keydown', e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); chatForm.dispatchEvent(new Event('submit')); } });
    tableSelect.addEventListener('change', loadTable);
    checkHealth();

    // Load sales_transactions by default
    tableSelect.value = 'sales_transactions';
    loadTable();
});

async function checkHealth() {
    try { const res = await fetch(API_HEALTH); const data = await res.json(); updateStatus(data.status === 'healthy' ? 'online' : 'error', data.status === 'healthy' ? 'Connected' : 'Error'); }
    catch { updateStatus('error', 'Disconnected'); }
}

function updateStatus(status, text) { statusDot.className = 'status-dot' + (status === 'online' ? '' : ' ' + status); statusText.textContent = text; }

async function handleChat(e) {
    e.preventDefault(); const query = chatInput.value.trim(); if (!query || state.isLoading) return;
    addMessage('user', query); chatInput.value = ''; autoResize(); state.isLoading = true; sendButton.disabled = true;
    const loadingDiv = addMessage('loading', 'Analyzing...');
    try {
        const res = await fetch(API_CHAT, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ query }) });
        const data = await res.json(); loadingDiv.remove();
        if (data.success) addMessage('assistant', data.answer, data.agent); else addMessage('assistant', 'Error: ' + (data.error || 'Unknown error'), 'Error Handler');
    } catch (err) { loadingDiv.remove(); addMessage('assistant', 'Failed: ' + err.message, 'Error'); }
    finally { state.isLoading = false; sendButton.disabled = false; chatInput.focus(); }
}

function addMessage(type, content, agent) {
    const div = document.createElement('div');
    div.className = 'message ' + type + '-message';

    if (type === 'loading') {
        div.innerHTML = '<div class="loading-message"><div class="loading-dots"><span></span><span></span><span></span></div> ' + content + '</div>';
    } else {
        const mc = document.createElement('div');
        mc.className = 'message-content';

        if (type === 'assistant' && agent) {
            const b = document.createElement('div');
            b.className = 'agent-badge';
            b.textContent = agent;
            mc.appendChild(b);
        }

        const t = document.createElement('div');
        t.innerHTML = content.replace(/\n/g, '<br>');
        mc.appendChild(t);
        div.appendChild(mc);
    }

    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return div;
}

function autoResize() { chatInput.style.height = 'auto'; chatInput.style.height = Math.min(chatInput.scrollHeight, 120) + 'px'; }

async function loadTable() {
    const tableName = tableSelect.value;
    if (!tableName) { dataContent.innerHTML = '<div class="data-placeholder"><svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M3 6h18M3 12h18M3 18h18"/></svg><p>Select a table to view data</p></div>'; return; }
    dataContent.innerHTML = '<div class="table-loading">Loading data...</div>'; state.currentTable = tableName;
    try {
        const res = await fetch(API_TABLE + '/' + tableName); const data = await res.json();
        if (data.success) { state.tableData = data.data; renderTable(data.data, data.columns); }
        else dataContent.innerHTML = '<div class="table-loading">Error: ' + data.error + '</div>';
    } catch (err) { dataContent.innerHTML = '<div class="table-loading">Failed: ' + err.message + '</div>'; }
}

function renderTable(data, columns) {
    const c = document.createElement('div'); c.style.cssText = 'display: flex; flex-direction: column; height: 100%;';
    const ctrl = document.createElement('div'); ctrl.className = 'table-controls';
    ctrl.innerHTML = '<div class="table-info">Showing ' + data.length + ' rows</div><div class="table-search"><input type="text" class="search-input" placeholder="Search..."></div>';
    c.appendChild(ctrl);
    const tc = document.createElement('div'); tc.className = 'table-container';
    const tbl = document.createElement('table'); tbl.className = 'data-table';
    const thead = document.createElement('thead'); const hr = document.createElement('tr');
    columns.forEach(col => { const th = document.createElement('th'); th.textContent = col; th.className = 'sortable'; th.onclick = () => sortTable(col); hr.appendChild(th); });
    thead.appendChild(hr); tbl.appendChild(thead);
    const tbody = document.createElement('tbody');
    data.forEach(row => { const tr = document.createElement('tr'); columns.forEach(col => { const td = document.createElement('td'); td.textContent = row[col] !== null && row[col] !== undefined ? row[col] : ''; tr.appendChild(td); }); tbody.appendChild(tr); });
    tbl.appendChild(tbody); tc.appendChild(tbl); c.appendChild(tc);
    const si = ctrl.querySelector('.search-input');
    si.addEventListener('input', e => { const term = e.target.value.toLowerCase(); const rows = tbody.querySelectorAll('tr'); rows.forEach(row => { row.style.display = row.textContent.toLowerCase().includes(term) ? '' : 'none'; }); });
    dataContent.innerHTML = ''; dataContent.appendChild(c);
}

function sortTable(column) {
    if (state.sortColumn === column) state.sortDirection = state.sortDirection === 'asc' ? 'desc' : 'asc';
    else { state.sortColumn = column; state.sortDirection = 'asc'; }
    state.tableData.sort((a, b) => {
        let valA = a[column], valB = b[column];
        if (typeof valA === 'string') valA = valA.toLowerCase();
        if (typeof valB === 'string') valB = valB.toLowerCase();
        return (valA < valB ? -1 : valA > valB ? 1 : 0) * (state.sortDirection === 'asc' ? 1 : -1);
    });
    loadTable();
}
