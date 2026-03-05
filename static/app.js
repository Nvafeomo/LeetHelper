const API = '/api';

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

// Tabs
document.querySelectorAll('.tab').forEach((tab) => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.tab').forEach((t) => t.classList.remove('active'));
    document.querySelectorAll('.panel').forEach((p) => p.classList.remove('active'));
    tab.classList.add('active');
    document.getElementById(tab.dataset.tab).classList.add('active');
    if (tab.dataset.tab === 'problems') loadProblems();
    if (tab.dataset.tab === 'stats') loadStats();
  });
});

// Load problems
async function loadProblems(searchQuery = '') {
  const list = document.getElementById('problemsList');
  try {
    let problems;
    if (searchQuery) {
      problems = await fetchJson(`${API}/search?q=${encodeURIComponent(searchQuery)}`);
    } else {
      problems = await fetchJson(`${API}/problems`);
    }
    if (problems.length === 0) {
      list.innerHTML = '<div class="empty-state">No problems found. Add one to get started!</div>';
      return;
    }
    list.innerHTML = problems.map((p) => {
      const diff = (p.difficulty || '').toLowerCase();
      const diffClass = diff === 'easy' || diff === 'medium' || diff === 'hard' ? diff : '';
      return `
        <div class="problem-card" data-title="${escapeHtml(p.title)}">
          <div class="title">${escapeHtml(p.title)}</div>
          <div class="meta">
            <span class="difficulty ${diffClass}">${escapeHtml(p.difficulty)}</span>
            <span>${escapeHtml(p.category)}</span>
            <span>${(p.notes || []).length} note(s)</span>
          </div>
        </div>
      `;
    }).join('');
    list.querySelectorAll('.problem-card').forEach((card) => {
      card.addEventListener('click', () => openProblemModal(card.dataset.title));
    });
  } catch (e) {
    list.innerHTML = `<div class="empty-state">Error: ${e.message}</div>`;
  }
}

function escapeHtml(s) {
  if (!s) return '';
  const div = document.createElement('div');
  div.textContent = s;
  return div.innerHTML;
}

// Search
let searchTimeout;
document.getElementById('searchInput').addEventListener('input', (e) => {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => loadProblems(e.target.value.trim()), 300);
});

document.getElementById('refreshBtn').addEventListener('click', () => {
  document.getElementById('searchInput').value = '';
  loadProblems();
});

// Add problem form
document.getElementById('addForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const form = e.target;
  const data = {
    title: form.title.value.trim(),
    category: form.category.value.trim(),
    difficulty: form.difficulty.value,
    status: form.status.value,
    link: form.link.value.trim(),
    attempt: form.attempt.value.trim(),
    approach: form.approach.value.trim(),
    reflection: form.reflection.value.trim(),
    time_spent: form.time_spent.value.trim(),
  };
  try {
    await fetchJson(`${API}/problems`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
    showToast('Problem added!');
    form.reset();
    form.attempt.value = '1';
    document.querySelector('[data-tab="problems"]').click();
    loadProblems();
  } catch (err) {
    showToast(err.message, 'error');
  }
});

