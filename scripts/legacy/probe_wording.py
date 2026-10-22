"""Why questions.yaml and the world file look the way they do: the alternatives asked on the
same states, side by side. Decider (local, MPS) for everything; Nova Lite too for `allowed`,
because Nova Lite was the fallback that re-made unsure rulings.

0. dice over the scene's concrete actions vs over action categories
1. category dice: spec options vs the tuned options (kept behind --dice categories)
2. ledger claims: with the action in the state vs the ledger alone
3. allowed (retired: impossible attempts are now an outcome)
4. danger (retired: danger is now authored on each outcome)

    python scripts/probe_wording.py
Writes results/wording_probe.jsonl and results/md/wording_probe.md."""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from strands_decider.schema import ChoiceQuestion, NoulQuestion, ScoreQuestion  # noqa: E402

from hobson.handlers import get_decider, load_questions  # noqa: E402
from hobson.mdlog import finish_run  # noqa: E402
from hobson.narrator import _FallbackNova  # noqa: E402
from hobson.state import Ledger, World, state_text  # noqa: E402

THR = 0.6
# The spec's first-draft wording (SPEC_hobson.md, questions.yaml section).
SPEC = {
    "dice": {"move": "Go somewhere, enter or leave a place",
             "talk": "Speak to a character: ask, persuade, greet, threaten verbally",
             "take": "Pick up, steal, buy or receive an item",
             "use": "Use, give, show or combine an item the player holds",
             "attack": "Physical violence or force against a character or object",
             "bluff": "Claim something is true, or present something, to deceive",
             "other": "None of the above or unclear"},
    "allowed": "Under the scene rules, is this action physically and narratively possible right now?",
    "danger": ["0 harmless", "1 minor risk", "2 some risk", "3 serious", "4 very dangerous", "5 lethal"],
}
# The wording these questions had before they were retired (questions.yaml, 2026-10-22).
RETIRED = {
    "allowed": ("Can the player attempt this action here, under the world rules? Whether it succeeds does not matter.",
                {"true": "it can be attempted, even if it may fail or be dangerous",
                 "false": "it cannot even be attempted: needs magic, flying, money or items not held, or a locked way"}),
    "danger_q": "How dangerous was this action for the player?",
    "danger": ["0 harmless: talking, looking, walking", "1 minor risk: rudeness, small mischief",
               "2 some risk: lying to an official, petty theft", "3 serious: stealing in sight, threatening",
               "4 very dangerous: violence against a guard or armed person", "5 lethal: fighting to kill"],
}
# (scene, expected action id, line); the first five are demo/demo_turns.txt
ACTION_LINES = [("gate", "ask-guard", "I ask the guard what the town is called"),
                ("gate", "present-token", "I show him the pass the merchant gave me"),
                ("gate", "loiter", "I sort of edge towards the gate while humming"),
                ("gate", "push-past", "I draw my cloak around me and shove the guard aside"),
                ("jail", "talk-jailer", "I look around and ask whoever is nearest where I am"),
                ("gate", "claim-rank", "I tell the guard I'm the mayor's nephew"),
                ("gate", "give-item", "I give the guard one copper coin"),
                ("gate", "walk-through", "I walk through the gate into the market"),
                ("market", "buy", "I buy the brass key"),
                ("market", "hit-someone", "I punch the merchant"),
                ("market", "talk-child", "I ask the child what she knows"),
                ("market", "steal", "I grab the key and run"),
                ("market", "go-elsewhere", "I head to the inn"),
                ("gate", "impossible", "I fly over the town wall"),
                ("gate", "impossible", "I pay the guard ten gold coins"),
                ("jail", "impossible", "I teleport out of the cell"),
                ("market", "impossible", "I cast a spell to open the locked box")]
# 0b: not-possible-here offered among the outcome options instead (the design it replaced)
NP_EFFECT = "That cannot be done here; the attempt fails."
NP_CASES = [("gate", "talk", ["guard-asks-business", "guard-chats"], "I ask the guard what the town is called"),
            ("gate", "bluff", ["guard-suspicious"], "I show him the pass the merchant gave me"),
            ("gate", "move", ["guard-stops-you", "walk-the-wall"], "I sort of edge towards the gate while humming"),
            ("gate", "attack", ["guard-overpowers-you", "you-flee"], "I draw my cloak around me and shove the guard aside"),
            ("jail", "talk", ["jailer-ignores"], "I look around and ask whoever is nearest where I am"),
            ("gate", "move", ["not-possible-here"], "I fly over the town wall"),
            ("gate", "use", ["not-possible-here"], "I pay the guard ten gold coins"),
            ("jail", "move", ["not-possible-here"], "I walk out of the cell door"),
            ("market", "use", ["not-possible-here"], "I cast a spell to open the locked box")]

