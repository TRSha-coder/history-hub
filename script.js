const grid = document.getElementById('grid');
const q = document.getElementById('q');
const stats = document.getElementById('stats');
const tpl = document.getElementById('cardTpl');
const reloadBtn = document.getElementById('reloadBtn');
const bookshelfBtn = document.getElementById('bookshelfBtn');

const readerModal = document.getElementById('readerModal');
const readerFrame = document.getElementById('readerFrame');
const readerTitle = document.getElementById('readerTitle');
const closeReaderBtn = document.getElementById('closeReaderBtn');

let allItems = [];
let showOnlyBookshelf = false;

// 书架使用 localStorage 存储 identifier
function getBookshelf() {
  try {
    return JSON.parse(localStorage.getItem('history-bookshelf') || '[]');
  } catch (e) {
    return [];
  }
}

function saveBookshelf(books) {
  localStorage.setItem('history-bookshelf', JSON.stringify(books));
}

function toggleBookmark(identifier) {
  let books = getBookshelf();
  if (books.includes(identifier)) {
    books = books.filter(id => id !== identifier);
  } else {
    books.push(identifier);
  }
  saveBookshelf(books);
  render();
}

async function loadData() {
  try {
    const res = await fetch('./data/magazines.json', { cache: 'no-store' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    allItems = data.items || [];
    render();
  } catch (err) {
    stats.textContent = `加载失败：${err.message}。请先运行抓取脚本生成 data/magazines.json`;
  }
}

function normalize(v) {
  return String(v ?? '').toLowerCase();
}

function render() {
  const keyword = normalize(q.value).trim();
  const books = getBookshelf();

  const filtered = allItems.filter((item) => {
    if (showOnlyBookshelf && !books.includes(item.identifier)) {
      return false;
    }
    if (!keyword) return true;
    const joined = [
      item.title,
      item.year,
      item.identifier,
      ...(item.subject || [])
    ].map(normalize).join(' ');
    return joined.includes(keyword);
  });

  stats.textContent = showOnlyBookshelf 
    ? `书架共 ${filtered.length} 条`
    : `共 ${allItems.length} 条，当前显示 ${filtered.length} 条`;
  
  grid.innerHTML = '';

  filtered.forEach((item) => {
    const node = tpl.content.firstElementChild.cloneNode(true);
    node.querySelector('.title').textContent = item.title || 'Untitled';
    node.querySelector('.meta').textContent = `年份：${item.year || '未知'} · ID：${item.identifier}`;
    node.querySelector('.desc').textContent = item.description || '暂无简介';
    
    const tags = node.querySelector('.tags');
    (item.subject || []).slice(0, 5).forEach((tag) => {
      const el = document.createElement('span');
      el.className = 'tag';
      el.textContent = tag;
      tags.appendChild(el);
    });

    // 书架按钮
    const bookmarkBtn = node.querySelector('.bookmark-btn');
    const isSaved = books.includes(item.identifier);
    if (isSaved) {
      bookmarkBtn.classList.add('saved');
      bookmarkBtn.textContent = '移出书架';
    }
    bookmarkBtn.addEventListener('click', () => toggleBookmark(item.identifier));

    // 站内阅读按钮
    const readBtn = node.querySelector('.read-btn');
    readBtn.addEventListener('click', () => openReader(item.title, item.url));

    // 外部链接
    const link = node.querySelector('.link');
    link.href = item.url;
    
    grid.appendChild(node);
  });
}

function openReader(title, url) {
  readerTitle.textContent = title;
  readerFrame.src = url;
  readerModal.classList.add('open');
}

closeReaderBtn.addEventListener('click', () => {
  readerModal.classList.remove('open');
  readerFrame.src = ''; // 清空 iframe，停止加载
});

q.addEventListener('input', render);
reloadBtn.addEventListener('click', () => {
  alert('静态站不直接联网抓取。\n请在项目目录运行：\npython scripts/fetch_magazines.py\n然后刷新页面。');
});

bookshelfBtn.addEventListener('click', () => {
  showOnlyBookshelf = !showOnlyBookshelf;
  bookshelfBtn.classList.toggle('active', showOnlyBookshelf);
  render();
});

loadData();