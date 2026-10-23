"""Continuity: does the narrator's paragraph keep to the ledger and the ruling?

Not one vague question ("does this contradict anything?": Decider sat at 0.05-0.44 on it) but
one concrete `noul` per thing that could go wrong, the shape Decider is good at:

  - for every claim the ledger ruled NOT established:  "Does the PARAGRAPH show <claim> as true or happening?"   expect no
  - for every item the player does NOT hold:           "Does the PARAGRAPH show the player using or holding <item>?"  expect no
  - if the outcome's condition was not met:            "Does the PARAGRAPH show the attempt succeeding (<effect>)?"  expect no
  - always:                                            "Does the PARAGRAPH show this happening: <ruled effect>?"      expect yes

The draft fails if any expected-no is yes or the expected-yes is no. The Decision's value is
True when the paragraph broke the rules; `p` holds the per-check answers. Reusable standalone:

    Continuity(load_questions()).decide(lstate, checks=[("c0", "Does the PARAGRAPH show ...?", False)], paragraph="...")
"""
from __future__ import annotations

import re

from . import Decision, Handler, NoulQuestion, _noul

CRITERIA = {"true": "yes, the paragraph shows it", "false": "no, the paragraph does not show it"}


def _plain(claim: str) -> str:
    """'the player claims to hold a brass key' -> 'the player holds a brass key'"""
    c = claim.strip().rstrip(".")
    c = re.sub(r"^(the player|they|you)\s+claims?\s+(to\s+)?", "the player ", c, flags=re.I)
    c = re.sub(r"^the player (have|hold|know|own|carry|possess)\b", lambda m: "the player " + m.group(1) + "s", c)
    return c


def checks_for(decisions, met: bool, outcome: dict) -> list[tuple[str, str, bool]]:
    """Build the check list from a turn's decisions: (key, question, expected answer).

    Contested turn (a claim or holding Decider was sure is false, or the condition unmet): one
    question, "does the paragraph show the attempt succeeding in any form?", expected no. Asking
    per claim ("does it show the player holding the key?") was tried first and failed on correct
    prose: a paragraph that says "the key your uncle supposedly gave you" mentions the key, and
    both Decider and Nova Lite read a mention as a showing. Uncontested turn: did the ruled
    outcome happen, expected yes."""
    sure_false = [d for d in decisions if d.name in ("ledger", "grounds") and not d.value and d.via == "decider"]
    contested = (not met) or bool(sure_false)
    if contested:
        out = [("fail", "Does the PARAGRAPH show the player's attempt succeeding in any form?", False)]
        for i, d in enumerate(x for x in sure_false if x.name == "grounds"):
            out.append((f"hold_{i}", f"Does the PARAGRAPH show {d.detail} physically present and being used by the player "
                                    f"(turning in a lock, handed over, lit)? Reaching for it and finding nothing does not count.", False))
        return out[:4]
    return [("outcome", f"Does the PARAGRAPH show this happening: {outcome.get('effect')}?", True)]


def short_name(x: str) -> str:
    """'the player holds a brass key' -> 'a brass key'; 'the player knows their uncle' ->
    'their uncle' (no article in front of a possessive, which produced "a their uncle")."""
    x = re.sub(r"^(the player|you)\s+(claims?\s+to\s+)?(holds?|has|knows?|owns?|carries|carry)\s+",
               "", str(x).strip(), flags=re.I)
    x = re.sub(r"^(one|a|an|the)\s+", "", x, flags=re.I).strip().rstrip(".")
    if re.match(r"^(their|his|her|its|our|your|my)\b", x, flags=re.I):
        return x
    return "a " + x


_GENERIC = {"thing", "things", "one", "ones", "something", "anything", "it", "them",
            "item", "items", "object", "objects", "person", "people", "someone"}


def head_noun(short: str) -> str:
    """'a locked cabinet by the lamp' -> 'cabinet'; 'a brass key' -> 'key'; 'their uncle' -> 'uncle'.
    The trailing prepositional phrase is dropped first, because it usually names something that
    IS in the ledger ('by the lamp') and matching on it would throw away honest facts."""
    x = re.split(r"\s+(?:by|in|on|at|of|from|with|near|beside|under|inside)\s+", str(short).strip(), maxsplit=1)[0]
    words = re.findall(r"[A-Za-z][A-Za-z'-]*", x)
    return words[-1].lower() if words else ""


