/* Edmonton-region news prototype — small progressive enhancements.
   Without JavaScript the pages still work: the nav shows as a plain list,
   desktop menus open on hover, and the search form is always visible. */
(() => {
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];
  const body = document.body;
  const root = document.documentElement;
  const mqMobile = window.matchMedia('(max-width: 1000px)'); // keep in sync with styles.css
  const onMqChange = (fn) => (mqMobile.addEventListener ? mqMobile.addEventListener('change', fn) : mqMobile.addListener(fn));
  const isShown = (el) => !!el && el.offsetParent !== null;
  const header = $('.site-header');

  /* Keep anchor jumps and focused elements clear of the sticky header. */
  const setScrollPad = () => { if (header) root.style.scrollPaddingTop = `${header.offsetHeight + 16}px`; };
  setScrollPad();
  window.addEventListener('resize', setScrollPad);

  /* ---------- Dropdown menus (desktop row + mobile accordion) ---------- */
  const nav = $('#primary-nav');
  const menuButtons = $$('.nav-item > button[aria-expanded]:not([data-search-toggle])');
  const closeMenus = (except) => menuButtons.forEach((b) => { if (b !== except) b.setAttribute('aria-expanded', 'false'); });

  menuButtons.forEach((btn) => {
    const item = btn.parentElement;
    btn.addEventListener('click', () => {
      const open = btn.getAttribute('aria-expanded') === 'true';
      if (!mqMobile.matches) closeMenus(btn);
      btn.setAttribute('aria-expanded', String(!open));
    });
    // Desktop: pointing at another section closes a menu that was opened by click…
    item.addEventListener('mouseenter', () => { if (!mqMobile.matches) closeMenus(btn); });
    // …and tabbing out of a section closes its menu.
    item.addEventListener('focusout', (e) => {
      if (mqMobile.matches || item.contains(e.relatedTarget)) return;
      btn.setAttribute('aria-expanded', 'false');
    });
  });

  document.addEventListener('click', (e) => {
    if (!mqMobile.matches && !e.target.closest('.nav-item')) closeMenus();
  });
  if (nav) nav.addEventListener('mouseleave', () => nav.classList.remove('hover-off'));

  /* ---------- Mobile drawer ---------- */
  const menuToggle = $('.menu-toggle');
  const backdrop = $('.nav-backdrop');
  const navClose = $('.nav-close');
  const drawerOpen = () => body.classList.contains('nav-open');
  const behindDrawer = () => ['.header-top', '#search-panel', '.page', '.site-footer', '.preview-bar', '.skip-link']
    .map((s) => $(s)).filter(Boolean);

  function openDrawer() {
    body.classList.add('nav-open');
    menuToggle.setAttribute('aria-expanded', 'true');
    backdrop.hidden = false;
    behindDrawer().forEach((el) => el.setAttribute('inert', ''));
    (navClose || $('a, button', nav)).focus();
  }
  function closeDrawer({ restoreFocus = true } = {}) {
    body.classList.remove('nav-open');
    menuToggle.setAttribute('aria-expanded', 'false');
    backdrop.hidden = true;
    behindDrawer().forEach((el) => el.removeAttribute('inert'));
    if (restoreFocus && isShown(menuToggle)) menuToggle.focus();
  }

  if (nav && menuToggle && backdrop) {
    menuToggle.addEventListener('click', () => (drawerOpen() ? closeDrawer() : openDrawer()));
    backdrop.addEventListener('click', () => closeDrawer());
    if (navClose) navClose.addEventListener('click', () => closeDrawer());
    onMqChange(() => {
      if (!mqMobile.matches && drawerOpen()) closeDrawer({ restoreFocus: false });
      closeMenus();
      setScrollPad();
    });
    // Belt and braces: keep Tab inside the open drawer even where `inert` is unsupported.
    nav.addEventListener('keydown', (e) => {
      if (e.key !== 'Tab' || !drawerOpen()) return;
      const items = $$('a[href], button:not([disabled])', nav).filter(isShown);
      const first = items[0];
      const last = items[items.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    });
  }

  /* ---------- Search panel ---------- */
  const searchPanel = $('#search-panel');
  const searchButtons = $$('[data-search-toggle]');
  const searchStatus = searchPanel ? $('.search-status', searchPanel) : null;

  function toggleSearch(force) {
    if (!searchPanel) return;
    const show = typeof force === 'boolean' ? force : searchPanel.hidden;
    const hadFocus = searchPanel.contains(document.activeElement);
    searchPanel.hidden = !show;
    searchButtons.forEach((b) => b.setAttribute('aria-expanded', String(show)));
    setScrollPad();
    if (show) {
      if (searchStatus) searchStatus.textContent = '';
      $('input', searchPanel).focus();
    } else if (hadFocus) {
      const toggle = searchButtons.find(isShown);
      if (toggle) toggle.focus();
    }
  }
  searchButtons.forEach((b) => b.addEventListener('click', () => toggleSearch()));
  if (searchPanel) {
    $('form', searchPanel).addEventListener('submit', (e) => {
      e.preventDefault();
      if (searchStatus) searchStatus.textContent = 'Search isn’t connected in this design preview.';
    });
  }

  /* ---------- Escape closes whatever is open ---------- */
  document.addEventListener('keydown', (e) => {
    if (e.key !== 'Escape') return;
    if (drawerOpen()) { closeDrawer(); return; }
    const openBtn = menuButtons.find((b) => b.getAttribute('aria-expanded') === 'true');
    if (openBtn) { closeMenus(); openBtn.focus(); return; }
    if (nav && !mqMobile.matches && nav.matches(':hover')) { nav.classList.add('hover-off'); return; }
    if (searchPanel && !searchPanel.hidden) toggleSearch(false);
  });

  /* ---------- Community poll (sample results, nothing is recorded) ---------- */
  $$('form.poll').forEach((form) => {
    const out = $('.poll-results', form);
    const note = $('.poll-note', form);
    const fieldset = $('fieldset', form);
    const voteBtn = $('[data-vote]', form);
    const resultsBtn = $('[data-show-results]', form);
    if (!out || !note || !fieldset || !voteBtn) return;
    let data = {};
    try { data = JSON.parse(form.dataset.results || '{}'); } catch { data = {}; }
    const resultsLabel = resultsBtn ? resultsBtn.innerHTML : '';
    let voted = null;

    const renderBars = () => {
      const counts = { ...data };
      if (voted) counts[voted] = (counts[voted] || 0) + 1;
      const total = Object.values(counts).reduce((a, b) => a + b, 0) || 1;
      out.replaceChildren();
      Object.entries(counts).forEach(([label, n]) => {
        const pct = Math.round((n / total) * 100);
        const li = document.createElement('li');
        const row = document.createElement('span');
        row.className = 'row-label';
        const name = document.createElement('span');
        name.textContent = label;
        const val = document.createElement('span');
        val.textContent = `${pct}%`;
        row.append(name, val);
        const bar = document.createElement('span');
        bar.className = 'bar';
        bar.setAttribute('aria-hidden', 'true');
        const fill = document.createElement('span');
        fill.style.width = `${pct}%`;
        bar.append(fill);
        li.append(row, bar);
        out.append(li);
      });
    };
    const showResults = () => {
      renderBars();
      out.hidden = false;
      fieldset.hidden = true;
      voteBtn.hidden = true;
      if (resultsBtn) {
        if (voted) resultsBtn.hidden = true;
        else resultsBtn.textContent = 'Back to poll';
      }
    };
    const showPoll = () => {
      out.hidden = true;
      fieldset.hidden = false;
      voteBtn.hidden = false;
      if (resultsBtn) resultsBtn.innerHTML = resultsLabel;
      note.textContent = '';
    };

    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const picked = new FormData(form).get('vote');
      if (!picked) { note.textContent = 'Choose an option first.'; return; }
      voted = String(picked);
      showResults();
      note.textContent = 'Thanks for voting. These are sample results — this preview doesn’t record votes.';
      out.focus();
    });

    if (resultsBtn) {
      resultsBtn.addEventListener('click', () => {
        if (!out.hidden) {
          showPoll();
          const first = $('input', fieldset);
          if (first) first.focus();
          return;
        }
        showResults();
        note.textContent = 'Sample results.';
      });
    }
  });

  /* ---------- Newsletter cards: the name stays "Add", the pressed state carries the change ---------- */
  $$('.nl-card .btn').forEach((btn) => {
    const label = document.createElement('span');
    label.textContent = btn.textContent.trim();
    const done = document.createElement('span');
    done.textContent = 'Added ✓';
    done.setAttribute('aria-hidden', 'true');
    done.hidden = true;
    btn.replaceChildren(label, done);
    btn.addEventListener('click', () => {
      const on = btn.getAttribute('aria-pressed') !== 'true';
      btn.setAttribute('aria-pressed', String(on));
      label.className = on ? 'sr-only' : '';
      done.hidden = !on;
    });
  });

  $$('.nl-wrap').forEach((wrap) => {
    const track = $('.nl-track', wrap);
    const prev = $('.nl-arrow.prev', wrap);
    const next = $('.nl-arrow.next', wrap);
    if (!track || !prev || !next) return;
    const step = () => track.clientWidth / 2 + 8;
    const update = () => {
      const atStart = track.scrollLeft < 10;
      const atEnd = track.scrollLeft + track.clientWidth >= track.scrollWidth - 10;
      // Don't strand keyboard focus on an arrow that is about to disappear.
      if (atStart && document.activeElement === prev) (atEnd ? track : next).focus();
      if (atEnd && document.activeElement === next) (atStart ? track : prev).focus();
      prev.disabled = atStart;
      next.disabled = atEnd;
    };
    prev.addEventListener('click', () => track.scrollBy({ left: -step() }));
    next.addEventListener('click', () => track.scrollBy({ left: step() }));
    track.addEventListener('scroll', update, { passive: true });
    window.addEventListener('resize', update);
    update();
  });

  /* ---------- Article: share ---------- */
  const shareStatus = $('[data-share-status]');
  let shareTimer = null;
  const sayShare = (msg) => {
    if (!shareStatus) return;
    shareStatus.textContent = msg;
    clearTimeout(shareTimer);
    shareTimer = setTimeout(() => { shareStatus.textContent = ''; }, 2500);
  };
  $$('[data-share]').forEach((btn) => {
    btn.addEventListener('click', async () => {
      if (navigator.share) {
        try { await navigator.share({ title: document.title, url: location.href }); } catch { /* user cancelled */ }
        return;
      }
      try { await navigator.clipboard.writeText(location.href); sayShare('Link copied'); }
      catch { sayShare('Couldn’t copy — use the address bar link'); }
    });
  });

  /* ---------- Article: listen (placeholder player with a working timer) ---------- */
  $$('[data-listen]').forEach((wrap) => {
    const btn = $('.listen-btn', wrap);
    const label = $('.listen-label', wrap);
    const time = $('.listen-time', wrap);
    if (!btn || !label || !time) return;
    const totalText = time.dataset.total || time.textContent.trim();
    const total = totalText.split(':').reduce((acc, n) => acc * 60 + Number(n), 0) || 0;
    const fmt = (s) => [Math.floor(s / 3600), Math.floor(s / 60) % 60, s % 60].map((n) => String(n).padStart(2, '0')).join(':');
    const icon = $('use', btn);
    let secs = 0;
    let timer = null;

    const stop = (finished) => {
      clearInterval(timer);
      timer = null;
      btn.setAttribute('aria-pressed', 'false');
      if (icon) icon.setAttribute('href', '#i-play');
      label.textContent = 'Listen to this article';
      if (finished) { secs = 0; time.textContent = totalText; }
    };
    btn.addEventListener('click', () => {
      if (timer) { stop(false); return; }
      btn.setAttribute('aria-pressed', 'true');
      if (icon) icon.setAttribute('href', '#i-pause');
      label.textContent = 'Playing (audio placeholder)';
      timer = setInterval(() => {
        secs += 1;
        if (total && secs >= total) { stop(true); return; }
        time.textContent = `${fmt(secs)} / ${totalText}`;
      }, 1000);
    });
  });

  /* ---------- Footer year ---------- */
  $$('[data-year]').forEach((el) => { el.textContent = String(new Date().getFullYear()); });
})();
