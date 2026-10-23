"""The baseline referee (`--referee nova`): Nova Lite makes the same decisions from the same
state as Decider, via JSON-constrained prompts. One call for dice + ledger claims, one for the
outcome (+ conditions and grounding), one pairwise call for the editor. Nova gives no confidence, so
nothing is ever `unsure` in this mode."""
from __future__ import annotations

from .handlers import Decision
from .narrator import parse_json

SYSTEM = "You are the referee of a text adventure. Judge strictly from the STATE. Reply with JSON only."


class NovaReferee:
    def __init__(self, narrator, questions):
        self.n, self.q = narrator, questions

    def _ask(self, state, body, max_tokens=300):
        text, ms = self.n.converse("lite", SYSTEM, f"STATE:\n{state}\n\n{body}", max_tokens=max_tokens, ruling=True)
        try:
            return parse_json(text), ms
        except Exception:
            return {}, ms

    def _d(self, name, value, ms, kind, question, options=None, detail=""):
        return Decision(name, value, {}, None, False, ms, via="nova", detail=detail, kind=kind,
                        question=question, options=options)

    def holdings(self, lstate, holdings):
        if not holdings:
            return []
        q = self.q
        hold = "\n".join(f'  "{h["object"]}": ' + q["grounding"]["question"].format(
            object=h["object"], amount=h.get("amount") or "one") for h in holdings)
        d, ms = self._ask(lstate, f"Answer true/false for each holding:\n{hold}\nReturn {{\"holdings\": {{\"<object>\": true|false}}}}", max_tokens=120)
        out = []
        for h in holdings:
            amt = h.get("amount") or "one"
            out.append(self._d("grounds", bool((d.get("holdings") or {}).get(h["object"], False)), ms, "noul",
                               q["grounding"]["question"].format(object=h["object"], amount=amt),
                               detail=f"{amt} {h['object']}".strip()))
        return out

    def screen_facts(self, lstate, absent, facts):
        plain = [f for f in facts if not str(f).startswith("~")]
        if not absent or not plain:
            return list(facts), []
        what = "; ".join(absent)
        body = ("These do not exist: " + what + ".\nFor each sentence, does it treat any of them as real, "
                "present or existing?\n" + "\n".join(f'  "{i}": "{f}"' for i, f in enumerate(plain))
                + '\nReturn {"<index>": true|false}')
        d, ms = self._ask(lstate, body, max_tokens=120)
        keep, drop = [], []
        for i, f in enumerate(plain):
            (drop if bool(d.get(str(i), False)) else keep).append(f)
        return keep + [f for f in facts if str(f).startswith("~")], drop

    def continuity(self, lstate, checks, paragraph):
        qs = "\n".join(f'  "{k}": {q}' for k, q, _ in checks)
        d, ms = self._ask(f"{lstate}\n\nPARAGRAPH:\n{paragraph}",
                          f"Answer true/false for each:\n{qs}\nReturn {{\"<key>\": true|false}}", max_tokens=120)
        broke = [k for k, q, exp in checks if bool(d.get(k, exp)) != exp]
        out = self._d("continuity", bool(broke), ms, "noul", "; ".join(q for _, q, _ in checks))
        out.decider_value = {"broke": broke, "checks": len(checks)}
        return out

    def call1(self, state, claims, dice_opts):
        q = self.q
        dq = q["dice"]["question"]
        menu = "\n".join(f"  {k}: {v}" for k, v in dice_opts.items())
        cl = "\n".join(f'  "{c}"' for c in claims) or "  (none)"
        body = (f"1. {dq} Options:\n{menu}\n"
                f"2. For each claim, {q['ledger_claim']['question'].replace(': {claim}', '')}\n{cl}\n"
                'Return {"dice": "<option>", "claims": {"<claim>": true|false}}')
        d, ms = self._ask(state, body)
        dice = d.get("dice") if d.get("dice") in dice_opts else list(dice_opts)[-1]
        out = [self._d("dice", dice, ms, "choice", dq, dice_opts)]
        got = d.get("claims") or {}
        for c in claims:
            v = got.get(c, list(got.values())[claims.index(c)] if len(got) == len(claims) else False)
            out.append(self._d("ledger", bool(v), ms, "noul", q["ledger_claim"]["question"].format(claim=c), detail=c))
        return out, ms

    def call2(self, state, outcomes, requires, holdings):
        q = self.q
        menu = "\n".join(f"  {k}: {v}" for k, v in outcomes.items())
        req = "\n".join(f'  "{label}": does the ledger establish that {c}?' for label, c in requires.items())
        hold = "\n".join(f'  "{h["object"]}": ' + q["grounding"]["question"].format(
            object=h["object"], amount=h.get("amount") or "one") for h in holdings)
        body = (f"1. {q['outcome']['question']} Options:\n{menu}\n"
                + (f"2. Answer true/false for each condition:\n{req}\n" if req else "")
                + (f"3. Answer true/false for each holding:\n{hold}\n" if hold else "")
                + 'Return {"outcome": "<option>", "requires": {"<label>": true|false}, '
                  '"holdings": {"<object>": true|false}}')
        d, ms = self._ask(state, body)
        oc = d.get("outcome") if d.get("outcome") in outcomes else next(iter(outcomes))
        out = [self._d("outcome", oc, ms, "choice", q["outcome"]["question"], outcomes)]
        for label, c in requires.items():
            out.append(self._d("requires", bool((d.get("requires") or {}).get(label, False)), ms, "noul",
                               f"Does the ledger establish that {c}?", detail=label))
        for h in holdings:
            amt = h.get("amount") or "one"
            out.append(self._d("grounds", bool((d.get("holdings") or {}).get(h["object"], False)), ms, "noul",
                               q["grounding"]["question"].format(object=h["object"], amount=amt),
                               detail=f"{amt} {h['object']}".strip()))
        return out, ms

    def editor(self, context, a, b):
        e = self.q["editor"]
        body = f"DRAFT A:\n{a}\n\nDRAFT B:\n{b}\n\n{e['swap_question']}\nReturn {{\"better\": \"A\"|\"B\"}}"
        d, ms = self._ask(context, body, max_tokens=20)
        pick = d.get("better") if d.get("better") in ("A", "B") else "A"
        return self._d("editor", pick, ms, "choice", e["swap_question"], e["swap_options"])
