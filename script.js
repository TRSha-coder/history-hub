const loadingEl = document.getElementById('loading');
const errorEl = document.getElementById('error');
const resourceContainer = document.getElementById('resourceContainer');
const refreshBtn = document.getElementById('refreshBtn');
const updatedAtEl = document.getElementById('updatedAt');
const totalCountEl = document.getElementById('totalCount');
const sourceSummaryEl = document.getElementById('sourceSummary');
const searchInputEl = document.getElementById('searchInput');
const clearSearchBtnEl = document.getElementById('clearSearchBtn');

let allItems = [];
let currentSource = 'all';
let currentKeyword = '';

function sourceLabel(source) {
    if (source === 'shuge') return '书格';
    if (source === 'zh-wikipedia') return '中文维基百科';
    return source || '未知来源';
}

function safeText(value) {
    if (value === null || value === undefined) return '';
    return String(value);
}

function formatYear(item) {
    const year = safeText(item.year).trim();
    if (year) return year;
    const date = safeText(item.date).trim();
    if (/^\d{4}/.test(date)) return date.slice(0, 4);
    return '年份未知';
}

function renderCards(items) {
    if (!items.length) {
        resourceContainer.innerHTML = '<div class="empty">没有匹配到资源，请尝试其他关键词。</div>';
        totalCountEl.textContent = '0';
        return;
    }

    resourceContainer.innerHTML = items.map((item) => {
        const title = escapeHtml(safeText(item.title) || '未命名资源');
        const summary = escapeHtml(safeText(item.summary) || '暂无摘要');
        const year = escapeHtml(formatYear(item));
        const source = escapeHtml(sourceLabel(item.source));
        const link = safeText(item.link) || '#';
        return `
            <article class="card">
                <div class="card-meta">
                    <span class="badge">${source}</span>
                    <span class="year">${year}</span>
                </div>
                <h3>${title}</h3>
                <p>${summary}</p>
                <a href="${encodeURI(link)}" target="_blank" rel="noopener noreferrer">查看原文</a>
            </article>
        `;
    }).join('');

    totalCountEl.textContent = String(items.length);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showLoading() {
    loadingEl.style.display = 'block';
    errorEl.style.display = 'none';
    resourceContainer.innerHTML = '';
}

function hideLoading() {
    loadingEl.style.display = 'none';
}

function showError() {
    loadingEl.style.display = 'none';
    errorEl.style.display = 'block';
}

function applyFilters() {
    const keyword = currentKeyword.trim().toLowerCase();
    const filtered = allItems.filter((item) => {
        const matchSource = currentSource === 'all' || item.source === currentSource;
        const corpus = `${safeText(item.title)} ${safeText(item.summary)} ${safeText(item.subjects)}`.toLowerCase();
        const matchKeyword = !keyword || corpus.includes(keyword);
        return matchSource && matchKeyword;
    });
    renderCards(filtered);
}

function updateSummary(meta) {
    updatedAtEl.textContent = safeText(meta.updatedAt) || '未知';
    const sourceLines = Object.entries(meta.sourceStats || {}).map(([key, value]) => {
        return `${sourceLabel(key)}：${value}`;
    });
    sourceSummaryEl.textContent = sourceLines.length ? `来源分布：${sourceLines.join(' · ')}` : '来源分布：暂无';
}

async function loadData() {
    showLoading();
    refreshBtn.disabled = true;
    try {
        const response = await fetch('data/magazines.json', { cache: 'no-cache' });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        allItems = Array.isArray(data.items) ? data.items : [];
        updateSummary(data.meta || {});
        hideLoading();
        applyFilters();
    } catch (error) {
        console.error(error);
        showError();
    } finally {
        refreshBtn.disabled = false;
    }
}

document.querySelectorAll('.tab').forEach((tab) => {
    tab.addEventListener('click', () => {
        document.querySelectorAll('.tab').forEach((btn) => btn.classList.remove('active'));
        tab.classList.add('active');
        currentSource = tab.dataset.source;
        applyFilters();
    });
});

searchInputEl.addEventListener('input', () => {
    currentKeyword = searchInputEl.value;
    applyFilters();
});

clearSearchBtnEl.addEventListener('click', () => {
    searchInputEl.value = '';
    currentKeyword = '';
    applyFilters();
});

refreshBtn.addEventListener('click', () => window.location.reload());

loadData();