// Problem modal
async function openProblemModal(title) {
  const modal = document.getElementById('problemModal');
  const body = document.getElementById('modalBody');
  const problems = await fetchJson(`${API}/problems`);
  const p = problems.find((x) => x.title.toLowerCase() === title.toLowerCase());
  if (!p) {
    body.innerHTML = '<p>Problem not found.</p>';
    modal.classList.add('active');
    return;
  }
  const notes = p.notes || [];
  body.innerHTML = `
    <h2>${escapeHtml(p.title)}</h2>
    <div class="meta">
      <span class="difficulty ${(p.difficulty || '').toLowerCase()}">${escapeHtml(p.difficulty)}</span>
      · ${escapeHtml(p.category)} · ${escapeHtml(p.status)}
    </div>
    ${p.link ? `<a href="${escapeHtml(p.link)}" target="_blank" rel="noopener">View on LeetCode</a>` : ''}
    <div class="notes-section">
      <h4>Reflection Notes</h4>
      ${notes.length === 0 ? '<p class="text-muted">No notes yet.</p>' : ''}
      ${notes.map((n) => `
        <div class="note-item" data-attempt="${escapeHtml(String(n.attempt))}">
          <div class="note-meta">Attempt ${escapeHtml(String(n.attempt))} · ${escapeHtml(n.timestamp || '')}</div>
          <div><strong>${escapeHtml(n.approach || '')}</strong></div>
          <div>${escapeHtml(n.reflection || '')}</div>
          <div>Time: ${escapeHtml(n.time_spent || '')}</div>
          <button class="btn btn-danger delete-note-btn" data-attempt="${escapeHtml(String(n.attempt))}">Delete note</button>
        </div>
      `).join('')}
    </div>
    <div class="add-note-form">
      <h4>Add Note</h4>
      <input type="text" name="attempt" placeholder="Attempt number" value="${notes.length + 1}">
      <input type="text" name="approach" placeholder="Approach used">
      <textarea name="reflection" placeholder="Reflection" rows="2"></textarea>
      <input type="text" name="time_spent" placeholder="Time spent (e.g. 30 minutes)">
      <button type="button" class="btn btn-primary add-note-btn">Add Note</button>
    </div>
    <div style="margin-top:1rem">
      <button class="btn btn-danger delete-problem-btn">Delete Problem</button>
    </div>
  `;
  body.querySelectorAll('.delete-note-btn').forEach((btn) => {
    btn.addEventListener('click', async () => {
      if (!confirm('Delete this note?')) return;
      try {
        await fetchJson(`${API}/problems/${encodeURIComponent(p.title)}/notes/${encodeURIComponent(btn.dataset.attempt)}`, { method: 'DELETE' });
        showToast('Note deleted');
        openProblemModal(p.title);
      } catch (err) {
        showToast(err.message, 'error');
      }
    });
  });
  body.querySelector('.add-note-btn').addEventListener('click', async () => {
    const form = body.querySelector('.add-note-form');
    const note = {
      attempt: form.querySelector('[name="attempt"]').value.trim(),
      approach: form.querySelector('[name="approach"]').value.trim(),
      reflection: form.querySelector('[name="reflection"]').value.trim(),
      time_spent: form.querySelector('[name="time_spent"]').value.trim(),
    };
    if (!note.attempt || !note.approach || !note.time_spent) {
      showToast('Fill in attempt, approach, and time spent', 'error');
      return;
    }
    try {
      await fetchJson(`${API}/problems/${encodeURIComponent(p.title)}/notes`, {
        method: 'POST',
        body: JSON.stringify(note),
      });
      showToast('Note added!');
      openProblemModal(p.title);
    } catch (err) {
      showToast(err.message, 'error');
    }
  });
  body.querySelector('.delete-problem-btn').addEventListener('click', async () => {
    if (!confirm(`Delete "${p.title}"?`)) return;
    try {
      await fetchJson(`${API}/problems/${encodeURIComponent(p.title)}`, { method: 'DELETE' });
      showToast('Problem deleted');
      modal.classList.remove('active');
      loadProblems();
    } catch (err) {
      showToast(err.message, 'error');
    }
  });
  modal.classList.add('active');
}

document.querySelector('.modal-close').addEventListener('click', () => {
  document.getElementById('problemModal').classList.remove('active');
});

document.getElementById('problemModal').addEventListener('click', (e) => {
  if (e.target.id === 'problemModal') e.target.classList.remove('active');
});

// Stats
async function loadStats() {
  try {
    const [fastest, slowest] = await Promise.all([
      fetchJson(`${API}/stats/fastest-hard`),
      fetchJson(`${API}/stats/slowest-categories`),
    ]);
    const fastestEl = document.getElementById('fastestHard');
    const slowestEl = document.getElementById('slowestCategories');
    fastestEl.innerHTML = fastest.length === 0
      ? '<li>No hard problems with time data yet.</li>'
      : fastest.map((x) => `<li>${escapeHtml(x.title)} → ${x.minutes} min</li>`).join('');
    slowestEl.innerHTML = slowest.length === 0
      ? '<li>No category data yet.</li>'
      : slowest.map((x) => `<li>${escapeHtml(x.category)}: ${x.avg_minutes} min (avg)</li>`).join('');
  } catch (e) {
    document.getElementById('fastestHard').innerHTML = `<li>Error: ${e.message}</li>`;
    document.getElementById('slowestCategories').innerHTML = '';
  }
}

document.getElementById('loadStatsBtn').addEventListener('click', async () => {
  const title = document.getElementById('statsProblemTitle').value.trim();
  if (!title) {
    showToast('Enter a problem title', 'error');
    return;
  }
  const el = document.getElementById('timeStats');
  try {
    const stats = await fetchJson(`${API}/stats/time/${encodeURIComponent(title)}`);
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

// Init
loadProblems();
