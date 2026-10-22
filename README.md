# Hobson

**Nova writes; Hobson decides.** A text adventure with two brains. You type where the story begins,
anything at all, and what your character does, in your own words. **Amazon Nova** (Bedrock) invents
the setting, writes every scene and proposes what could happen next. **Strands Decider 2B**, running
locally, makes the calls: what kind of action that was, whether what you just claimed is actually
true in the story so far, which of the proposed outcomes follows, and, before a paragraph is
accepted, whether the narrator's own writing contradicts the facts the story has established.
Every ruling prints its confidence; below 0.6 Decider says so and Nova Lite takes that one call.

Nothing about the story is written in advance. There is no world file, no scene list, no prepared
outcomes. The only hand-written sentences in the game are five setting-free rules and the typed
questions in `hobson/questions.yaml`.

Entry for the AWS Builder Center *Agent Experience Hackathon: Strands Decider*. Declared decision
pattern: **`#guardrails`**: every claim the player makes, and every paragraph the narrator writes,
is checked against the ledger of established facts before it is allowed to act on the story. Also
uses the policy pattern (the dice classifies the action into fixed categories before anything else
happens), context/memory (the ledger) and stakes routing (Nova Lite or Pro by danger).

Named after the checkpoint, `strands-decider-2B-hobson-v19`, and after Hobson's choice: you can type
anything, but what is true is not up to you.

```
> I use the brass key my uncle gave me to open the locked cabinet by the lamp

  What did you try?                    use                              not sure · 0.57 → Nova answered: use
  Is that true in the story so far?    "the player claims to know their uncle"        No   0.80
  Is that true in the story so far?    "the player claims to hold a brass key …"      No   0.79
  What happens?                        unlock cabinet            not sure · 0.59 → Nova answered
                                       condition not met → it does not happen
  Does the story back that up?         "the player holds a brass key given by …"      No   0.78
  Do you actually have that?           brass key                                      No   0.72
  Who writes the next paragraph?       Nova Lite
```

_(Web run `hobson_web_decider_s11_20261022-214344`, rows in `results/referee_decider_11.jsonl`. A
lighthouse on the Kerala coast, 1962, a premise typed into the box. Nothing about a key, an uncle or
a cabinet existed anywhere before the player typed that line. That run predates contested routing
(step 7); the same turn now goes to Nova Pro.)_

## Run it

Apple Silicon (MPS). Decider runs in-process; Bedrock is Nova only (Lite and Pro), us-east-1.

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt          # first Decider call pulls the v19 weights (~4 GB)
export AWS_PROFILE=<your-profile> AWS_REGION=us-east-1

uvicorn hobson.web:app --port 8000        # then open http://localhost:8000 and type a premise
python -m hobson play --premise "a research station on Europa, two days after the supply ship failed to arrive"
python -m hobson play                     # blank premise: Nova invents one
python -m hobson play --referee nova --premise "..."         # Nova Lite decides instead (the baseline)
python -m hobson compare --seed 7 --repeats 3                # both referees → results/md/referee_compare.md
```

Every run appends one JSON row per turn to `results/referee_<mode>_<seed>.jsonl` (each ruling with
its probabilities and confidence, the candidate outcomes Nova proposed, both drafts, the pick,
latency, tokens per Nova tier, cost) and writes `results/md/<run>.md` when the game ends.

## One turn

1. **Claims.** Nova Lite lists what your action relies on having been established ("the player
   holds a brass key given by their uncle") and any object it names as held, shown or used.
2. **Decider, call A, against the ledger alone** (the state stops before your action, so your own
   wording cannot vouch for itself): one `noul` per claim, one `noul` per named object.
3. **Decider, call B, the dice:** a `choice` over fixed, setting-free categories (move, talk, take,
   use, attack, bluff, examine, impossible, other). The policy pattern: the category decides what
   is checked next and what Nova is asked to propose.
4. **Candidates.** Nova Lite proposes four outcomes for *this* action in *this* state, given the
   claim rulings, each with a one-line effect, a danger 0–5, optionally a place it moves the player
   to, a ledger condition it depends on, and the facts it would establish. `impossible` actions
   skip this: their one outcome is that it does not happen.
5. **Decider, call C, the outcome:** a `choice` over the candidates, on a state that also carries
   the claim rulings. If the picked outcome has a condition, a `noul` checks it against the ledger;
   if false, the attempt fails and nothing of it happens.
6. **Unsure → Nova Lite.** Any decision with confidence below 0.6 is re-asked of Nova Lite with the
   same question and options, and shown as `not sure · 57% → Nova answered`.
7. **Routing.** Danger 0–2 → Nova Lite writes, 3–5 → Nova Pro. A *contested* turn (any claim or
   holding ruled false, or a condition not met) also goes to Pro: the writer has to push back
   against the player's own words, and Lite does that badly.
8. **Two drafts, the guard, the editor.** Nova writes two drafts. Decider checks each against the
   ledger and the ruling with one concrete `noul` per thing that could go wrong (did the false claim
   come true, did the player use the item they do not hold, did the ruled outcome actually happen).
   A failing draft is dropped; if both fail, Nova Pro rewrites with the specific problem, twice at
   most. A paragraph the guard still rejects is shown but never feeds the ledger. Between two
   passing drafts, the editor scores each alone (0–6) and the higher wins.
9. **Ledger.** The accepted paragraph's new facts and the outcome's facts are appended; facts the
   paragraph lists as `NOW FALSE` are retired. A `moves_to` outcome makes Nova write the next scene.

## The five handlers

Usable without the game, configured by `hobson/questions.yaml`:

```python
from hobson.handlers import Dice, Ledger, Ruling, Continuity, Editor, ask_batch, load_questions
from hobson.handlers.continuity import checks_for

