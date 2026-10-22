# Hobson

**Nova writes; Hobson decides.** A game master you play in the terminal. Amazon Nova narrates a
small market town at dusk. Every decision about what your free-text action means and what happens
next is made by **Strands Decider 2B**, running locally, which prints its numbers under each action.
When Decider is unsure, Nova Lite re-makes that one decision and the screen says so.

Entry for the AWS Builder Center *Agent Experience Hackathon: Strands Decider*. Decision pattern:
**`#policy`** (classify the request before the agent acts). Also shows tool selection (the dice is
a pick over the scene's concrete actions, the outcome a pick over prepared results), context/memory
(the ledger) and evaluation (the referee comparison).

Named after the checkpoint, `strands-decider-2B-hobson-v19`, and after Hobson's choice: you can type
anything, but what can happen was fixed before you typed it.

```
> I show him the pass the merchant gave me

  dice     action: present-token (bluff)                                        0.96
  ledger   "the player claims to have a pass given …"  not established          0.79
  ruling   outcome: guard-suspicious                                            0.85
  danger   2 / 5  (authored on the outcome)
  route    narrator: Lite (danger 2)
  editor   tie (2.5 vs 2.6) → A · swap disagrees
  ⟲ 2628 ms on Decider · 4.9 s on Nova
```

_(Turn 2 of run `hobson_decider_s7_20261022-172956`; rows in `results/referee_decider_7.jsonl`.)_

## Run it

Apple Silicon (MPS). Decider runs in-process; Bedrock is Nova only (Lite and Pro), us-east-1.

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt          # first Decider call pulls the v19 weights (~4 GB)
export AWS_PROFILE=<your-profile> AWS_REGION=us-east-1

python -m hobson play                                     # play
python -m hobson play --script demo/demo_turns.txt --seed 7 --show-drafts   # the demo
python -m hobson play --referee nova --script demo/demo_turns.txt           # Nova decides instead
python -m hobson play --dice categories --script demo/demo_turns.txt        # the old category dice
python -m hobson compare --seed 7 --repeats 3             # both referees → results/md/referee_compare.md
python scripts/probe_wording.py                           # → results/md/wording_probe.md
```

Every run appends one JSON row per turn to `results/referee_<mode>_<seed>.jsonl` (each ruling with
its probabilities and confidence, both drafts, the pick, latency, tokens per Nova tier, cost) and
writes `results/md/<run>.md`.

## One turn

1. **Claims.** Nova Lite lists up to three things your action relies on ("the merchant gave the
   player a pass") and any object or amount it names.
2. **Decider, call A, against the ledger alone** (the state stops before your action): one `noul`
   per claim, one `noul` per named object (grounding), one `noul` per conditional outcome in the
   scene ("the player holds three copper coins").
3. **Decider, call B, the dice:** a `choice` over the scene's concrete actions from
   `world/town.yaml` (at the gate: `ask-guard`, `present-token`, `claim-rank`, `walk-through`,
   `go-back`, `loiter`, `push-past`, `give-item`, `impossible`, `something-else`). The picked
   action's `type` selects the outcome group.
4. **Decider, call C, the outcome:** a `choice` over that group's prepared outcomes. An
   `impossible` action ("fly, use magic, or pay with something you don't have") has one outcome,
   `not-possible-here`, so there is nothing to ask.
5. **Unsure → Nova Lite.** Any decision with confidence below 0.6 is re-asked of Nova Lite with
   the same question and options (in parallel), and shown as `? (0.45) → via Nova: talk-jailer`.
6. **Stakes routing.** The picked outcome's danger, authored in the world file (default 0), routes
   the narration: 0–2 → Nova Lite, 3–5 → Nova Pro. Being overpowered by the guard is 5.
7. **Two drafts, one editor.** Nova writes two drafts (temperature 0.8). Decider scores each alone
   on a 0–6 rubric and the higher wins; within 0.2 is a tie and A is kept. The A/B-then-B/A
   pairwise pick is asked too, as a consistency check, and printed as `swap agrees/disagrees`.
8. **Ledger.** The winning draft's `FACTS:` and the outcome's `adds` are appended; a `goto` moves
   you to the next scene; danger ≥ 4 means guards arrive next turn.

Actions and outcomes come from `world/town.yaml` and are fixed before any input; the narrator would
only fill an outcome group a scene leaves empty, and none does.

## The four handlers

Usable without the game, configured by `hobson/questions.yaml`:

```python
from hobson.handlers import Dice, Ledger, Ruling, Editor, ask_batch, load_questions

q = load_questions()
Dice(q).decide(state, actions={"ask-guard": "ask or tell the guard something",
                               "push-past": "shove or hit the guard", ...})
Ruling(q).decide(state, outcomes={"guard-suspicious": "...", "guard-waves-through": "..."})
Editor(q).decide(context, draft_a, draft_b)

decisions, ms, usage = ask_batch(state, [(Ledger(q), {"claims": claims}), (Ruling(q), {"parts": ("requires",), "requires": conds})])
```

| Handler | Question type | Asks |
|---|---|---|
| `Dice` | `choice` | which of these concrete actions is the player attempting (or, with no actions given, which category) |
| `Ledger` | `noul` per claim / object | has this been established; does the player hold this much of it |
| `Ruling` | `choice` + `noul` per condition | which prepared outcome happens; is each outcome's condition met |
| `Editor` | `score` per draft + `choice` both orders | how good is each draft (0–6); does the A/B pick survive the swap |

Each returns `Decision(name, value, p, confidence, unsure, latency_ms, via, ...)`; `noul`
confidence is `|2p − 1|`, as in the gauntlet. Handlers only flag `unsure`; the caller decides what
to do about it. `questions.yaml`:

```yaml
threshold: 0.6
dice:
  type: choice
  question: "Which of these is the player attempting?"
  # options: the current scene's `actions` (id -> says) from world/town.yaml
dice_categories:   # the original category dice, for --dice categories
  type: choice
  question: "Which kind of action is the player attempting?"
  options:
    move:   "Go somewhere, enter or leave a place"
    talk:   "Speak to a character: ask, persuade, greet, threaten verbally"
    take:   "Pick up, steal, buy or receive an item"
    use:    "Use, give or combine an item the player holds"
    attack: "Physical violence or force against a character or object"
    bluff:  "Claim something is true, or show or present something, to deceive"
    other:  "None of the above or unclear"
ledger_claim:
  type: noul
  question: "Has the following been established earlier in this story (in the ledger): {claim}?"
  criteria: {"true": "the ledger says so", "false": "the ledger does not say so"}
outcome:
  type: choice
  question: "Given the scene, the ledger and the action, which prepared outcome happens?"
grounding:
  type: noul
  question: "Does the ledger establish that the player currently holds {object} in at least the amount {amount}?"
  criteria: {"true": "the ledger says so", "false": "the ledger does not say so"}
  ask_for: [take, use, talk]
editor:
  type: score
  question: "How good is this paragraph as the next beat of the story: vivid, consistent with the rulings and the ledger, and in the same voice?"
  levels: ["useless", "poor", "weak", "acceptable", "good", "very good", "excellent"]
  tie: 0.2
  swap_question: "Which paragraph is the better next beat: vivid, consistent with the rulings and the ledger, and in the same voice?"
  swap_options: {A: "Draft A", B: "Draft B"}
```

The editor's levels are the gauntlet's Ep5 pointwise rubric
([ep5](https://github.com/Felina14/decider-gauntlet/blob/main/results/md/ep5_report.md)).

## Design changes, and the measurements behind them

Every comparison below was asked on the same states, side by side, in
[`results/md/wording_probe.md`](results/md/wording_probe.md) (`scripts/probe_wording.py`).

**The dice picks a concrete action, not a category.** This is the tool-selection shape: in the
gauntlet, Decider picked the right tool from 5 described options 98.6% of the time
([ep1](https://github.com/Felina14/decider-gauntlet/blob/main/results/md/ep1_report.md)). On 17
probe lines, the scene-action dice was right with confidence ≥ 0.6 on 16 and the category dice on 7
(judged on the action's type). All five demo lines: scene actions 5/5, categories 2/5. The miss is
"I tell the guard I'm the mayor's nephew", read as `ask-guard` (0.55) instead of `claim-rank`. The
`says` texts are short and player-voiced ("shove or hit the guard"). The category dice stays behind
`--dice categories`; its demo run (`results/referee_decider_categories_7.jsonl`) sent the dice to
Nova Lite on 4 of 5 turns and read the pass as `use`.

**`allowed` was dropped.** Decider was right and confident on 2/10 probe lines in both wordings
tried: it could not separate "fly over the town wall" from "shove the guard". Impossible attempts
are now an action in every scene's dice, `impossible` ("fly, use magic, or pay with something you
don't have"), whose only outcome is `not-possible-here` ("That cannot be done here; the attempt
fails", danger 0). That routed 4/4 impossible probe lines correctly (0.78–0.99). The first version
offered `not-possible-here` among the outcome options instead. Decider then picked it for ordinary
actions, including the guard shove at 0.89, and was right and confident on 3/9 lines (section 0b).

**Why danger is authored.** Decider's `score` never reached the threshold on danger in either
wording tried. Its highest confidence was 0.47, so every turn's danger went to Nova Lite. The
level examples did separate the attacks (P(level ≥ 3) for the shove: 0.69, against 0.50 with bare
levels), but never confidently:

| line | bare levels: E / conf, P(≥3) | levels with examples: E / conf, P(≥3) |
|---|---|---|
| I ask the guard what the town is called | 1.5 / 0.45, 0.26 | 1.4 / 0.40, 0.25 |
| I show him the pass the merchant gave me | 1.9 / 0.45, 0.33 | 1.9 / 0.40, 0.32 |
| I sort of edge towards the gate while humming | 1.6 / 0.45, 0.26 | 1.5 / 0.39, 0.27 |
| I draw my cloak around me and shove the guard aside | 2.5 / 0.45, 0.50 | 3.0 / 0.46, 0.69 |
| I punch the merchant | 2.6 / 0.47, 0.54 | 2.7 / 0.40, 0.59 |
| I buy the brass key | 1.8 / 0.43, 0.33 | 1.8 / 0.45, 0.31 |

So danger is authored on each outcome in the world file, and stakes routing reads it. What is
dangerous is then decided by which outcome Decider picks, which it is good at.

**The editor scores each draft alone.** The pairwise A/B pick, asked in both orders, disagreed
with itself on 6 of 15 turns in the comparison runs. Pointwise scoring takes the order out. Its scores
sit in a narrow band (about 2.4–3.3 of 6 in the demo runs), so many turns are ties and keep A. The
swap stays as a check; see the referee comparison for both rates.

**Ledger questions read the ledger, not your action.** With the action in the state, the claim
"the merchant gave the player a pass" came out 0.23. That is on the right side but unsure, and true
ledger facts dropped below the threshold too. On a state that stops at the ledger, 7/8 claims were
right and confident (with the action, 4/8). The miss, "the player holds a brass key" while the
merchant is *selling* one, stays unsure (0.54). The action is also labelled `PLAYER ACTION
(attempted now; anything it claims is not established by saying it)`.

**Conditional outcomes carry a `requires` condition**, decided by its own `noul`. If it is false,
`otherwise` replaces the effect and its `goto`/`adds`/danger do not apply. Without it,
"buy-key-if-three-coppers" would hand over the key whatever Decider thought of the coins.

Smaller wording changes from the spec's first draft: the category dice moved "show" from `use` to
`bluff` (the pass line became `bluff` 0.49 instead of `use` 0.43); `ledger_claim` and `grounding`
gained true/false criteria.

## Referee mode: Decider vs Nova Lite

`--referee nova` makes the same decisions from the same state with Nova Lite and JSON-constrained
prompts (one call for the dice + claims, one for the outcome + conditions + grounding, one
pairwise call for the editor). Everything else is identical, including claim extraction and
narration. From [`results/md/referee_compare.md`](results/md/referee_compare.md) (demo script,
seed 7, three runs each):

| | Decider referee | Nova Lite referee |
|---|---|---|
| ruling latency per turn, median | 2,667 ms (Decider 741 ms + Nova 1,905 ms) | 2,926 ms |
| Nova cost per 100 turns, rulings only | $0.0044 | $0.0131 |
| Nova cost per 100 turns, incl. narration | $0.0569 | $0.0899 |
| unsure rulings re-made by Nova Lite | 9 in 15 turns | n/a (Nova gives no confidence) |
| editor: swap (A/B vs B/A) disagreement | 6/15 (40%) | n/a (one pairwise call) |
| editor: pointwise ties (within 0.2) | 8/15 | n/a |
| editor: pointwise pick = swap pick, where both decided | 6/6 | n/a |

The Decider referee's Nova time is claim extraction (both referees do it) plus the 9 fallbacks.

Agreement on the turns where both were in the same scene: dice 12/12, outcome 6/12. Turn 2, the
bluff with a pass that was never established, is the one that matters. Decider ruled
`guard-suspicious` in 3/3 runs. Nova Lite waved the player into the market in 3/3, which is also
why turn 3 is never paired: after turn 2, the two referees are in different scenes. The other
disagreement is the guard's reply to an innocent question (`guard-asks-business` vs `guard-chats`).

Prices are on-demand list prices for us-east-1, read from the AWS Price List API on 2026-10-22: Nova
Lite $0.00006 / $0.00024 and Nova Pro $0.0008 / $0.0032 per 1K input / output tokens. Decider runs
locally and is counted at $0.

## What Hobson does NOT demonstrate

Long option lists: every choice here has at most ten options, because in the gauntlet Decider's
accuracy fell with list length and with the true option's position (100 options: 0.92 in the first
quartile, 0.81 in the last; [ep1](https://github.com/Felina14/decider-gauntlet/blob/main/results/md/ep1_report.md)).
The bundled HTTP server: it failed every request at two concurrent clients on MPS
([throughput](https://github.com/Felina14/decider-gauntlet/blob/main/results/md/throughput_mps-crash.md)),
so Hobson is single-process by design. Multilingual play: tool-selection accuracy dropped from 0.95
in English to 0.63 in Tamil, −32 points
([multilingual](https://github.com/Felina14/decider-gauntlet/blob/main/results/md/multilingual_r1.md)).
Routing by prompt difficulty: no router tried, Decider or Nova Lite, beat random routing
([ep3](https://github.com/Felina14/decider-gauntlet/blob/main/results/md/ep3_report.md)). Hobson
routes by stakes instead.

What the numbers say about Decider here, plainly. Given concrete options it is confident and right:
the scene action (0.92–0.98 on the first four demo beats), whether a claim is in the ledger, and the
outcome when the action fits one cleanly (guard-suspicious 0.85–0.87, guard-asks-business 0.94).
It is unsure where a person would hesitate too. The shove could end with you overpowered or
fleeing (0.02–0.09), and the jailer's reaction in beat 5 is close (0.12–0.15). Those go to Nova Lite. It was not useful as
a yes/no on possibility or as a danger score, so neither is asked. As an editor its pointwise scores
are flat and its pairwise pick moves with the order. All of this is in `results/`.

## Layout

```
hobson/
  cli.py          the terminal: python -m hobson play | compare
  game.py         the turn loop (shared with any front end)
  narrator.py     Nova: openings, drafts, claim extraction, fallback rulings, prices, meter
  referee_nova.py the Nova Lite baseline referee
  handlers/       Dice, Ledger, Ruling, Editor + Decision, ask_batch
  questions.yaml  every typed question
  state.py        Scene, World, Ledger, Turn, state_text()
  decider_local.py, nova.py, base.py, mdlog.py   copied from decider-gauntlet
  compare.py      referee comparison report
world/town.yaml   rules, six scenes: actions (the dice), outcomes with authored danger
demo/demo_turns.txt
scripts/probe_wording.py
results/          rows (*.jsonl) and markdown (md/)
```

MIT licence.
