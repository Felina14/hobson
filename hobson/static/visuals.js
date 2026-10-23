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


  // ---------- mark up the player's own sentence ----------
  // Each claim row names what the action leaned on ("the player holds a brass key"). The words of
  // that thing are found in the sentence the player typed and underlined there: red where the
  // record does not hold it, green where it does. Nothing is guessed; if the words are not in the
  // sentence, nothing is marked.
  const STOP = new Set(['the','a','an','player','holds','hold','has','have','knows','know','their',
    'his','her','its','your','my','our','of','to','by','in','on','at','is','was','were','and','or',
    'that','this','there','claims','claim','given','gave','location','one','some','any']);

  function markSentence(elp, claims, record) {
    // a word the record already holds ("lamp") can sit inside a refused claim ("a locked cabinet
    // by the lamp"); it is real, so it is never marked as missing
    const held = new Set((record || []).join(' ').toLowerCase().match(/[a-z][a-z'-]*/g) || []);
    if (!elp || elp.dataset.marked) return;
    const text = elp.textContent.replace(/^>\s*/, '');
    const spans = [];
    claims.forEach(r => {
      const bad = /^No\b/.test(r.answer);
      const words = String(r.note || '').toLowerCase().match(/[a-z][a-z'-]*/g) || [];
      const want = words.filter(w => !STOP.has(w) && w.length > 2 && !(bad && held.has(w)));
      want.forEach(w => {
        const m = new RegExp('\\b' + w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '\\w*', 'i').exec(text);
        if (m) spans.push({ from: m.index, to: m.index + m[0].length, bad });
      });
    });
    if (!spans.length) return;
    // merge touching or overlapping spans so "brass key" underlines once, not twice
    spans.sort((a, b) => a.from - b.from);
    const merged = [];
    spans.forEach(sp => {
      const last = merged[merged.length - 1];
      if (last && sp.from <= last.to + 1 && sp.bad === last.bad) last.to = Math.max(last.to, sp.to);
      else merged.push({ ...sp });
    });
    let out = '', at = 0;
    const esc = t => t.replace(/[&<>]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));
    merged.forEach(sp => {
      out += esc(text.slice(at, sp.from));
      out += `<mark class="hv-mark ${sp.bad ? 'bad' : 'ok'}">${esc(text.slice(sp.from, sp.to))}</mark>`;
      at = sp.to;
    });
    out += esc(text.slice(at));
    elp.innerHTML = out;
    elp.dataset.marked = '1';
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
      : claims.length === 0 ? 'Allowed · the action claimed nothing to check'
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
    markSentence(you, claims, t.ledger);
    if (you) {
      const chip = el('div', 'hv-chip ' + (blocked ? 'bad' : 'ok'));
      chip.appendChild(el('span', 'dot', blocked ? '✕' : '✓'));
      const facts = added ? `${added} fact${added > 1 ? 's' : ''} recorded` : 'nothing recorded';
      chip.appendChild(el('span', '', blocked
        ? `${denied.length} of ${claims.length} claim${claims.length > 1 ? 's' : ''} refused · ${facts}`
        : claims.length === 0 ? `nothing claimed · ${facts}`
        : `${claims.length} claim${claims.length === 1 ? '' : 's'} checked · ${facts}`));
      you.after(chip);
    }

    turns.push({ added, blocked, denied: denied.length });
    TL.innerHTML = '';
    const kept = turns.filter(x => x.blocked).length;
    const h = el('div', 'hv-h', 'EVERY TURN SO FAR');
    if (kept) h.appendChild(el('em', '', `${kept} refused`));
    TL.appendChild(h);
    const strip = el('div', 'hv-strip');
    turns.forEach((x, i) => {
      const col = el('div', 'col' + (x.blocked ? ' bad' : ''));
      const bar = el('div', 'bar'); bar.style.height = Math.min(54, 10 + x.added * 14) + 'px';
      col.appendChild(bar); col.appendChild(el('span', '', String(i + 1)));
      col.title = x.blocked ? `turn ${i + 1}: ${x.denied} claim(s) refused, ${x.added} fact(s) recorded`
                            : `turn ${i + 1}: ${x.added} fact(s) recorded`;
      strip.appendChild(col);
    });
    TL.appendChild(strip);
    TL.appendChild(el('div', 'hv-note',
      'Height is how much that turn added to the record. Red is a turn that tried to add something never true.'));

    // the record is the thing being protected: show it reacting
    const led = document.getElementById('ledger');
    if (led) { led.classList.remove('sealed'); void led.offsetWidth; if (blocked && !added) led.classList.add('sealed'); }
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
