const API = '/api';

const state = {
  offset: 0,
  limit: 75,
  q: '',
  sort: 'id',
  order: 'asc',
  tag: '',
  /** 'all' | 'blind75' — sent as GET /api/catalog?list=… */
  list: 'all',
};

function showToast(message, type = 'success') {
  const toast = document.createElement('div');
  toast.className = `toast ${type} show`;
  toast.textContent = message;
  document.body.appendChild(toast);
  setTimeout(() => {
    toast.classList.remove('show');
    setTimeout(() => toast.remove(), 300);
  }, 2500);
}

async function fetchJson(url, options = {}) {
  const res = await fetch(url, {
    ...options,
    headers: { 'Content-Type': 'application/json', ...options.headers },
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || res.statusText);
  return data;
}

function escapeHtml(s) {
  if (s == null) return '';
  const div = document.createElement('div');
  div.textContent = s;
  return div.innerHTML;
}

// Tabs
document.querySelectorAll('.tab').forEach((tab) => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.tab').forEach((t) => t.classList.remove('active'));
    document.querySelectorAll('.panel').forEach((p) => p.classList.remove('active'));
    tab.classList.add('active');
    document.getElementById(tab.dataset.tab).classList.add('active');
    if (tab.dataset.tab === 'catalog') loadCatalog();
    if (tab.dataset.tab === 'stats') loadStats();
  });
});

function buildCatalogQuery() {
  const params = new URLSearchParams({
    limit: String(state.limit),
    offset: String(state.offset),
    sort: state.sort,
    order: state.order,
  });
  if (state.list && state.list !== 'all') params.set('list', state.list);
  if (state.q) params.set('q', state.q);
  if (state.tag) params.set('tag', state.tag);
  return params.toString();
}

function catalogTagsUrl() {
  if (state.list && state.list !== 'all') {
    return `${API}/catalog/tags?list=${encodeURIComponent(state.list)}`;
  }
  return `${API}/catalog/tags`;
}

async function loadCatalogTags() {
  const tagSelect = document.getElementById('tagFilter');
  const hint = document.getElementById('tagHint');
  try {
    const tags = await fetchJson(catalogTagsUrl());
    tagSelect.innerHTML = '<option value="">All topics</option>';
    tags.forEach((t) => {
      const opt = document.createElement('option');
      opt.value = t;
      opt.textContent = t;
      tagSelect.appendChild(opt);
    });
    tagSelect.value = state.tag;
    if (tags.length === 0) {
      hint.textContent =
        'No topic tags yet. Populate data/problem_topics.json as { "problem-slug": ["Array", "Hash Table"] } to enable topic filters and stats.';
    } else {
      hint.textContent = '';
    }
  } catch (e) {
    hint.textContent = '';
  }
}

async function loadCatalog() {
  const tbody = document.getElementById('catalogBody');
  const pag = document.getElementById('catalogPagination');
  try {
    const data = await fetchJson(`${API}/catalog?${buildCatalogQuery()}`);
    const items = data.items || [];
    if (items.length === 0) {
      tbody.innerHTML = '<tr><td colspan="4" class="empty-cell">No problems match.</td></tr>';
    } else {
      tbody.innerHTML = items
        .map((p) => {
          const diff = (p.difficulty || '').toLowerCase();
          const diffClass =
            diff === 'easy' || diff === 'medium' || diff === 'hard' ? diff : '';
          const tags = (p.tags || []).slice(0, 4).map((t) => `<span class="tag-chip">${escapeHtml(t)}</span>`).join(' ');
          const paid = p.paid_only ? ' <span class="badge-paid">Premium</span>' : '';
          return `
            <tr class="catalog-row" data-id="${p.id}" tabindex="0">
              <td class="mono">${p.id}</td>
              <td class="title-cell">${escapeHtml(p.title)}${paid}</td>
              <td><span class="difficulty ${diffClass}">${escapeHtml(p.difficulty)}</span></td>
              <td class="tags-cell">${tags || '<span class="text-muted">—</span>'}</td>
            </tr>`;
        })
        .join('');
      tbody.querySelectorAll('.catalog-row').forEach((row) => {
        const id = row.dataset.id;
        row.addEventListener('click', () => openProblemModal(id));
        row.addEventListener('keydown', (ev) => {
          if (ev.key === 'Enter' || ev.key === ' ') {
            ev.preventDefault();
            openProblemModal(id);
          }
        });
      });
    }
    const listHintEl = document.getElementById('catalogListHint');
    if (listHintEl) {
      if (data.list === 'blind75' && data.list_size != null) {
        const m =
          data.matched_in_catalog != null ? data.matched_in_catalog : data.total;
        const missing = data.list_size - m;
        const extra =
          missing > 0
            ? ` ${missing} id(s) from the list are not in your leetcode.json export.`
            : '';
        listHintEl.textContent = `Blind 75: ${m} of ${data.list_size} problems in catalog.${extra}`;
      } else {
        listHintEl.textContent = '';
      }
    }

    const total = data.total ?? 0;
    const end = Math.min(state.offset + state.limit, total);
    const prevDisabled = state.offset <= 0;
    const nextDisabled = state.offset + state.limit >= total;
    pag.innerHTML = `
      <span class="page-info">${total ? state.offset + 1 : 0}–${end} of ${total}</span>
      <button type="button" class="btn btn-secondary" id="prevPage" ${prevDisabled ? 'disabled' : ''}>Previous</button>
      <button type="button" class="btn btn-secondary" id="nextPage" ${nextDisabled ? 'disabled' : ''}>Next</button>
    `;
    const prev = document.getElementById('prevPage');
    const next = document.getElementById('nextPage');
    if (prev && !prevDisabled) prev.onclick = () => { state.offset = Math.max(0, state.offset - state.limit); loadCatalog(); };
    if (next && !nextDisabled) next.onclick = () => { state.offset = state.offset + state.limit; loadCatalog(); };
  } catch (e) {
    tbody.innerHTML = `<tr><td colspan="4" class="empty-cell">Error: ${escapeHtml(e.message)}</td></tr>`;
    pag.innerHTML = '';
  }
}

