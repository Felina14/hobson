/* Hobson visuals. Three things the ruling log could not show at a glance:
     1. the verdict  — was this turn allowed in, and did anything reach the ledger
     2. the claims   — what the action relied on, and which of it the record actually holds
     3. the timeline — the whole story's integrity so far, one column per turn
   Everything here is read from the turn payload the server returned. Nothing is invented. */
(function () {
  const $ = s => document.querySelector(s);
  const el = (t, c, x) => { const e = document.createElement(t); if (c) e.className = c; if (x != null) e.textContent = x; return e; };
  const V = $('#hv-verdict'), C = $('#hv-claims'), TL = $('#hv-timeline'), rows = $('#rows'), story = $('#story');
  if (!V) return;
  const turns = [];

  // ---------- flow strip: who is doing what, right now ----------
  const flow = el('div'); flow.id = 'hv-flow';
  flow.innerHTML = `
    <div class="node" data-n="you"><b>You</b><small>free text</small></div>
    <div class="arrow"><span class="dot"></span></div>
    <div class="node" data-n="decider"><b>Decider 2B</b><small>decides what is true<br>on this Mac</small></div>
    <div class="arrow"><span class="dot"></span></div>
    <div class="node" data-n="nova"><b>Nova</b><small>writes the prose<br>on Bedrock</small></div>`;
  V.parentNode.insertBefore(flow, V);
  const node = n => flow.querySelector(`.node[data-n="${n}"]`);
  const lit = (...names) => { flow.querySelectorAll('.node').forEach(e => e.className = 'node'); names.forEach(n => node(n).classList.add('lit')); };
  const travel = i => { const d = flow.querySelectorAll('.arrow')[i].querySelector('.dot'); d.classList.remove('go'); void d.offsetWidth; d.classList.add('go'); };

  // ---------- a confidence dial ----------
  function dial(p, bad) {
    const r = 13, c = 2 * Math.PI * r, s = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    s.setAttribute('class', 'hv-dial' + (bad ? ' bad' : '')); s.setAttribute('viewBox', '0 0 34 34');
    s.innerHTML = `<circle cx="17" cy="17" r="${r}" class="trk"/>
      <circle cx="17" cy="17" r="${r}" class="val" stroke-dasharray="${c}" stroke-dashoffset="${c}"/>
      <text x="17" y="21" text-anchor="middle">${Math.round(p * 100)}</text>`;
    requestAnimationFrame(() => setTimeout(() => { s.querySelector('.val').style.strokeDashoffset = c * (1 - p); }, 80));
    return s;
  }

  // ---------- per turn ----------
  function render(t) {
    const claims = t.rows.filter(r => r.key === 'ledger' || r.key === 'grounding');
    const denied = claims.filter(r => /^No\b/.test(r.answer));
    const added = (t.new_facts || []).length;
    const blocked = denied.length > 0;

    V.innerHTML = ''; C.innerHTML = '';
    const card = el('div', 'hv-verdict ' + (blocked ? 'bad' : 'ok'));
    card.appendChild(el('div', 'stamp', blocked ? '✕' : '✓'));
    const txt = el('div', 'txt');
    const n = denied.length, plural = n === 1 ? 'claim is' : 'claims are';
    txt.appendChild(el('div', 'head', blocked
      ? `Refused · ${n} of ${claims.length} ${plural} not in the record`
      : `Allowed · ${claims.length === 1 ? 'the claim checks out' : `all ${claims.length} claims check out`}`));
    txt.appendChild(el('div', 'sub', added
      ? `${added} new fact${added === 1 ? '' : 's'} recorded`
      : 'Nothing from this turn was recorded'));
    card.appendChild(txt);
    if (added) {
      const ul = el('ul', 'hv-added');
      (t.new_facts || []).forEach(f => ul.appendChild(el('li', '', f)));
      txt.appendChild(ul);
    }
    V.appendChild(card);

    if (claims.length) {
      C.appendChild(el('div', 'hv-h', 'WHAT THE ACTION RELIED ON'));
      claims.forEach((r, i) => {
        const bad = /^No\b/.test(r.answer);
        const row = el('div', 'hv-claim' + (bad ? ' bad' : ''));
        row.style.animationDelay = (i * 110) + 'ms';
        row.appendChild(dial(r.confidence || 0, bad));
        const b = el('div', 'b');
        b.appendChild(el('div', 'what', r.note || r.label));
        b.appendChild(el('div', 'says', bad ? 'the record does not say so' : 'the record says so'));
        row.appendChild(b);
        C.appendChild(row);
      });
    }

    // the same verdict, inline in the story, so the transcript itself carries the evidence
    const you = [...document.querySelectorAll('#story p.you')].pop();
    if (you) {
      const chip = el('div', 'hv-chip ' + (blocked ? 'bad' : 'ok'));
      chip.appendChild(el('span', 'dot', blocked ? '✕' : '✓'));
      chip.appendChild(el('span', '', blocked
        ? `${denied.length} of ${claims.length} claim${claims.length > 1 ? 's' : ''} refused · ${added ? added + ' fact' + (added > 1 ? 's' : '') + ' recorded' : 'nothing recorded'}`
        : `${claims.length} claim${claims.length === 1 ? '' : 's'} checked · ${added} fact${added === 1 ? '' : 's'} recorded`));
      you.after(chip);
    }

    turns.push({ added, blocked, denied: denied.length });
    TL.innerHTML = '';
    TL.appendChild(el('div', 'hv-h', 'THE STORY SO FAR · one column per turn'));
    const strip = el('div', 'hv-strip');
    turns.forEach((x, i) => {
      const col = el('div', 'col' + (x.blocked ? ' bad' : ''));
      const bar = el('div', 'bar'); bar.style.height = Math.min(48, 8 + x.added * 13) + 'px';
      col.appendChild(bar); col.appendChild(el('span', '', String(i + 1)));
      col.title = x.blocked ? `turn ${i + 1}: ${x.denied} claim(s) refused, ${x.added} fact(s) recorded`
                            : `turn ${i + 1}: ${x.added} fact(s) recorded`;
      strip.appendChild(col);
    });
    TL.appendChild(strip);
    TL.appendChild(el('div', 'hv-note', 'A short red column is a turn someone tried to add something that was never true.'));
  }

  document.addEventListener('hobson:start', () => { lit('nova'); });
  document.addEventListener('hobson:turn', e => { lit('decider', 'nova'); travel(0); travel(1); render(e.detail); });

  // keep the per-row flourishes in the (now collapsed) log
  new MutationObserver(ms => { for (const m of ms) for (const n of m.addedNodes) {
    if (n.nodeType !== 1 || !n.classList.contains('row')) continue;
    const q = (n.querySelector('.q') || {}).textContent || '', a = n.querySelector('.a');
    if (!a) continue;
    if (/dangerous/i.test(q)) { const mm = a.textContent.match(/(\d)\s*of\s*5/); if (mm) {
      const p = el('span', 'hv-pips' + (+mm[1] >= 4 ? ' hot' : ''));
      for (let i = 0; i < 5; i++) { const d = el('i'); if (i < +mm[1]) d.classList.add('on'); p.appendChild(d); } a.appendChild(p); } }
    if (/who writes/i.test(q)) { const pro = /pro/i.test(a.textContent);
      a.appendChild(el('span', 'hv-route ' + (pro ? 'pro' : 'lite'), pro ? 'stronger writer' : 'faster writer')); }
  } }).observe(rows, { childList: true });

  if (story) new MutationObserver(ms => { for (const m of ms) for (const n of m.addedNodes) {
    if (n.nodeType === 1 && n.classList && n.classList.contains('thinking')) {
      if (/^Nova/.test(n.textContent)) lit('nova'); else { lit('you'); travel(0); }
    } } }).observe(story, { childList: true });
})();
