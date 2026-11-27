/* archdeck — deck.js: fit-to-screen stage, step reveals, keyboard nav,
   speaker notes, recording mode. No dependencies; works from file://.

   Keys  → Space PgDn Enter  next step     ← PgUp Backspace  previous step
         ↓ / ↑  next / previous slide      Home / End        first / last
         12 Enter  jump to slide 12        R  replay current step
         F fullscreen   N notes   C clean (recording) mode   T light/dark
   URL   #/3/2 = slide 3, step 2 (#/3/99 clamps to its last step)
         ?clean  recording mode   ?theme=dark   ?motion  ignore reduced-motion
   API   window.archdeck.go(slideIndex, step) / .next() / .prev() / .state()
*/
(() => {
  'use strict';
  const W = 1920, H = 1080;
  const root = document.documentElement;
  const deck = document.querySelector('.deck');
  if (!deck) return;
  const slides = Array.from(deck.querySelectorAll(':scope > .slide'));
  if (!slides.length) return;

  const params = new URLSearchParams(location.search);
  if (params.has('clean')) root.classList.add('is-clean');
  if (params.get('theme')) root.dataset.theme = params.get('theme');
  if (params.has('motion')) root.classList.add('force-motion');
  const lang = root.lang || 'vi';

  const int = (v, d) => { const n = parseInt(v, 10); return Number.isFinite(n) ? n : d; };
  const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));
  const stepped = (slide) => Array.from(slide.querySelectorAll('[data-step], [data-out]'))
    .filter((el) => !el.closest('.notes'));
  const lastStep = slides.map((slide) => stepped(slide)
    .reduce((m, el) => Math.max(m, int(el.dataset.step, 0), int(el.dataset.out, 0)), 0));

  // Shared SVG arrowheads: marker-end="url(#ad-arrow)" (or -problem/-fix/-info/-focus/-muted).
  const tones = { '': 'var(--ink-2)', '-problem': 'var(--problem)', '-fix': 'var(--fix)',
    '-info': 'var(--info)', '-focus': 'var(--focus)', '-muted': 'var(--line-strong)' };
  const defs = Object.entries(tones).map(([s, c]) =>
    `<marker id="ad-arrow${s}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" ` +
    `orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" style="fill:${c}"/></marker>`).join('');
  document.body.insertAdjacentHTML('afterbegin',
    `<svg aria-hidden="true" style="position:absolute;width:0;height:0;overflow:hidden"><defs>${defs}</defs></svg>`);

  // Title block: deck name · step ticks · sheet number. build.py stamps
  // data-sheet="n/total" so a standalone slide file shows its real number.
  const pad = (n) => String(n).padStart(2, '0');
  const deckTitle = deck.dataset.title || document.title;
  slides.forEach((sl, k) => {
    const [n, total] = (sl.dataset.sheet || `${k + 1}/${slides.length}`).split('/');
    sl.querySelectorAll('[data-slide-num]').forEach((el) => { el.textContent = `${n}/${total}`; });
    if (sl.querySelector(':scope > .sheet')) return;
    const sheet = document.createElement('footer');
    sheet.className = 'sheet';
    sheet.innerHTML = `<span class="sheet-deck"></span><span class="sheet-ticks">${'<i></i>'.repeat(lastStep[k])}</span>` +
      `<span class="sheet-no">Tờ <b>${pad(n)}</b> / ${pad(total)}</span>`;
    sheet.querySelector('.sheet-deck').textContent = deckTitle;
    if (root.lang && !root.lang.startsWith('vi')) sheet.querySelector('.sheet-no').firstChild.textContent = 'Sheet ';
    sl.append(sheet);
  });

  const progress = document.createElement('div');
  progress.className = 'deck-progress';
  progress.innerHTML = '<i></i>';
  const count = document.createElement('div');
  count.className = 'deck-count';
  const notes = document.createElement('aside');
  notes.className = 'deck-notes';
  document.body.append(progress, count, notes);

  let cur = 0, step = 0;

  function fit() {
    root.style.setProperty('--scale', Math.min(innerWidth / W, innerHeight / H));
  }

  // .a-count: counts data-from → data-to (decimals: data-decimals, ms: data-ms).
  function countUp(el, on, instant) {
    const dec = int(el.dataset.decimals, 0);
    const fmt = new Intl.NumberFormat(lang, { minimumFractionDigits: dec, maximumFractionDigits: dec });
    const from = parseFloat(el.dataset.from || '0'), to = parseFloat(el.dataset.to || '0');
    cancelAnimationFrame(el._raf);
    if (!on) { el._done = false; el.textContent = fmt.format(from); return; }
    if (el._done) return;
    el._done = true;
    if (instant) { el.textContent = fmt.format(to); return; }
    const dur = int(el.dataset.ms, 1200), t0 = performance.now();
    const tick = (t) => {
      const p = Math.min(1, (t - t0) / dur), e = 1 - Math.pow(1 - p, 3);
      el.textContent = fmt.format(from + (to - from) * e);
      if (p < 1) el._raf = requestAnimationFrame(tick);
    };
    el._raf = requestAnimationFrame(tick);
  }

  function renderNotes(slide) {
    const ps = Array.from(slide.querySelectorAll('.notes [data-step], .notes > p'));
    const seen = new Set();
    const html = ps.filter((p) => !seen.has(p) && seen.add(p)).map((p) => {
      const at = int(p.dataset.step, 0);
      if (at > step) return '';
      return `<p class="${at === step ? 'now' : ''}">${p.innerHTML}</p>`;
    }).join('');
    const title = slide.querySelector('.title');
    notes.innerHTML = `<div class="meta">${cur + 1}/${slides.length} · step ${step}/${lastStep[cur]}` +
      `${title ? ' · ' + title.textContent.trim() : ''}</div>${html || '<p class="now">—</p>'}`;
  }

  function render(i, s, instant) {
    cur = clamp(i, 0, slides.length - 1);
    step = clamp(s, 0, lastStep[cur]);
    if (instant) root.classList.add('no-anim');
    slides.forEach((sl, k) => sl.classList.toggle('is-active', k === cur));
    const slide = slides[cur];
    for (const el of stepped(slide)) {
      const at = int(el.dataset.step, 0), out = int(el.dataset.out, Infinity);
      const on = step >= at && step < out;
      el.classList.toggle('is-on', on);
      el.classList.toggle('is-current', on && at > 0 && at === step);
      if (el.classList.contains('a-count')) countUp(el, on, instant);
    }
    slide.dataset.at = step;
    slide.querySelectorAll(':scope > .sheet .sheet-ticks i').forEach((t, k) => t.classList.toggle('on', k < step));
    const total = slides.length;
    progress.style.setProperty('--p', `${((cur + (lastStep[cur] ? step / (lastStep[cur] + 1) : 0)) / total) * 100}%`);
    count.textContent = `${cur + 1} / ${total}${lastStep[cur] ? ` · ${step}/${lastStep[cur]}` : ''}`;
    renderNotes(slide);
    history.replaceState(null, '', `#/${cur + 1}/${step}`);
    if (instant) requestAnimationFrame(() => requestAnimationFrame(() => root.classList.remove('no-anim')));
  }

  const next = () => (step < lastStep[cur] ? render(cur, step + 1) : cur < slides.length - 1 && render(cur + 1, 0, true));
  const prev = () => (step > 0 ? render(cur, step - 1) : cur > 0 && render(cur - 1, lastStep[cur - 1], true));
  const go = (i, s = 0) => render(i, s, true);
  function replay() {
    const s = step;
    render(cur, Math.max(0, s - 1), true);
    requestAnimationFrame(() => requestAnimationFrame(() => render(cur, s)));
  }
  function fromHash() {
    const m = location.hash.match(/^#\/(\d+)(?:\/(\d+))?/);
    if (m) go(int(m[1], 1) - 1, int(m[2], 0));
    else go(0, 0);
  }

  let typed = '';
  addEventListener('keydown', (e) => {
    if (e.metaKey || e.ctrlKey || e.altKey) return;
    const k = e.key;
    if (/^\d$/.test(k)) { typed += k; return; }
    if (k === 'Enter' && typed) { go(int(typed, 1) - 1, 0); typed = ''; e.preventDefault(); return; }
    typed = '';
    const actions = {
      ArrowRight: next, PageDown: next, ' ': next, Enter: next,
      ArrowLeft: prev, PageUp: prev, Backspace: prev,
      ArrowDown: () => go(cur + 1, 0), ArrowUp: () => go(cur - 1, 0),
      Home: () => go(0, 0), End: () => go(slides.length - 1, 0),
      r: replay, R: replay,
      f: () => (document.fullscreenElement ? document.exitFullscreen() : root.requestFullscreen()),
      n: () => root.classList.toggle('show-notes'),
      c: () => root.classList.toggle('is-clean'),
      t: () => { root.dataset.theme = root.dataset.theme === 'dark' ? 'light' : 'dark'; },
    };
    const act = actions[k] || actions[k.toLowerCase()];
    if (act) { e.preventDefault(); act(); }
  });
  deck.addEventListener('click', (e) => {
    if (e.target.closest('a, button, input, select, textarea') || String(getSelection())) return;
    next();
  });
  addEventListener('resize', fit);
  addEventListener('hashchange', () => {
    const m = location.hash.match(/^#\/(\d+)(?:\/(\d+))?/);
    if (m && (int(m[1], 1) - 1 !== cur || int(m[2], 0) !== step)) fromHash();
  });

  window.archdeck = { go, next, prev, replay, state: () => ({ slide: cur, step, last: lastStep[cur], total: slides.length }) };
  fit();
  fromHash();
})();
