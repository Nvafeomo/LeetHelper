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
  /** last /api/catalog total (for page jump) */
  catalogTotal: 0,
  attemptsTitle: '',
  attemptsTopic: '',
  attemptsApproach: '',
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
    if (tab.dataset.tab === 'attempts') {
      loadAttemptsTags();
      loadAttempts();
    }
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
    state.catalogTotal = total;
    const end = Math.min(state.offset + state.limit, total);
    const prevDisabled = state.offset <= 0;
    const nextDisabled = total === 0 || state.offset + state.limit >= total;
    const totalPages = total === 0 ? 0 : Math.ceil(total / state.limit);
    const currentPage = total === 0 ? 1 : Math.floor(state.offset / state.limit) + 1;

    const jumpBlock =
      totalPages > 0
        ? `
      <label class="page-jump">
        <span class="page-jump-label">Page</span>
        <input type="number" class="page-jump-input" id="catalogPageInput" min="1" max="${totalPages}" value="${currentPage}" aria-label="Page number" />
        <span class="page-jump-of">of ${totalPages}</span>
      </label>
      <button type="button" class="btn btn-secondary" id="catalogPageGo">Go</button>
    `
        : '';

    pag.innerHTML = `
      <span class="page-info">${total ? state.offset + 1 : 0}–${end} of ${total}</span>
      <div class="pagination-controls">
        <button type="button" class="btn btn-secondary" id="prevPage" ${prevDisabled ? 'disabled' : ''}>Previous</button>
        ${jumpBlock}
        <button type="button" class="btn btn-secondary" id="nextPage" ${nextDisabled ? 'disabled' : ''}>Next</button>
      </div>
    `;

    const prev = document.getElementById('prevPage');
    const next = document.getElementById('nextPage');
    if (prev && !prevDisabled) prev.onclick = () => { state.offset = Math.max(0, state.offset - state.limit); loadCatalog(); };
    if (next && !nextDisabled) next.onclick = () => { state.offset = state.offset + state.limit; loadCatalog(); };

    const pageInput = document.getElementById('catalogPageInput');
    const goBtn = document.getElementById('catalogPageGo');
    const applyPageJump = () => {
      const t = state.catalogTotal;
      const tp = t === 0 ? 0 : Math.ceil(t / state.limit);
      if (!pageInput || tp < 1) return;
      let p = parseInt(pageInput.value, 10);
      if (Number.isNaN(p)) p = 1;
      p = Math.max(1, Math.min(tp, p));
      state.offset = (p - 1) * state.limit;
      loadCatalog();
    };
    if (pageInput && goBtn) {
      goBtn.onclick = applyPageJump;
      pageInput.addEventListener('keydown', (ev) => {
        if (ev.key === 'Enter') {
          ev.preventDefault();
          applyPageJump();
        }
      });
    }
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
          await openProblemModal(id);
          if (document.getElementById('attempts')?.classList.contains('active')) loadAttempts();
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
        await openProblemModal(id);
        if (document.getElementById('attempts')?.classList.contains('active')) loadAttempts();
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

function buildAttemptsQuery() {
  const params = new URLSearchParams();
  if (state.attemptsTitle) params.set('title', state.attemptsTitle);
  if (state.attemptsTopic) params.set('topic', state.attemptsTopic);
  if (state.attemptsApproach) params.set('approach', state.attemptsApproach);
  return params.toString();
}

async function loadAttemptsTags() {
  const sel = document.getElementById('attemptsTopicFilter');
  const hint = document.getElementById('attemptsHint');
  if (!sel) return;
  try {
    const tags = await fetchJson(`${API}/catalog/tags`);
    sel.innerHTML = '<option value="">All topics</option>';
    tags.forEach((t) => {
      const opt = document.createElement('option');
      opt.value = t;
      opt.textContent = t;
      sel.appendChild(opt);
    });
    sel.value = state.attemptsTopic;
    hint.textContent = tags.length
      ? ''
      : 'Add topic tags in data/problem_topics.json to filter by topic.';
  } catch (e) {
    hint.textContent = '';
  }
}

function truncateText(s, max) {
  if (s == null || s === '') return '—';
  const t = String(s);
  if (t.length <= max) return t;
  return `${t.slice(0, max)}…`;
}

