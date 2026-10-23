# Hobson

**A text adventure where the thing deciding what is true cannot write a word.**

Type a premise — any sentence. **Amazon Nova** on Bedrock invents the place, the people and the
facts the story opens with. Then type what you do, in your own words, and Nova writes what happens
next. Everything the story establishes lands in one list, **the ledger**, and that list is the only
memory the game has.

The model that reads the ledger is not Nova. It is **Strands Decider 2B**, running locally, and it
cannot produce prose. It reads a state and a typed question and returns a choice, a yes or no, or a
score, each with a calibrated confidence. It rules on what kind of action you attempted, whether
every claim your action leans on is actually established, whether you hold what you named, which of
Nova's proposed outcomes follows, and — before any paragraph is accepted — whether Nova's own
writing contradicts the record. Below 0.6 confidence it says "not sure" out loud and hands that one
call to Nova Lite.

It cannot be talked into anything, because it cannot talk.

Nothing about the story is written in advance. There is no world file, no scene list, no prepared
outcomes. The only hand-written English in the game is five setting-free rules and the typed
questions in [`hobson/questions.yaml`](hobson/questions.yaml).

> **Demo video** · [2:50, narrated](https://d3qpn17qic87hh.cloudfront.net/hobson/index.html)
> **Reusable pattern** · [`patterns/ledger_guard.py`](patterns/ledger_guard.py)

Entry for the AWS Builder Center *Agent Experience Hackathon: Strands Decider*. Declared decision
pattern **`#guardrails`**: every claim the player makes, and every paragraph the narrator writes, is
checked against the ledger before it is allowed to act on the story. It also exercises **policy**
(the dice classifies the action into fixed categories before anything else happens),
**context/memory** (the ledger is the only context injected) and **model routing** (Nova Lite or Pro
by stakes).

Named after the checkpoint, `strands-decider-2B-hobson-v19`, and after Hobson's choice: you can type
anything, but what is true is not up to you.

---

## The problem it exists for

Give a language model a story and it will believe whatever you tell it. On an early build I typed a
bluff into my own game:

```
> I use the brass key my uncle gave me to open the locked cabinet by the lamp
```

No key, no uncle, no cabinet had ever existed in that story. The model wrote back:

> The brass key, gripped tightly in your hand, fails to engage with the lock. You turn it this way
> and that, but the key simply does not fit.

That reads like a refusal. It is not. The cabinet stays shut, but the key is now in the player's
hand, and from the next turn on it can be used on other locks. The model writing the world was also
the model deciding what was true in it, and storytelling won.

Hobson takes the deciding away from the writer. Here is the same turn today:

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
lighthouse on the Kerala coast, 1962, a premise typed into the box. That run predates contested
routing (step 7); the same turn now goes to Nova Pro.)_