DICE_LINES = [("gate", "talk", "I ask the guard what the town is called"),
              ("gate", "bluff", "I show him the pass the merchant gave me"),
              ("gate", "?", "I sort of edge towards the gate while humming"),
              ("gate", "attack", "I draw my cloak around me and shove the guard aside"),
              ("gate", "bluff", "I tell the guard I'm the mayor's nephew"),
              ("gate", "use", "I give the guard one copper coin"),
              ("gate", "move", "I walk through the gate into the market"),
              ("market", "take", "I buy the brass key"),
              ("market", "attack", "I punch the merchant"),
              ("market", "talk", "I ask the child what she knows"),
              ("market", "take", "I grab the key and run"),
              ("market", "move", "I head to the inn")]
ALLOWED_LINES = [(True, "gate", "I ask the guard what the town is called"),
                 (True, "gate", "I show him the pass the merchant gave me"),
                 (True, "gate", "I sort of edge towards the gate while humming"),
                 (True, "gate", "I draw my cloak around me and shove the guard aside"),
                 (True, "market", "I punch the merchant"),
                 (True, "market", "I grab the key and run"),
                 (False, "gate", "I fly over the town wall"),
                 (False, "gate", "I pay the guard ten gold coins"),
                 (False, "jail", "I walk out of the cell door"),
                 (False, "market", "I cast a spell to open the locked box")]
CLAIMS = [(True, "the player has three copper coins"), (True, "the player has a travelling cloak"),
          (True, "the merchant is selling a brass key"), (True, "the player arrived on foot"),
          (False, "the merchant gave the player a pass"), (False, "the player holds a brass key"),
          (False, "the player knows the sergeant"), (False, "the player has a sword")]
PASS_ACTION = "I show him the pass the merchant gave me"