let searchDebounce;
document.getElementById('catalogSearch').addEventListener('input', (e) => {
  clearTimeout(searchDebounce);
  searchDebounce = setTimeout(() => {
    state.q = e.target.value.trim();
    state.offset = 0;
    loadCatalog();
  }, 300);
});

document.getElementById('catalogList').addEventListener('change', (e) => {
  state.list = e.target.value || 'all';
  state.tag = '';
  state.offset = 0;
  loadCatalogTags();
  loadCatalog();
});

['sortBy', 'sortOrder', 'tagFilter'].forEach((id) => {
  document.getElementById(id).addEventListener('change', (e) => {
    if (id === 'sortBy') state.sort = e.target.value;
    if (id === 'sortOrder') state.order = e.target.value;
    if (id === 'tagFilter') state.tag = e.target.value;
    state.offset = 0;
    loadCatalog();
  });
});

async function openProblemModal(problemId) {
  const modal = document.getElementById('problemModal');
  const body = document.getElementById('modalBody');
  const id = String(problemId);
  try {
    const p = await fetchJson(`${API}/catalog/${id}`);
    const attempts = p.attempts || [];
    const diff = (p.difficulty || '').toLowerCase();
    const diffClass = diff === 'easy' || diff === 'medium' || diff === 'hard' ? diff : '';
    const tags = (p.tags || []).map((t) => `<span class="tag-chip">${escapeHtml(t)}</span>`).join(' ');
    body.innerHTML = `
      <h2 class="modal-title">${escapeHtml(p.title)}</h2>
      <div class="meta">
        <span class="mono">#${p.id}</span>
        <span class="difficulty ${diffClass}">${escapeHtml(p.difficulty)}</span>
        ${p.paid_only ? '<span class="badge-paid">Premium</span>' : ''}
      </div>
      ${tags ? `<div class="modal-tags">${tags}</div>` : ''}
      ${p.link ? `<p><a href="${escapeHtml(p.link)}" target="_blank" rel="noopener noreferrer">Open on LeetCode</a></p>` : ''}
      <div class="notes-section">
        <h4>Attempts</h4>
        ${attempts.length === 0 ? '<p class="text-muted">No attempts logged yet.</p>' : ''}
        ${attempts.map((n) => `
          <div class="note-item" data-attempt="${escapeHtml(String(n.attempt))}">
            <div class="note-meta">Attempt ${escapeHtml(String(n.attempt))} · ${escapeHtml(n.timestamp || '')}</div>
            <div><strong>${escapeHtml(n.approach || '')}</strong> · ${n.solved ? 'Solved' : 'Not solved'}</div>
            <div>${escapeHtml(n.reflection || '')}</div>
            <div>Time: ${escapeHtml(n.time_spent || '')}</div>
            <button type="button" class="btn btn-danger delete-note-btn" data-attempt="${escapeHtml(String(n.attempt))}">Delete attempt</button>
          </div>
        `).join('')}
      </div>
      <div class="add-note-form">
        <h4>Log attempt</h4>
        <input type="text" name="time_spent" placeholder="Time spent (e.g. 30 minutes)" required>
        <input type="text" name="approach" placeholder="Approach used" required>
        <label class="checkbox-row">
          <input type="checkbox" name="solved"> Solved
        </label>
        <textarea name="reflection" placeholder="Reflection (optional)" rows="3"></textarea>
        <button type="button" class="btn btn-primary add-note-btn">Save attempt</button>
      </div>
    `;
    body.querySelectorAll('.delete-note-btn').forEach((btn) => {
      btn.addEventListener('click', async () => {
        if (!confirm('Delete this attempt?')) return;
        try {
          await fetchJson(`${API}/catalog/${id}/attempts/${encodeURIComponent(btn.dataset.attempt)}`, {
            method: 'DELETE',
          });
          showToast('Attempt deleted');
          openProblemModal(id);
        } catch (err) {
          showToast(err.message, 'error');
        }
      });
    });
    body.querySelector('.add-note-btn').addEventListener('click', async () => {
      const form = body.querySelector('.add-note-form');
      const timeSpent = form.querySelector('[name="time_spent"]').value.trim();
      const approach = form.querySelector('[name="approach"]').value.trim();
      const reflection = form.querySelector('[name="reflection"]').value.trim();
      const solved = form.querySelector('[name="solved"]').checked;
      if (!timeSpent || !approach) {
        showToast('Time spent and approach are required', 'error');
        return;
      }
      try {
        await fetchJson(`${API}/catalog/${id}/attempts`, {
          method: 'POST',
          body: JSON.stringify({
            time_spent: timeSpent,
            approach,
            reflection,
            solved,
          }),
        });
        showToast('Attempt saved');
        openProblemModal(id);
      } catch (err) {
        showToast(err.message, 'error');
      }
    });
    modal.classList.add('active');
  } catch (e) {
    body.innerHTML = `<p>${escapeHtml(e.message)}</p>`;
    modal.classList.add('active');
  }
}