**This is not a games problem.** Anywhere an agent acts on what a user simply asserts — a refund, an
insurance claim, an access request, a support escalation — the same failure is available. That is why
the guard ships separately; see [the reusable pattern](#the-reusable-pattern-the-ledger-guard).

---

## What it does

| | |
|---|---|
| **Any premise** | A lighthouse in 1962, a 3am payments outage, a generation ship. Nova builds the world; no authored content of any kind. |
| **A ledger as the only memory** | Plain sentences. Nothing is true because it sounds true — only because it is in the ledger. |
| **Claims ruled against the record alone** | The claim question is asked on a state that stops at the ledger, with the player's sentence deleted, so the sentence cannot vouch for itself. |
| **The narrator guarded too** | The same question is turned on Nova's own paragraph before it is allowed to count. |
| **Calibrated confidence as control flow** | Below 0.6 Decider says "not sure" on screen and hands that one call to Nova Lite. |
| **Stakes routing** | Danger 0–2 → Nova Lite writes; 3–5, or any contested turn → Nova Pro. |
| **Two drafts, scored** | Decider checks both against the ledger, then scores them; the higher wins. |
| **The turn shown as it happens** | `POST /turn_stream` pushes each real milestone — claims extracted, each claim ruled, writer chosen — so the page is never a frozen seven seconds. |
| **Your own sentence marked up** | The words the action leaned on are underlined where you typed them: red where the ledger does not hold them, green where it does. |
| **A drawing for every scene** | Composed in code from the scene's own words ([`hobson/scene_art.py`](hobson/scene_art.py)): a motif from eleven, plus sea, rain or stars, seeded by a hash. Deterministic, offline, free. |
| **Everything logged** | One JSON row per turn: every ruling with its probabilities and confidence, the candidate outcomes, both drafts, the pick, latency, tokens and cost. |

---

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
python -m patterns.example_refund_desk                       # the guard on an agent that is not a game
```

Every run appends one JSON row per turn to `results/referee_<mode>_<seed>.jsonl` and writes
`results/md/<run>.md` when the game ends.

---

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
   to, a ledger condition it depends on, and the facts it would establish. When the turn leans on
   something absent, Hobson inserts its own `it-is-not-there` candidate **first**, because option
   order moves the pick. `impossible` actions skip this step.
5. **Decider, call C, the outcome:** a `choice` over the candidates, on a state that also carries
   the claim rulings. If the picked outcome has a condition, a `noul` checks it against the ledger;
   if false, the attempt fails and nothing of it happens.
6. **Unsure → Nova Lite.** Any decision below 0.6 is re-asked of Nova Lite with the same question
   and options, and shown as `not sure · 57% → Nova answered`.
7. **Routing.** Danger 0–2 → Nova Lite writes, 3–5 → Nova Pro. A *contested* turn (any claim or
   holding ruled false, or a condition not met) also goes to Pro: the writer has to push back
   against the player's own words, and Lite does that badly.
8. **Two drafts, the guard, the editor.** Decider checks each draft against the ledger with one
   concrete `noul` per thing that could go wrong. A failing draft is dropped; if both fail, Nova Pro
   rewrites with the specific problem, twice at most. A paragraph the guard still rejects is shown
   but never feeds the ledger. Between two passing drafts, the editor scores each alone (0–6).
9. **Ledger.** On an uncontested turn the accepted paragraph's new facts and the outcome's facts are
   appended, and facts listed as `NOW FALSE` are retired. **On a contested turn the prose
   establishes nothing** — only the outcome's own additions survive, and those are screened (below).

---

## The guardrail, in detail

Four things stand between a user's assertion and the record.

**1. The claim is asked against the ledger alone.** The state stops before the action. Measured
while building: on a state that ends at the ledger, 7 of 8 test claims were right and confident;
with the action included, 4 of 8.

**2. Nova is told what is absent** before it proposes outcomes, and an honest `it-is-not-there`
candidate is offered first.

**3. A contested turn records nothing from the prose.** Only the outcome's own `adds` survive.

**4. A deterministic gate screens those.** A model-based screen was asked whether a proposed fact
relied on something absent, and it let this through:

```
You do not have the key to open the locked cabinet.
```

That is a denial — and it installs *the cabinet* in the ledger as a thing that exists. So a string
match now runs in front of the model: any fact naming an absent thing by its head noun is refused
without asking anyone ([`hobson/handlers/continuity.py`](hobson/handlers/continuity.py)).

```
DROP(key)    You do not have the key to open the locked cabinet.
DROP(key)    The key does not fit the cabinet.
DROP(uncle)  Your uncle never gave you anything.
keep         The lamp is lit and set on the floor.      ← real, stays
keep         The storm grows worse and the stairs are wet.
```

Whatever survives all four, plus the model screen, fails closed: a fact that is not clearly clear of
the absent things does not get written.

---

## Does it generalise?

Every comparison number below comes from one premise, so the design was tested on others. See
[`results/md/generalisation.md`](results/md/generalisation.md).

- **A 3am production incident at a payments company in Bengaluru.** Nova invented a colleague named
  Rajiv and recorded him. The bluff — *"I use the production root token my manager gave me last
  week"* — was refused on all three claims at 81%, 82%, 83%; `new_facts` empty.
- **A generation ship, where the bluff was not an object at all** — *"the captain already signed my
  emergency override"*. Refused at 81%. The ledger check does not care whether the lie is a thing
  you could be asked to produce or a claim about who authorised what.
- **A Chennai hospital night shift**, live: *"I open the drug cabinet with the key the senior gave
  me."* **key** and **senior** both came back absent, in a world forty seconds old.

Those runs also exposed the classifier weakness honestly: on both turns the nine-way dice was under
threshold and went to Nova.

---

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
record. Usage note: use it anywhere a generator is allowed to act on what a user asserts (a support
agent told "I already paid", a game told "the merchant gave me a pass"); keep the record in plain
sentences; ask the claim against the record alone.

---

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

---

## The pattern on a Strands agent that is not a game

The ledger guard is the piece worth lifting, so it also ships as a standalone
`InterventionHandler` in [`patterns/ledger_guard.py`](patterns/ledger_guard.py) — one file,
depending on nothing in this repository.

```python
from strands import Agent
from patterns.ledger_guard import LedgerGuard

guard = LedgerGuard(
    record=lambda: RECORD,                      # the established facts, one sentence each
    claims={"issue_refund": lambda i: [         # what this call takes for granted
        f"order {i['order_id']} was returned by the customer",
        f"order {i['order_id']} was delivered",
    ]},
)
agent = Agent(model=..., tools=[lookup_order, issue_refund], interventions=[guard])
```

Before `issue_refund` runs, each statement goes to Decider as one `noul` against the record,
and a statement the record does not support turns the call into a `Deny` whose reason tells the
model what is missing. Three details do the work:

- **The user's message is not in the state.** Decider reads the record and nothing else
  (`LedgerGuard.state()`). With the message in, the user's own phrasing — "the key my uncle gave
  me", "the one I already returned" — pulls the answer towards yes. Measured while building the
  game: on a state that stops at the record, 7 of 8 claims were right and confident; with the
  action included, 4 of 8.
- **It is three-way, and fails closed by default.** Confidently in the record proceeds; confidently
  absent is denied; below the 0.6 line is neither, and `on_unsure` decides whether that denies (the
  default), asks a person through the framework's `Confirm` action, or allows. The margins are real:
  on the refund desk an invented return was refused at 0.78, while true claims passed at 0.66 to
  0.78. True claims clear the line, but not by much, which is exactly when handing the call to a
  human beats guessing in either direction. `on_error` returns `"deny"`.
- **The engine is cached.** The first build reloaded the checkpoint per instance, 3,496 ms a call.
  A module-level cache (`get_engine`) brought that to 233–268 ms.

[`patterns/example_refund_desk.py`](patterns/example_refund_desk.py) is a runnable refund desk.
In the sharpest of three observed runs, **Nova called `issue_refund` immediately, with no lookup at
all** — its reasoning: *"The user has provided the order ID and the amount, so I can proceed."* The
guard refused it in **233 ms** (*"order A-4471 was returned by the customer"*, not established,
**0.78**); only then did Nova look up the order, find no return, and ask for a receipt. A genuine
return is allowed in 268 ms.

Across those three runs the agent behaved differently each time: once it looked the order up first
and the guard never fired; twice it had to refuse, and in the clearest of those Nova had not
looked the order up at all. **The guard is not an improvement
on a model that was already careful — it is what makes the behaviour reliable**, because the model
alone is a coin toss. Both behaviours are recorded in the example's docstring rather than only the
flattering one.

It is the same check the game runs on the player, and the same one it runs on the narrator's own
paragraphs. A record, and a model with no stake in the story being allowed to say what is in it.

---

## What this version replaced

The first build (22 Oct, morning) had a hand-authored world: six scenes, prepared outcomes and a
dice over each scene's concrete actions (`world/legacy/town.yaml`). It made Decider look good and
proved little: a judge could fairly ask why an LLM could not pick from a list I wrote. This version
generates everything and keeps Decider for the two jobs a generator cannot be trusted with:
judging the player's claims and judging its own prose against the record.

That build's probe (`scripts/legacy/probe_wording.py`, results in
[`results/legacy/md/wording_probe.md`](results/legacy/md/wording_probe.md)) and its runs set three
things this version keeps:

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
  game.py         the turn loop (shared with any front end), on_phase milestones
  narrator.py     Nova: openings, drafts, claim extraction, fallback rulings, prices, meter
  referee_nova.py the Nova Lite baseline referee
  handlers/       Dice, Ledger, Ruling, Continuity, Editor + Decision, ask_batch
  questions.yaml  every typed question
  state.py        Scene, World (premise + rules), Ledger (add/retire), Turn, state_text()
  scene_art.py    a line drawing for any scene, composed from its own words
  web.py          FastAPI: /start, /turn, /turn_stream (NDJSON), /scene/<k>.svg
  static/         the page, visuals.js/.css (verdict card, confidence dials, marked-up sentence)
  decider_local.py, nova.py, base.py, mdlog.py   copied from decider-gauntlet
  compare.py      referee comparison report
patterns/         the ledger guard as a standalone Strands InterventionHandler, + a refund-desk example
demo/             demo_turns.txt: the five scripted turns the referee comparison runs
results/          rows (*.jsonl) and markdown (md/); legacy/ holds the first build's
```

MIT licence.