q = load_questions()
Dice(q).decide(state)                                                    # which category
Ruling(q).decide(state, outcomes={"guard-suspicious": "...", "guard-waves-through": "..."})
Continuity(q).decide(ledger_state, checks=checks_for(decisions, met, outcome), paragraph=draft)
Editor(q).decide(context, draft_a, draft_b)
decisions, ms, usage = ask_batch(ledger_state, [(Ledger(q), {"claims": claims, "holdings": holdings})])
```

| Handler | Question type | Asks |
|---|---|---|
| `Dice` | `choice` | which kind of action the player is attempting (fixed categories) |
| `Ledger` | `noul` per claim / object | has this been established; does the player hold this much of it |
| `Ruling` | `choice` + `noul` per condition | which proposed outcome happens; is its condition met |
| `Continuity` | `noul` per check | does the paragraph show a false claim as true, an unheld item used, the ruled outcome happening |
| `Editor` | `score` per draft + `choice` both orders | how good is each draft (0–6); does the A/B pick survive the swap |

Each returns `Decision(name, value, p, confidence, unsure, latency_ms, via, ...)`; `noul`
confidence is `|2p − 1|`. Handlers only flag `unsure`; the caller decides what to do about it.

### The reusable pattern: the ledger guard

The typed question, its option set and the wiring, as the hackathon asks for:

```yaml
ledger_claim:
  type: noul
  question: "Has the following been established earlier in this story (in the ledger): {claim}?"
  criteria: {"true": "the ledger says so", "false": "the ledger does not say so"}