document.querySelector('.modal-close').addEventListener('click', () => {
  document.getElementById('problemModal').classList.remove('active');
});

document.getElementById('problemModal').addEventListener('click', (e) => {
  if (e.target.id === 'problemModal') e.target.classList.remove('active');
});

document.getElementById('searchAttemptsBtn').addEventListener('click', async () => {
  const q = document.getElementById('approachSearch').value.trim();
  const el = document.getElementById('searchResults');
  if (!q) {
    el.innerHTML = '<div class="empty-state">Enter a keyword.</div>';
    return;
  }
  try {
    const results = await fetchJson(`${API}/search?q=${encodeURIComponent(q)}`);
    if (results.length === 0) {
      el.innerHTML = '<div class="empty-state">No matching attempts.</div>';
      return;
    }
    el.innerHTML = results
      .map((p) => {
        const diff = (p.difficulty || '').toLowerCase();
        const diffClass = diff === 'easy' || diff === 'medium' || diff === 'hard' ? diff : '';
        return `
        <div class="problem-card" data-id="${p.id}">
          <div class="title">${escapeHtml(p.title)} <span class="mono">#${p.id}</span></div>
          <div class="meta">
            <span class="difficulty ${diffClass}">${escapeHtml(p.difficulty)}</span>
            <span>${(p.notes || []).length} matching note(s)</span>
          </div>
        </div>`;
      })
      .join('');
    el.querySelectorAll('.problem-card').forEach((card) => {
      card.addEventListener('click', () => openProblemModal(card.dataset.id));
    });
  } catch (e) {
    el.innerHTML = `<div class="empty-state">${escapeHtml(e.message)}</div>`;
  }
});

async function loadStats() {
  try {
    const [fastest, slowest] = await Promise.all([
      fetchJson(`${API}/stats/fastest-hard`),
      fetchJson(`${API}/stats/slowest-categories`),
    ]);
    const fastestEl = document.getElementById('fastestHard');
    const slowestEl = document.getElementById('slowestCategories');
    fastestEl.innerHTML =
      fastest.length === 0
        ? '<li>No hard problems with time data yet.</li>'
        : fastest.map((x) => `<li>${escapeHtml(x.title)} (#${x.id}) → ${x.minutes} min</li>`).join('');
    slowestEl.innerHTML =
      slowest.length === 0
        ? '<li>No topic data yet.</li>'
        : slowest.map((x) => `<li>${escapeHtml(x.category)}: ${x.avg_minutes} min (avg)</li>`).join('');
  } catch (e) {
    document.getElementById('fastestHard').innerHTML = `<li>Error: ${escapeHtml(e.message)}</li>`;
    document.getElementById('slowestCategories').innerHTML = '';
  }
}

document.getElementById('loadStatsBtn').addEventListener('click', async () => {
  const raw = document.getElementById('statsProblemId').value.trim();
  const el = document.getElementById('timeStats');
  if (!raw) {
    showToast('Enter a problem number', 'error');
    return;
  }
  const pid = parseInt(raw, 10);
  if (Number.isNaN(pid)) {
    showToast('Invalid problem number', 'error');
    return;
  }
  try {
    const stats = await fetchJson(`${API}/stats/time/${pid}`);
    if (stats.average == null) {
      el.innerHTML = '<p>No time data for this problem.</p>';
    } else {
      el.innerHTML = `
        <div class="stat-row">Average: ${stats.average} min</div>
        <div class="stat-row">Shortest: ${stats.shortest} min</div>
        <div class="stat-row">Longest: ${stats.longest} min</div>
      `;
    }
  } catch (err) {
    el.innerHTML = `<p>${escapeHtml(err.message)}</p>`;
  }
});

state.list = document.getElementById('catalogList').value || 'all';
state.sort = document.getElementById('sortBy').value;
state.order = document.getElementById('sortOrder').value;
loadCatalogTags();
loadCatalog();
