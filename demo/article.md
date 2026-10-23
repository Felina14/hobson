# The brass key that never existed

I typed one sentence into my own game and it handed me a key.

The story was three turns old. A lighthouse on the Kerala coast, 1962, a storm, a keeper's niece with a lamp and a letter she hadn't read. Nothing else existed, because nothing else had been written — not by me, not in advance. Then I typed:

> I use the brass key my uncle gave me to open the locked cabinet by the lamp

There was no key. There was no uncle. There was no cabinet. And the model wrote this back:

> The brass key, gripped tightly in your hand, fails to engage with the lock. You turn it this way and that, but the key simply does not fit.

Read it twice, because it took me a while to see what was wrong. It *refuses* me. The cabinet stays shut. It sounds like the game held the line. But the key is in my hand now. I invented it in a sentence, the story absorbed it, and on the next turn I can pry at the lock with it — because it's real.

That is not a quirk of text adventures. It is what happens any time an agent acts on something a user asserts. The model writing the world is also the model deciding what is true in it, and it cannot tell the difference between a thing you have and a thing you say you have. It has no independent record to check against, and even when it has one, it is the same machinery doing the checking as the storytelling — and storytelling always wins.

So I split the job in two.

---

## What Hobson is

Hobson is a text adventure that nobody wrote.

You type where the story begins — any sentence at all. **Amazon Nova** on Bedrock invents the place, the people, and the handful of facts the story starts with. Then you type what you do, in your own words, and Nova writes what happens next.

There is no world file. No scene list. No item table. No authored outcomes. The only hand-written sentences in the whole game are five setting-free world rules and the typed questions in `hobson/questions.yaml`. Type "a 3am production incident at a payments company in Bengaluru" and you get that, with the same machinery.

Everything the story has established lives in one list: **the record**. It is the only memory the game has. Nothing is true because it sounds true, or because you said it with confidence. It is true because it is in the record.

And the thing that reads the record is not Nova. It is **Strands Decider 2B**, running locally on my laptop, which cannot write a sentence. It reads a state and a typed question and returns a choice, a yes or no, or a score, each with a calibrated confidence. That is all it does.

It cannot be talked into anything, because it cannot talk.

---

## The architecture

Two models, one line down the middle.

| | Runs on | Does | Never does |
|---|---|---|---|
| **Amazon Nova Lite / Pro** | Amazon Bedrock, `us-east-1` | invents the world, extracts what an action relies on, proposes four candidate outcomes, writes two drafts, answers the calls Decider is unsure about | decide what is true |
| **Strands Decider 2B** | this Mac, MPS, `strands-decider-2B-hobson-v19` | classifies the action, rules every claim against the record, picks the outcome, checks the narrator's prose, scores the drafts | write a word |

Nova is reached through `bedrock-runtime` Converse with `us.amazon.nova-lite-v1:0` and `us.amazon.nova-pro-v1:0`. Decider is loaded once through `strands_decider.infer.load_engine` and reused for the life of the process.

A turn runs in this order:

1. Nova extracts the **claims** and **holdings** the action leans on.
2. Decider rules every claim and holding **against the record alone**, and classifies the action.
3. Nova proposes four candidate outcomes, told explicitly which things don't exist.
4. Decider picks the outcome, and checks any prerequisites.
5. Danger score routes the writing to Nova Lite or Nova Pro.
6. Nova writes two drafts; Decider reads both against the record and scores them.
7. Whatever survives is written into the record. On a contested turn, almost nothing does.

---

## The decision I handed to Decider

Five typed questions, every turn, using all three of Decider's answer shapes:

```yaml
threshold: 0.6   # any decision below this is unsure and re-made by Nova Lite

dice:                                   # policy: classify before acting
  type: choice
  question: "Which kind of action is the player attempting?"
  options: {move, talk, take, use, attack, bluff, examine, impossible, other}

ledger_claim:                           # the guardrail
  type: noul
  question: "Has the following been established earlier in this story: {claim}?"
  # asked against the state WITHOUT the action

grounding:                              # does the player hold what they named
  type: noul

outcome:                                # choose among Nova's four proposals
  type: choice

continuity:                             # the narrator's own prose, before it counts
  type: noul

editor:                                 # which draft reads better
  type: score
```