```

Wiring (`hobson/game.py`): the question is asked on a state that ends at the ledger, *without* the
user's message, so the message cannot vouch for itself. The answer is written into the brief the
generator must honour, and the same check is turned round on the generator's output
(`Continuity`): "does the PARAGRAPH show this claim as true?" Anything that fails never reaches the
record. Usage note: use it anywhere a generator is allowed to act on what a user asserts (a
support agent told "I already paid", a game told "the merchant gave me a pass"); keep the record
in plain sentences; ask the claim against the record alone.

## Referee mode: Decider vs Nova Lite

`--referee nova` makes the same decisions from the same states with Nova Lite and JSON-constrained
prompts. World generation, candidate outcomes, claim extraction and narration are the same code. From
[`results/md/referee_compare.md`](results/md/referee_compare.md) (`demo/demo_turns.txt` on the
Kerala-lighthouse premise, seed 7, three runs each):

| | Decider referee | Nova Lite referee |
|---|---|---|
| ruling latency per turn, median | 7,481 ms (Decider 1,899 ms + Nova 5,165 ms) | 7,515 ms |
| Nova cost per 100 turns, rulings only | $0.0268 | $0.0376 |
| Nova cost per 100 turns, incl. world and narration | $0.1916 | $0.1987 |
| claims checked against the ledger / ruled not established | 22 / 11 | 23 / 4 |
| paragraphs checked by the guard / swapped or rewritten | 15 / 6 | 15 / 4 |
| unsure rulings re-made by Nova Lite | 47 in 15 turns | n/a (Nova gives no confidence) |
| editor: A/B vs B/A swap disagreement | 7/11 | n/a |

**The bluff** (turn 2: a brass key, an uncle's gift and a cabinet that exist nowhere in the story).
Decider ruled "the player holds a brass key" not established in 3/3 runs (0.75–0.81). In one run
Nova picked the `unlock-cabinet` outcome after Decider was unsure (0.34). But Decider ruled its
condition, holding the key, not met (0.80), so it did not happen. Nova Lite as referee ruled the
player *holds* a brass key in 3/3 runs, and in one the effect was "The brass key fits perfectly,
and the locked cabinet door swings open."

**Agreement.** On the 11 turns where both referees were in the same scene, the dice agreed 11/11.
The outcomes agreed 0/11 by label, which means little. Nova proposes fresh candidates every run, so
the referees choose from different lists, and several pairs are the same event under two names
(`key-does-not-fit` vs `key-doesnt-fit`).

**Latency.** Most of a turn's ruling time is Nova's: proposing candidates, extracting claims and,
with Decider as referee, the fallbacks. Decider's own share is about 1.9 s per turn.

Prices are on-demand list prices for us-east-1, read from the AWS Price List API on 2026-10-22: Nova
Lite $0.00006 / $0.00024 and Nova Pro $0.0008 / $0.0032 per 1K input / output tokens. Decider runs
locally and is counted at $0.

## What the numbers say about Decider here

- **Strong:** whether a claim is in the ledger, which is the guard's whole job. It ruled the bluff's
  key not established in 3/3 runs; Nova Lite ruled it established in 3/3.
- **Unsure where a person would hesitate:** which kind of action "use the key my uncle gave me" is,
  or which of four freshly written outcomes follows. Those go to Nova Lite: 47 times in 15 turns.
- **Partial:** the continuity guard on its own prose. On turn 2 of two Decider runs, the kept
  paragraph still failed a check after two rewrites. Both times a Nova-judged item decided it, and
  that paragraph's facts were kept out of the ledger.
- **Weak:** the editor. Pointwise scores sit in a narrow band and tie often, and the A/B pick
  disagreed with itself 7 times in 11.

## What this version replaced

The first build (22 Oct, morning) had a hand-authored world: six scenes, prepared outcomes and a
dice over each scene's concrete actions (`world/legacy/town.yaml`). It made Decider look good and
proved little: a judge could fairly ask why an LLM could not pick from a list I wrote. This version
generates everything and keeps Decider for the two jobs a generator cannot be trusted with:
judging the player's claims and judging its own prose against the record.

That build's probe (`scripts/legacy/probe_wording.py`, results in
[`results/legacy/md/wording_probe.md`](results/legacy/md/wording_probe.md)) and its runs (rows and
reports in `results/legacy/`) set three things this version keeps:

- **Ledger questions read the ledger, not the action.** With the action in the state, true ledger
  facts dropped below the threshold and the fake "pass from the merchant" came out unsure. On the
  ledger alone, 7/8 test claims were right and confident; with the action, 4/8.
- **Impossibility is a dice category, not an outcome or a yes/no.** As a yes/no (`allowed`), Decider
  was right and confident on 2/10 probe lines. Offered as one outcome among others, it picked
  `not-possible-here` for ordinary actions (a guard shove at 0.89; 3/9 right). As a dice action it
  sent 4/4 impossible lines there.
- **Danger is not scored.** As a 0–5 `score`, Decider's confidence never passed 0.47 in any wording.
  Danger now comes with each candidate outcome and follows from which outcome Decider picks.

One thing did not carry over. That build's dice picked from each scene's concrete actions, which
was right and confident on 16/17 probe lines against 7/17 for categories. A generated world has no
authored action list, so the dice is back to fixed categories, and it is unsure more often.

## What Hobson does NOT demonstrate

Long option lists: no choice here has more than nine options, because in the gauntlet Decider's
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

## Layout

```
hobson/
  cli.py          the terminal: python -m hobson play | compare
  game.py         the turn loop (shared with any front end)
  narrator.py     Nova: openings, drafts, claim extraction, fallback rulings, prices, meter
  referee_nova.py the Nova Lite baseline referee
  handlers/       Dice, Ledger, Ruling, Continuity, Editor + Decision, ask_batch
  questions.yaml  every typed question
  state.py        Scene, World (premise + rules), Ledger (add/retire), Turn, state_text()
  decider_local.py, nova.py, base.py, mdlog.py   copied from decider-gauntlet
  compare.py      referee comparison report
  web.py          FastAPI web view; static/ the page, visuals.js/.css, scenes/ (six line drawings)
world/README.md   nothing is read from here any more; legacy/town.yaml is the first build's town
demo/             demo turns, narration, voice-over, recorder and assembler for the video
scripts/         draw_scenes.py (the six banners); legacy/probe_wording.py
results/          rows (*.jsonl) and markdown (md/); legacy/ holds the first build's
```

MIT licence.
