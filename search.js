// 引入 Fuse.js（可用CDN或本地）
// <script src="https://cdn.jsdelivr.net/npm/fuse.js/dist/fuse.min.js"></script>

async function loadSearch() {
  const res = await fetch('/index.json');
  const data = await res.json();
  const fuse = new Fuse(data, {
    keys: ['title'],
    threshold: 0.3
  });

  const input = document.getElementById('search-input');
  const result = document.getElementById('search-result');

  input.addEventListener('input', function() {
    const q = input.value.trim();
    result.innerHTML = '';
    if (q.length === 0) return;
    const found = fuse.search(q).filter(item => item.item.date);
    found.forEach(item => {
      const li = document.createElement('li');
      li.innerHTML = `<a href="${item.item.permalink}">${item.item.title}</a> <span style="color:#888;font-size:0.9em;margin-left:8px;">${item.item.date}</span>`;
      result.appendChild(li);
    });
  });
}

window.addEventListener('DOMContentLoaded', loadSearch);