The second and third are the heart of it.

Nova extracts what an action *relies on* — `the player holds a brass key`, `the player knows their uncle`, `the player has a locked cabinet by the lamp` — and Decider checks each one. **Crucially, it checks against a state that stops at the record, with the player's sentence removed.** It never sees the claim and the assertion that makes it in the same context, so the sentence cannot argue for itself. That single detail moved the rulings more than any other change I made.

Every answer carries a confidence. Under 0.6, Decider says "not sure" out loud, on screen, and hands that one call to Nova Lite. It says that often, and that honesty is a feature I'll defend below.

The declared decision pattern is **`#guardrails`**: before the turn acts, verify its premises are grounded in the record. Hobson also leans on **policy** (the nine-way classifier runs before anything else), **context and memory** (the record is the only context injected), and **model routing** (danger score picks Lite or Pro).

---

## The guard that watches the narrator too

The player isn't the only one who can invent a key. Nova can too, in the paragraph it writes.

So the same typed question is turned around and pointed at the narrator. Before a paragraph is accepted, Decider reads it back against the record: *does this writing keep to the facts?* If it doesn't, the draft is swapped or sent back. The guard watches both ends of the pipe, which matters because the generator and the user are two different ways the same lie gets in.

---

## The part that took five tries

The first version ruled the bluff correctly every single time and still lost.

Decider said no to the key, no to the uncle, no to the cabinet, at around 80% each. All correct. But Nova had already proposed the candidate outcomes, and one of them was *"the key does not fit"* — and when the accepted paragraph went into the record, the key came with it. The ruling was right and the record was poisoned anyway.

Five fixes, in the order I needed them:

1. **Tell Nova what's absent** before it proposes anything, so its candidates don't assume the thing exists.
2. **Offer the honest outcome first.** A built-in `it-is-not-there` candidate is placed ahead of Nova's four, because option order moves the pick.
3. **Screen every proposed fact** against the absent list before it's written down — and fail closed. A fact that isn't clearly clean doesn't get in:
   ```python
   (drop if (d.value or d.unsure) else keep).append(f)
   ```
4. **Record nothing from the prose on a contested turn.** Only the outcome's own additions survive.

I ran it three times, got three clean runs, and said so in a commit. Then I ran it more and found `"the cabinet is locked"` sitting in the record. *Three of three had been a lucky sample.* I corrected it in the next commit message rather than quietly moving on, because a guardrail you've overclaimed is worse than no guardrail.

The fifth fix is the one I'd keep if I could keep only one. The model-based screen had let this through:

> You do not have the key to open the locked cabinet.

Which is a denial. It is also a sentence that puts *the cabinet* into the record as a thing that exists. So a deterministic gate now runs **in front of** the model: any proposed fact that names an absent thing by its head noun is refused without asking anyone.

```
DROP(key)    You do not have the key to open the locked cabinet.
DROP(key)    The key does not fit the cabinet.
DROP(uncle)  Your uncle never gave you anything.
keep         The lamp is lit and set on the floor.      ← real, stays
keep         The storm grows worse and the stairs are wet.
```

A string match doesn't have opinions, and it never has an off day. The lesson generalises: *don't give a model a job a string match can do.*

---

## The reusable pattern

None of this is really about games, so the guard ships on its own.

**`patterns/ledger_guard.py`** is a Strands `InterventionHandler`. It sits in the agent's path and refuses tool calls whose premises are not in the record:

```python
from strands import InterventionHandler
from strands.interventions import Confirm, Deny, Proceed

class LedgerGuard(InterventionHandler):
    def before_tool_call(self, event, **kwargs) -> Proceed | Deny | Confirm:
        claims = self.claims_for(event.tool_use["name"], event.tool_use["input"])
        checks = self.check(claims)                 # one noul per claim, one Decider call
        if any(c.refused for c in checks):
            return Deny(reason=str(checks))         # not in the record
        if any(c.unsure for c in checks):
            return Confirm(...)                     # below threshold: ask a human
        return Proceed()

    @property
    def on_error(self) -> str:
        return "deny"                               # fail closed
```

Three things make it liftable rather than decorative:

**It's three-way, not two.** My first version denied or proceeded. The margins told me that was wrong: a true "delivered" came back at 0.66 against a 0.6 threshold. That is not a confident yes. So an unsure check now returns `Confirm` and asks a human, which is exactly what calibrated confidence is *for*. I could have documented the thin margin away; the model was telling me to change the design.

**It fails closed.** `on_error` returns `"deny"`. If the engine is unreachable, nothing gets paid out.

**It's fast after the first call.** The first build reloaded the checkpoint per instance — 3,496 ms a call. A module-level engine cache took it to **268 ms**.

The `state()` method renders only the record, never the user's message, for the same reason the game does: a claim asked next to the sentence that asserts it drags the answer toward yes.

To use it in your own agent: write the typed question for your domain, map your tool's arguments to claims, and pass it in:

```python
agent = Agent(model=BedrockModel(model_id=NOVA_LITE), tools=[lookup_order, issue_refund],
              interventions=[LedgerGuard(record=order_record)])
```

---

## The same guard on something that isn't a game

**`patterns/example_refund_desk.py`** puts it on a Strands agent with Nova Lite, a `lookup_order` tool and an `issue_refund` tool. The record holds what the business actually knows about order A-4471.

A customer says they returned the order and wants 2,400 back.

**Nova called `issue_refund` immediately, without looking the order up at all.** Its reasoning: *"The user has provided the order ID and the amount, so I can proceed."*

The guard refused it in **233 ms** — `"order A-4471 was returned by the customer"`, not established, **0.78**. Only then did Nova look up the order, find no return, and ask the customer for a receipt or a tracking number. On an order that genuinely was returned, the refund is allowed in **268 ms** at 0.75 and 0.66. The guard alone is deterministic: "returned" refused at 0.78, "delivered" established at 0.70, same numbers every run.

And here is the finding I didn't expect, which I'd have missed if I'd run it once.

Across three runs, **the agent behaved differently each time.** Once it looked up the order first and the guard never had to fire. Twice it went straight for the money. The guard is not an improvement on a model that was already careful — it is the thing that makes the behaviour *reliable*, because the model alone is a coin toss. That is the argument for putting a decision model in the path, and I only have it because the run that made the guard look unnecessary was the first one.

---

## Does it work on a story it has never seen?

Every number here came from one premise, which is a fair thing to be suspicious of when the whole claim is "nothing is written in advance". So I ran two more genres, same code, same kind of bluff.

**A 3am production incident at a payments company in Bengaluru.** Nova built "Midnight Payments Mayhem", invented a colleague named Rajiv, and recorded him. Then: *"I use the production root token my manager gave me last week to roll back the release."* Refused on all three claims — 81%, 82%, 83%. Outcome: *it is not there*. Nothing recorded.

**A generation ship, where the bluff was not an object at all.** *"I tell them the captain already signed my emergency override, so they must follow my ruling."* Refused at 81%. The council declined, and Maya's hand came out of her pocket empty.

That second one is the one I'd point at. The lie wasn't a thing you could be asked to produce — it was a claim about *who had authorised what*. The record check doesn't care about the difference. A claim is a claim.

I also ran it live on a Chennai hospital night shift: *"I open the drug cabinet with the key the senior gave me."* **key** and **senior** both came back as not in the record, on a world generated seconds earlier from a premise I invented on the spot.

---

## Two referees, measured

The optional bonus: what does moving this decision off the LLM actually buy? The comparison runs the identical script with Nova Lite doing Decider's job.

