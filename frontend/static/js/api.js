/**
 * api.js — Helper Fetch centralisé + utilitaires UI
 */

const API = {
  async request(method, url, body = null) {
    const opts = {
      method,
      headers: { 'Content-Type': 'application/json' },
      credentials: 'same-origin',
    };
    if (body !== null) opts.body = JSON.stringify(body);
    const res  = await fetch(url, opts);
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.erreur || 'Erreur serveur');
    return data;
  },
  get:    (url)        => API.request('GET',    url),
  post:   (url, body)  => API.request('POST',   url, body),
  put:    (url, body)  => API.request('PUT',    url, body),
  delete: (url)        => API.request('DELETE', url),
};

// ── Toast ────────────────────────────────────────────────────
function toast(msg, type = 'success') {
  let el = document.querySelector('.toast');
  if (!el) {
    el = document.createElement('div');
    el.className = 'toast';
    document.body.appendChild(el);
  }
  el.textContent = msg;
  el.className = `toast ${type} show`;
  clearTimeout(el._t);
  el._t = setTimeout(() => el.classList.remove('show'), 3200);
}

// ── Auth guard ───────────────────────────────────────────────
async function checkAuth() {
  try {
    return await API.get('/api/auth/moi');
  } catch {
    window.location.href = '/connexion';
    return null;
  }
}

// ── Utilitaires ──────────────────────────────────────────────
function initiales(prenom, nom) {
  return ((prenom?.[0] || '') + (nom?.[0] || '')).toUpperCase();
}

function couleurAv(role) {
  return role === 'tuteur'
    ? 'background:rgba(124,110,247,0.2);color:#a89ef9'
    : 'background:rgba(62,207,170,0.15);color:#3ecfaa';
}

function formatDate(iso, opts = {}) {
  return new Date(iso).toLocaleString('fr-FR', {
    weekday: 'short', day: 'numeric', month: 'short',
    hour: '2-digit', minute: '2-digit',
    ...opts,
  });
}