def mentions_absent(fact: str, absent) -> str:
    """The deterministic half of the screen: a fact that names an absent thing by its head noun
    is refused without asking anyone. A model was asked first and let 'You do not have the key to
    open the locked cabinet' through, which concedes the cabinet exists; a string match does not
    have opinions. Returns the matched noun, or ''."""
    text = str(fact).lower()
    for a in absent:
        h = head_noun(short_name(a))
        if len(h) > 2 and h not in _GENERIC and re.search(rf"\b{re.escape(h)}(e?s)?\b", text):
            return h
    return ""


def screen_facts(handler, state, absent, facts, fallback=None):
    """Last gate on the record: drop any fact that treats a thing the ledger says is absent as
    real. Nova proposes the outcomes, so on a contested turn it can offer "the key does not fit"
    and the accepted paragraph then writes the key into the ledger. One noul per candidate fact,
    all in one Decider call. Returns (kept, dropped, latency_ms)."""
    plain = [f for f in facts if not str(f).startswith("~")]
    if not absent or not plain:
        return list(facts), [], 0.0
    # 1. the deterministic gate: anything naming an absent thing is out, no model involved
    hard_drop = [f for f in plain if mentions_absent(f, absent)]
    plain = [f for f in plain if f not in hard_drop]
    if not plain:
        return [f for f in facts if str(f).startswith("~")], hard_drop, 0.0
    # 2. the model gate, for everything that survived the string match
    what = "; ".join(dict.fromkeys(short_name(a) for a in absent))
    qs = {f"f{i}": NoulQuestion(
            instructions=f'None of these exist: {what}. Does this sentence mention or rely on any of them? '
                         f'SENTENCE: "{f}"',
            criteria={"true": "yes, the sentence mentions or relies on one of them",
                      "false": "no, the sentence is about something else entirely"})
          for i, f in enumerate(plain)}
    resp, ms = handler.decider.ask_many(state, qs)
    keep, drop = [], []
    for i, f in enumerate(plain):
        d = _noul("fact", resp, f"f{i}", ms, handler.threshold, "", detail=str(f)[:60])
        if d.unsure and fallback:
            fallback(d, f'{state}\n\nSENTENCE: "{f}"')
        # fail closed: the record is the thing being protected, so a fact that is not clearly
        # clear of the absent things does not get written
        (drop if (d.value or d.unsure) else keep).append(f)
    return keep + [f for f in facts if str(f).startswith("~")], hard_drop + drop, ms


class Continuity(Handler):
    def _text(self, state, paragraph):
        return f"{state}\n\nPARAGRAPH:\n{paragraph}"

    def build(self, state, checks=(), paragraph="", **ctx):
        return {k: NoulQuestion(instructions=q, criteria=CRITERIA) for k, q, _ in checks}

    def read(self, resp, ms, checks=(), paragraph="", **ctx) -> list[Decision]:
        items = [_noul(k, resp, k, ms, self.threshold, q, detail=("expect yes" if exp else "expect no"))
                 for k, q, exp in checks]
        return items

    def decide(self, state, checks=(), paragraph="", fallback=None, **ctx) -> Decision:
        """One Decider call for all checks; `fallback(decision, text)` re-makes any unsure item
        (Hobson passes the narrator's Nova Lite fallback). Returns the combined Decision."""
        qs = self.build(state, checks=checks)
        text = self._text(state, paragraph)
        resp, ms = self.decider.ask_many(text, qs)
        items = self.read(resp, ms, checks=checks)
        for it in items:
            if it.unsure and fallback:
                fallback(it, text)
        broke = []
        for it, (k, q, exp) in zip(items, checks):
            if bool(it.value) != exp:
                broke.append(k)
        conf = min((it.confidence for it in items if it.confidence is not None), default=None)
        via = "nova" if any(it.via == "nova" for it in items) else "decider"
        p = {k: round(float(it.p.get("true", 0.0)), 3) for it, (k, _, _) in zip(items, checks)}
        d = Decision("continuity", bool(broke), p, conf, any(it.unsure for it in items) and via == "decider",
                     ms, via=via, detail="", kind="noul",
                     question="; ".join(q for _, q, _ in checks), options=None)
        d.decider_value = {"broke": broke, "checks": len(checks)}
        return d