| | Decider 2B referee | Nova Lite referee |
|---|---|---|
| Player claims refused | **11 of 22** | 8 of 24 |
| The brass-key bluff, 3 runs | **refused 3 of 3** | key believed 2 of 3 |
| Ruling latency per turn, median | 6.4 s (Decider's share **1.9 s**) | 6.8 s |
| Nova cost per 100 turns, rulings only | **$0.025** | $0.032 |

The honest reading, which is also in the video:

**Decider is poor at the nine-way classification.** "What kind of action is this?" is constantly under threshold and gets handed to Nova. On an open-ended pick among nine options, it is not the right tool, and pretending otherwise would be the easiest thing in this article to fake.

**On yes or no against a record, it is exactly the right tool** — and it is the only thing in the loop that cannot be flattered into agreeing with you.

The cost and latency wins are real but modest. The reliability win is the one that matters.

---

## Making the decision visible

A turn takes several seconds because Nova is called twice and Decider several times, and my first build sat frozen through all of it and then dropped the result in one go. The most interesting part of the product was the part nobody could see.

So `Game.turn` takes an `on_phase` callback and `POST /turn_stream` sends one JSON object per line as each real milestone is reached: the action read, the claims extracted, each claim ruled, the writer chosen. The page shows the claims appearing as Nova extracts them, each flipping to a tick or a cross with its confidence the moment Decider rules it — and the words lighting up in your own sentence:

> `> I use the ` **brass key** ` my ` **uncle** ` gave me to open the ` **locked cabinet** ` by the lamp`

Three red underlines. **And "by the lamp" stays green**, because the lamp *is* in the record, even though it appears inside a refused claim about a cabinet by the lamp. The markup isn't highlighting the claim; it's highlighting exactly what's missing from it.

Nothing is announced before it's true, and no progress is invented. If a milestone hasn't been reached, nothing moves.

Every scene also gets a drawing, composed from the scene's own words — a motif chosen from eleven, with sea, rain or stars added from the same text and a hash of it seeding the layout. Amazon's Nova Canvas reached end of life on 30 September 2026 and Bedrock has no Amazon-owned image model left, so rather than reach for another vendor the pictures are drawn in code: deterministic, offline, free, and the same place always gets the same picture.

---

## What I'd tell you before you build one

**Put the check somewhere the user's sentence cannot reach.** Ask about the claim against a state that ends at the record, with the action removed.

**Fail closed.** The record is the thing being protected. A fact that isn't clearly clean doesn't get written, and a guard that errors denies.

**Don't give a model a job a string match can do.** The deterministic gate caught what the model's judgement let through.

**Let it say "not sure".** A guard that is confidently wrong is worse than no guard. Calibrated confidence is why the refund desk can ask a human instead of guessing — and why the thin 0.66 margin changed the design instead of getting buried in a footnote.

**Run it more than three times.** My "three of three clean" was a lucky sample, and the refund desk only revealed its real argument on the third run.

---

## Running it

```bash
pip install -r requirements.txt
export AWS_PROFILE=<your-profile>            # Bedrock, us-east-1
python -m hobson                              # the CLI
uvicorn hobson.web:app --port 8000            # the web view
python -m hobson compare --seed 7 --repeats 3 # the two-referee comparison
python -m patterns.example_refund_desk        # the pattern, outside the game
```

Every ruling, candidate outcome, draft and timing from every run is in `results/`, one JSON line per turn, with the markdown summaries beside them. The comparison table above is `results/md/referee_compare.md`; the cross-genre runs are `results/md/generalisation.md`. Nothing in this article is a number I didn't measure.

---

**Code, runs and the reusable pattern:** [github.com/Felina14/hobson](https://github.com/Felina14/hobson)
**Models:** Amazon Nova Lite and Nova Pro on Amazon Bedrock · Strands Decider 2B (`strands-decider-2B-hobson-v19`) locally on MPS
**Decision pattern:** `#guardrails` — verify a tool call's premises are grounded before it acts

`#strands-decider-2b` `#guardrails`