async function loadAttempts() {
  const tbody = document.getElementById('attemptsBody');
  if (!tbody) return;
  try {
    const q = buildAttemptsQuery();
    const rows = await fetchJson(`${API}/attempts${q ? `?${q}` : ''}`);
    if (rows.length === 0) {
      tbody.innerHTML =
        '<tr><td colspan="9" class="empty-cell">No attempts yet, or nothing matches your filters.</td></tr>';
      return;
    }
    tbody.innerHTML = rows
      .map((row) => {
        const a = row.attempt || {};
        const diff = (row.difficulty || '').toLowerCase();
        const diffClass =
          diff === 'easy' || diff === 'medium' || diff === 'hard' ? diff : '';
        const tags = (row.tags || [])
          .slice(0, 3)
          .map((t) => `<span class="tag-chip">${escapeHtml(t)}</span>`)
          .join(' ');
        const pid = row.problem_id;
        const approach = truncateText(a.approach || '', 100);
        return `
          <tr class="attempts-row catalog-row" data-id="${pid}" tabindex="0">
            <td class="mono text-muted">${escapeHtml(a.timestamp || '—')}</td>
            <td class="mono">${pid}</td>
            <td class="title-cell">${escapeHtml(row.title || '')}</td>
            <td><span class="difficulty ${diffClass}">${escapeHtml(row.difficulty || '')}</span></td>
            <td class="tags-cell">${tags || '<span class="text-muted">—</span>'}</td>
            <td class="mono">${escapeHtml(String(a.attempt ?? '—'))}</td>
            <td>${escapeHtml(a.time_spent || '—')}</td>
            <td class="approach-cell">${escapeHtml(approach)}</td>
            <td>${a.solved ? 'Yes' : 'No'}</td>
          </tr>`;
      })
      .join('');
    tbody.querySelectorAll('.attempts-row').forEach((r) => {
      const id = r.dataset.id;
      r.addEventListener('click', () => openProblemModal(id));
      r.addEventListener('keydown', (ev) => {
        if (ev.key === 'Enter' || ev.key === ' ') {
          ev.preventDefault();
          openProblemModal(id);
        }
      });
    });
  } catch (e) {
    tbody.innerHTML = `<tr><td colspan="9" class="empty-cell">Error: ${escapeHtml(e.message)}</td></tr>`;
  }
}

let attemptsDebounce;
function scheduleLoadAttempts() {
  clearTimeout(attemptsDebounce);
  attemptsDebounce = setTimeout(() => loadAttempts(), 300);
}

document.getElementById('attemptsTitleFilter').addEventListener('input', (e) => {
  state.attemptsTitle = e.target.value.trim();
  scheduleLoadAttempts();
});
document.getElementById('attemptsTopicFilter').addEventListener('change', (e) => {
  state.attemptsTopic = e.target.value;
  loadAttempts();
});
document.getElementById('attemptsApproachFilter').addEventListener('input', (e) => {
  state.attemptsApproach = e.target.value.trim();
  scheduleLoadAttempts();
});

function renderFastestRows(items, emptyLabel) {
  if (items.length === 0) return `<li>${emptyLabel}</li>`;
  return items
    .map((x) => `<li>${escapeHtml(x.title)} (#${x.id}) → ${x.minutes} min</li>`)
    .join('');
}

async function loadStats() {
  const emptyErr = (id, msg) => {
    const el = document.getElementById(id);
    if (el) el.innerHTML = `<li>${escapeHtml(msg)}</li>`;
  };
  try {
    const [easy, medium, hard, slowest] = await Promise.all([
      fetchJson(`${API}/stats/fastest?difficulty=easy`),
      fetchJson(`${API}/stats/fastest?difficulty=medium`),
      fetchJson(`${API}/stats/fastest?difficulty=hard`),
      fetchJson(`${API}/stats/slowest-categories`),
    ]);
    document.getElementById('fastestEasy').innerHTML = renderFastestRows(
      easy,
      'No easy problems with time data yet.',
    );
    document.getElementById('fastestMedium').innerHTML = renderFastestRows(
      medium,
      'No medium problems with time data yet.',
    );
    document.getElementById('fastestHard').innerHTML = renderFastestRows(
      hard,
      'No hard problems with time data yet.',
    );
    document.getElementById('slowestCategories').innerHTML =
      slowest.length === 0
        ? '<li>No topic data yet.</li>'
        : slowest.map((x) => `<li>${escapeHtml(x.category)}: ${x.avg_minutes} min (avg)</li>`).join('');
  } catch (e) {
    const msg = `Error: ${e.message}`;
    emptyErr('fastestEasy', msg);
    emptyErr('fastestMedium', msg);
    emptyErr('fastestHard', msg);
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