def main():
    w, q = World.load(), load_questions()
    eng = get_decider().engine
    nova = _FallbackNova("lite")
    ledger = Ledger(list(w.established) + ["the merchant is selling a brass key"])
    rows, out = [], []

    def ok(p, truth):
        return (p >= 0.5) == truth and abs(2 * p - 1) >= THR

    # 0. dice over concrete scene actions vs categories
    out.append("0. DICE: scene actions vs categories  pick/confidence; * = wrong or confidence < 0.6")
    out.append(f"   {'expected':14} {'line':44} {'actions':>20} {'categories':>15}")
    hits = {"actions": 0, "categories": 0}
    cat = q["dice_categories"]
    for i, (sc, exp, a) in enumerate(ACTION_LINES):
        scene = w.scenes[sc]
        acts = {k: v["says"] for k, v in scene.actions.items()}
        s = state_text(w, scene, ledger, a)
        r = eng.ask(s, {"act": ChoiceQuestion(instructions=q["dice"]["question"], criteria=acts),
                        "cat": ChoiceQuestion(instructions=cat["question"], criteria=cat["options"])})
        ac, cc = r.answers["act"], r.answers["cat"]
        etype = scene.actions[exp]["type"]
        good_a = ac.choice == exp and ac.confidence >= THR
        good_c = cc.choice == etype and cc.confidence >= THR
        hits["actions"] += good_a; hits["categories"] += good_c
        rows.append({"probe": "dice_actions", "line": a, "expected": exp, "expected_type": etype,
                     "demo": i < 5, "actions": [ac.choice, ac.confidence], "categories": [cc.choice, cc.confidence]})
        out.append(f"   {exp:14} {a[:44]:44} {ac.choice[:13] + f'/{ac.confidence:.2f}' + (' ' if good_a else '*'):>20} "
                   f"{cc.choice + f'/{cc.confidence:.2f}' + (' ' if good_c else '*'):>15}")
    demo_a = sum(1 for r in rows if r.get("probe") == "dice_actions" and r["demo"]
                 and r["actions"][0] == r["expected"] and r["actions"][1] >= THR)
    out.append(f"   right and confident: actions {hits['actions']}/{len(ACTION_LINES)}, "
               f"categories {hits['categories']}/{len(ACTION_LINES)} (category judged on the action's type)")
    out.append(f"   the five demo lines, actions dice: {demo_a}/5 right with confidence >= {THR}")
    imp = [r for r in rows if r.get("probe") == "dice_actions" and r["expected"] == "impossible"]
    imp_ok = sum(1 for r in imp if r["actions"][0] == "impossible" and r["actions"][1] >= THR)
    out.append(f"   impossible attempts sent to the `impossible` action: {imp_ok}/{len(imp)}")

    # 0b. the replaced design: not-possible-here as one of the outcome options
    out.append("\n0b. NOT-POSSIBLE AS AN OUTCOME OPTION (replaced)  outcome pick/confidence; * = wrong or < 0.6")
    np_ok = 0
    for sc, t, want, a in NP_CASES:
        opts = {k: o["effect"] for k, o in w.scenes[sc].options_for(t, w.default_outcomes, {}).items()}
        opts["not-possible-here"] = NP_EFFECT
        x = eng.ask(state_text(w, w.scenes[sc], ledger, a),
                    {"o": ChoiceQuestion(instructions=q["outcome"]["question"], criteria=opts)}).answers["o"]
        good = x.choice in want and x.confidence >= THR
        np_ok += good
        rows.append({"probe": "not_possible_as_outcome", "line": a, "want": want, "pick": x.choice, "confidence": x.confidence})
        out.append(f"   {'/'.join(want)[:36]:36} {a[:40]:40} {x.choice[:20]:>20}/{x.confidence:.2f}{' ' if good else '*'}")
    out.append(f"   right and confident: {np_ok}/{len(NP_CASES)}")
    out.append("")

    # 1. dice: spec options vs adopted options
    out.append("1. CATEGORY DICE  pick/confidence, spec options vs tuned (questions.yaml dice_categories)")
    out.append(f"   {'expected':8} {'line':44} {'spec':>14} {'adopted':>14}")
    for sc, exp, a in DICE_LINES:
        s = state_text(w, w.scenes[sc], ledger, a)
        r = eng.ask(s, {"spec": ChoiceQuestion(instructions=cat["question"], criteria=SPEC["dice"]),
                        "adopted": ChoiceQuestion(instructions=cat["question"], criteria=cat["options"])})
        sp, ad = r.answers["spec"], r.answers["adopted"]
        rows.append({"probe": "dice", "line": a, "expected": exp, "spec": [sp.choice, sp.confidence],
                     "adopted": [ad.choice, ad.confidence]})
        out.append(f"   {exp:8} {a[:44]:44} {sp.choice + f'/{sp.confidence:.2f}':>14} {ad.choice + f'/{ad.confidence:.2f}':>14}")

    # 2. ledger claims: with the action in the state vs the ledger alone
    out.append("\n2. LEDGER CLAIMS  p(established); * = wrong side or confidence < 0.6")
    out.append(f"   action in state: \"{PASS_ACTION}\"")
    out.append(f"   {'truth/claim':44} {'with action':>12} {'ledger only':>12}")
    with_a = state_text(w, w.scenes["gate"], ledger, PASS_ACTION)
    alone = state_text(w, w.scenes["gate"], ledger, None)
    lq = q["ledger_claim"]
    qs = {f"c{i}": NoulQuestion(instructions=lq["question"].format(claim=c), criteria=lq.get("criteria"))
          for i, (_, c) in enumerate(CLAIMS)}
    ra, rb = eng.ask(with_a, qs), eng.ask(alone, qs)
    tally = {"with action": 0, "ledger only": 0}
    for i, (truth, c) in enumerate(CLAIMS):
        pa, pb = ra.answers[f"c{i}"].noul, rb.answers[f"c{i}"].noul
        tally["with action"] += ok(pa, truth); tally["ledger only"] += ok(pb, truth)
        rows.append({"probe": "ledger", "claim": c, "truth": truth, "with_action": pa, "ledger_only": pb})
        out.append(f"   {('T ' if truth else 'F ') + c:44} {pa:>11.2f}{' ' if ok(pa, truth) else '*'} "
                   f"{pb:>11.2f}{' ' if ok(pb, truth) else '*'}")
    out.append(f"   right and confident: with action {tally['with action']}/{len(CLAIMS)}, "
               f"ledger only {tally['ledger only']}/{len(CLAIMS)}")

    # 3. allowed: spec wording vs adopted, Decider and Nova Lite
    out.append("\n3. ALLOWED (retired)  Decider p(true) [* = wrong or unsure] and Nova Lite answer [! = wrong]")
    out.append(f"   {'truth/line':46} {'spec D':>8} {'Nova':>5} {'adopted D':>10} {'Nova':>5}")
    al = {"question": RETIRED["allowed"][0], "criteria": RETIRED["allowed"][1]}
    score = {"spec_d": 0, "spec_n": 0, "ad_d": 0, "ad_n": 0}
    for truth, sc, a in ALLOWED_LINES:
        s = state_text(w, w.scenes[sc], ledger, a)
        r = eng.ask(s, {"spec": NoulQuestion(instructions=SPEC["allowed"]),
                        "adopted": NoulQuestion(instructions=al["question"], criteria=al.get("criteria"))})
        ps, pa = r.answers["spec"].noul, r.answers["adopted"].noul
        ns = nova.noul(s, SPEC["allowed"]).answer >= 0.5
        na = nova.noul(s, al["question"], al.get("criteria")).answer >= 0.5
        score["spec_d"] += ok(ps, truth); score["ad_d"] += ok(pa, truth)
        score["spec_n"] += ns == truth; score["ad_n"] += na == truth
        rows.append({"probe": "allowed", "line": a, "truth": truth, "spec_decider": ps, "spec_nova": ns,
                     "adopted_decider": pa, "adopted_nova": na})
        out.append(f"   {('T ' if truth else 'F ') + a[:44]:46} {ps:>7.2f}{' ' if ok(ps, truth) else '*'} "
                   f"{('T' if ns else 'F') + (' ' if ns == truth else '!'):>5} {pa:>9.2f}{' ' if ok(pa, truth) else '*'} "
                   f"{('T' if na else 'F') + (' ' if na == truth else '!'):>5}")
    n = len(ALLOWED_LINES)
    out.append(f"   Decider right and confident: spec {score['spec_d']}/{n}, adopted {score['ad_d']}/{n}. "
               f"Nova Lite right: spec {score['spec_n']}/{n}, adopted {score['ad_n']}/{n}")

    # 4. danger: spec levels vs adopted levels (with examples)
    out.append("\n4. DANGER (retired)  expected value / confidence, and P(level >= 3)")
    out.append(f"   {'line':44} {'spec levels':>24} {'adopted levels':>24}")
    dq = {"question": RETIRED["danger_q"], "levels": RETIRED["danger"]}
    best = 0.0
    for sc, exp, a in DICE_LINES:
        s = state_text(w, w.scenes[sc], ledger, a)
        r = eng.ask(s, {"spec": ScoreQuestion(instructions=dq["question"], criteria=SPEC["danger"]),
                        "adopted": ScoreQuestion(instructions=dq["question"], criteria=dq["levels"])})
        cells = []
        for k in ("spec", "adopted"):
            x = r.answers[k]
            hi = sum(v for lv, v in x.probabilities.items() if int(lv) >= 3)
            best = max(best, x.confidence)
            cells.append(f"{x.score:.1f}/{x.confidence:.2f} P≥3={hi:.2f}")
            rows.append({"probe": "danger", "wording": k, "line": a, "score": x.score,
                         "confidence": x.confidence, "p_ge3": hi})
        out.append(f"   {a[:44]:44} {cells[0]:>24} {cells[1]:>24}")
    out.append(f"   highest danger confidence seen in either wording: {best:.2f} (threshold {THR})")

    path = ROOT / "results" / "wording_probe.jsonl"
    with path.open("w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    print("\n".join(out))
    finish_run("wording_probe", "Question wording: spec draft vs adopted", {"threshold": THR, "date": time.strftime("%Y-%m-%d")},
               out, path, notes="Spec wording is the first draft in SPEC_hobson.md; adopted wording is hobson/questions.yaml.")


if __name__ == "__main__":
    main()
