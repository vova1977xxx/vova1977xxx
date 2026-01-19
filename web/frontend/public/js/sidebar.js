(function () {
  const el = document.getElementById('sidebar');
  if (!el) return;

  function item(icon, label, href) {
    return `
      <a class="gv-nav-item" href="${href}">
        <span class="gv-nav-ic">${icon}</span>
        <span class="gv-nav-tx">${label}</span>
      </a>
    `;
  }

  const user = localStorage.getItem('gv_user') || '';
  const status = user ? 'user' : 'guest';

  el.innerHTML = `
    <div class="gv-brand">GEMIVAS</div>

    <div class="gv-status">status: <b>${status}</b></div>

    <nav class="gv-nav">
      ${item('🎬','Feed','/feed/')}
      ${item('📻','Radio','/radio/')}
      ${item('📰','News','/news/')}
      ${item('🌦','Weather','/weather/')}
      ${item('🎵','Music','/music/')}
      ${item('💬','Chat','/chat/')}
      ${item('💎','Donate','/donate/')}
    </nav>

    <div class="gv-auth">
      ${user ? `<a class="gv-nav-item" href="/profile/">⚙️ Profile</a>` : `
        <a class="gv-nav-item" href="/login/">Login</a>
        <a class="gv-nav-item" href="/register/">Register</a>
      `}
    </div>
  `;
})();
