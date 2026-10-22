/* Hobson visuals — drop-in. Watches the DOM the page already renders and adds:
   - a You → Decider → Nova flow strip that lights up per turn (and animates "not sure" hand-offs),
   - count-up confidence numbers, a 60% tick on every bar,
   - danger pips (red at 4–5), a Lite/Pro route pill,
   - a red flash on the ledger when a claim fails the ledger check, green when it passes.
   No data is invented here: everything is read from the rows the server returned. */
(function () {
  const $ = (s, r) => (r || document).querySelector(s);
  const rows = $('#rows'), story = $('#story'), ledger = $('#ledger');
  if (!rows || !story) return;

  // ---------- flow strip ----------
  const flow = document.createElement('div');
  flow.id = 'hv-flow';
  flow.innerHTML = `
    <div class="node" data-n="you"><b>You</b><small>free text</small></div>
    <div class="arrow dec"><span class="dot"></span></div>
    <div class="node" data-n="decider"><b>Decider 2B</b><small>rules · on this Mac</small></div>
    <div class="arrow"><span class="dot"></span></div>
    <div class="node" data-n="nova"><b>Nova</b><small>writes · on Bedrock</small></div>
    <div class="legend"><span><i style="background:#68c478"></i>sure, Decider's call</span><span><i style="background:#ecab46"></i>not sure, handed to Nova</span></div>`;
  rows.parentNode.insertBefore(flow, rows);
  const node = n => flow.querySelector(`.node[data-n="${n}"]`);
  const arrows = flow.querySelectorAll('.arrow');
  const setNodes = (cls, ...names) => { flow.querySelectorAll('.node').forEach(e => e.classList.remove('lit', 'busy', 'amber', 'red')); names.forEach(n => node(n).classList.add(cls)); };
  function travel(i) { const d = arrows[i].querySelector('.dot'); d.classList.remove('go'); void d.offsetWidth; d.classList.add('go'); }

  // ---------- count-up for the % in .conf ----------
  function countUp(el) {
    const m = el.textContent.match(/(\d+)%/); if (!m) return;
    const target = +m[1], prefix = el.textContent.slice(0, m.index), t0 = performance.now(), dur = 900;
    const tick = now => {
      const k = Math.min(1, (now - t0) / dur), v = Math.round(target * (1 - Math.pow(1 - k, 3)));
      el.textContent = `${prefix}${v}%`; if (k < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }

  // ---------- per-row decoration ----------
  function decorate(row) {
    if (row.dataset.hv) return; row.dataset.hv = '1';
    const q = ($('.q', row) || {}).textContent || '', a = $('.a', row), conf = $('.conf', row);
    if (conf) countUp(conf);
    if (/true in the story/i.test(q) && a) {
      const bad = /^No\b/.test(a.textContent);
      const tag = document.createElement('span'); tag.className = 'hv-tag ' + (bad ? 'bad' : 'ok');
      tag.textContent = bad ? 'not in the ledger' : 'ledger agrees'; a.appendChild(tag);
      if (ledger) { ledger.classList.remove('hv-flash', 'hv-check'); void ledger.offsetWidth; ledger.classList.add(bad ? 'hv-flash' : 'hv-check'); }
    }
    if (/dangerous/i.test(q) && a) {
      const m = a.textContent.match(/(\d)\s*of\s*5/); if (m) {
        const n = +m[1], pips = document.createElement('span'); pips.className = 'hv-pips' + (n >= 4 ? ' hot' : '');
        for (let i = 0; i < 5; i++) { const p = document.createElement('i'); pips.appendChild(p); setTimeout(() => { if (i < n) p.classList.add('on'); }, 120 + i * 110); }
        a.appendChild(pips);
        if (n >= 4) node('nova').classList.add('red');
      }
    }
    if (/keep to the facts/i.test(q) && a) {
      const broke = /^No\b/.test(a.textContent);
      const tag = document.createElement('span'); tag.className = 'hv-tag ' + (broke ? 'bad' : 'ok');
      tag.textContent = broke ? 'caught by the guard' : 'checked against the ledger'; a.appendChild(tag);
      if (broke && ledger) { ledger.classList.remove('hv-flash', 'hv-check'); void ledger.offsetWidth; ledger.classList.add('hv-flash'); }
    }
    if (/who writes/i.test(q) && a) {
      const pro = /pro/i.test(a.textContent), pill = document.createElement('span');
      pill.className = 'hv-route ' + (pro ? 'pro' : 'lite'); pill.textContent = pro ? 'stronger writer' : 'faster writer'; a.appendChild(pill);
    }
    if (row.classList.contains('unsure')) { node('nova').classList.add('amber'); travel(1); }
  }

  // ---------- observers ----------
  let turnOpen = false;
  new MutationObserver(muts => {
    for (const m of muts) for (const n of m.addedNodes) if (n.nodeType === 1 && n.classList.contains('row')) {
      if (!turnOpen) { turnOpen = true; setNodes('lit', 'decider'); travel(0); }
      // rows get class "in" ~30 ms after insertion; decorate once visible so the bar animation is seen
      setTimeout(() => decorate(n), 40);
    }
    if (!rows.children.length) turnOpen = false;
  }).observe(rows, { childList: true });

  new MutationObserver(muts => {
    for (const m of muts) for (const n of m.addedNodes) {
      if (n.nodeType !== 1) continue;
      if (n.classList.contains('thinking')) {
        if (/^Nova/.test(n.textContent)) { setNodes('busy', 'nova'); }
        else { setNodes('busy', 'decider'); node('you').classList.add('lit'); travel(0); }
      }
      else if (n.tagName === 'P' && !n.classList.contains('you') && !n.classList.contains('scene') && turnOpen) {
        // the narration paragraph landed: Nova wrote
        node('nova').classList.add('lit'); turnOpen = false;
      }
    }
  }).observe(story, { childList: true });

  // opening state
  setNodes('lit', 'nova');
})();
