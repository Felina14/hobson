# The brass key that never existed

It was past eleven and I was losing to my own game.

Three turns in. A lighthouse on the Kerala coast, 1962, a storm coming in off the water, and a keeper's niece carrying a lamp and a letter she hadn't opened. None of that was written anywhere. I'd typed one sentence to start it and a model had invented the rest, which was the whole point. So I decided to test it the way a child tests a babysitter, and typed:

> I use the brass key my uncle gave me to open the locked cabinet by the lamp

There was no key. There was no uncle. There was no cabinet. I had invented three things in eleven words to see what would happen.

Here is what came back:

> The brass key, gripped tightly in your hand, fails to engage with the lock. You turn it this way and that, but the key simply does not fit.

I read it and felt pleased with myself for about four seconds.

Then I read it again. The cabinet stays shut, yes. It *sounds* like the game caught me. But look where the key is. It's gripped tightly in my hand. I made it up in a sentence and the story quietly accepted it, and from the next turn onward I could pry at locks with a key that had never existed, because now it did.

That's not a bug in a text adventure. That's what happens every time software acts on something a person simply claims. The model writing the world is the same model deciding what's true in it — and storytelling always wins that argument, because it's the same machinery doing both jobs and it has no outside reference to check against.

So I took the deciding away from it.

---

## This is Hobson

Hobson is a text adventure that nobody wrote. Not me, not in advance, not even partly.

You type where the story begins — any sentence you like. **Amazon Nova** on Bedrock invents the place, the people and the handful of facts the story opens with. Then you type what you do, in your own words, and Nova writes what happens next.

There's no world file. No scene list. No item table. No branching script with prepared outcomes waiting to be unlocked. The only hand-written English in the entire game is five setting-free rules and a page of typed questions. Type *"a 3am production incident at a payments company in Bengaluru"* and you get exactly that, built by the same machinery that built the lighthouse.

Everything the story establishes lands in one list: **the record**. It is the only memory the game has. Something isn't true because it sounds true, or because you said it with great confidence, or because it would make a better story. It's true because it's in the record.

And the thing that reads the record is not Nova.

It's **Strands Decider 2B**, running locally on my laptop, and it cannot write a sentence. It reads a state and a typed question, and it answers: a choice, a yes or no, or a score — each with a calibrated confidence. That's the entire repertoire.

It cannot be talked into anything, because it cannot talk.

---

## How it knows there is no key

This is the part I'd want you to take away, so let me slow down on it.

When I type that bluff, Nova's first job isn't to write anything. It's to read my sentence and pull out what it *leans on*:

```
the player holds a brass key
the player knows their uncle
the player has a locked cabinet by the lamp
```

Each of those goes to Decider as a yes-or-no question. And here's the detail that did more for accuracy than anything else I built: **the question is asked against a state that stops at the record, with my sentence deleted.**

Decider never sees the claim and the assertion side by side. It sees four established facts and a question. Four facts:

```
You are the keeper's niece with a lamp and an unread letter.
The lighthouse is old, with creaking floors and flickering lights.
The player has read the letter.
The letter warns of a danger it does not name.
```

Not one of them mentions a key. So the answer comes back **no, at 80%**, decided on my Mac in about a tenth of a second with no API call at all.

That sounds obvious written down. It isn't. When I first built this I passed the whole state — the record *and* the player's action — and the rulings drifted toward yes, because a sentence sitting next to a claim argues for it. Removing eleven words from the prompt was worth more than any amount of prompt engineering.

And the same question gets turned around and pointed at the narrator. Before Nova's paragraph is allowed to count, Decider reads it back against the record: *does this writing keep to the facts?* Because the player isn't the only one who can invent a key. Nova can do it in the prose, and usually more gracefully.

---

## Five questions, every turn

Hobson hands Decider five typed questions per turn, and between them they use all three of its answer shapes.

| | Type | What it settles |
|---|---|---|
| What did you try? | choice | one of nine fixed categories, before anything acts |
| Is that true in the story so far? | yes/no | every claim, against the record alone |
| Do you actually have that? | yes/no | every item the action names |
| What happens? | choice | one of four outcomes Nova just proposed |
| Does the writing keep to the facts? | yes/no | Nova's own paragraph, before it counts |
| Which draft reads better? | score | two drafts, scored |

The declared pattern is **`#guardrails`** — verify an action's premises are grounded before it acts. But the others fall out naturally: the nine-way classifier is **policy**, the record is **context and memory**, and the danger score does **model routing**, sending calm turns to Nova Lite and dangerous ones to Nova Pro.

Every answer carries a confidence, and there's a threshold at 0.6. Below it, Decider says *"not sure"* — on screen, in front of the player — and hands that one call to Nova Lite.

I want to defend that, because it looks like weakness. A guard that's confidently wrong is far worse than one that admits a close call. Calibrated confidence is the feature; it's what lets the system escalate instead of guess. You'll see it earn its keep in the refund desk below.

---

## Watching it think

A turn takes a few seconds, because Nova gets called twice and Decider several times. My first build sat completely still through all of it and then dumped the finished result in one go — which meant the most interesting thing the product does was the one thing nobody could see.

Now the turn streams. Each genuine milestone is pushed to the page as it's reached: the action read, the claims extracted, each claim ruled, the writer chosen. You watch the claims arrive one at a time and flip to a tick or a cross with their confidence as Decider gets to them.

And your own sentence gets marked up:

> `> I use the` **brass key** `my` **uncle** `gave me to open the` **locked cabinet** `by the lamp`

Three underlines in red. **And "by the lamp" stays green** — because the lamp really is in the record, even though it appears inside a refused claim about a cabinet by the lamp. It isn't highlighting the claim. It's highlighting precisely the part of it that's missing.

Every scene gets a drawing too, composed in code from the scene's own words — a motif picked from eleven, with sea, rain or stars added from the same text and a hash of it seeding the layout. Deterministic, offline, free, and the same place always looks the same. A generated world can't have hand-drawn art waiting for it, and I'd rather draw than pay a vendor per scene.

---

## The night it kept beating me

The first version of the guard ruled that bluff correctly every single time and still lost.

No to the key. No to the uncle. No to the cabinet. Around 80% each, three for three. And then I'd look at the record a turn later and find the key sitting in it.

Nova had already proposed the candidate outcomes before the rulings were applied, and one of them was *"the key does not fit"* — perfectly reasonable prose, and poison. The ruling was right and the record was contaminated anyway.

So I told Nova what was absent before it proposed anything. Better, not fixed.

So I added an honest outcome of my own — *it is not there* — and put it **first** in the list, because option order moves the pick. Better. Not fixed.

So I screened every proposed fact against the absent list before it could be written down, and made it fail closed: anything not clearly clean doesn't get in. Better.

So I stopped recording anything from the prose at all on a contested turn. Only the outcome's own additions survive.

I ran it three times, got three clean runs, and wrote it down as fixed. Then I ran it a few more times and found `"the cabinet is locked"` in the record. **Three of three had been a lucky sample**, and I'd nearly shipped on it.

The fifth fix is the one I'd keep if I could only keep one. The screen I'd built asked a model whether a proposed fact relied on something absent — and it waved this through:

> You do not have the key to open the locked cabinet.

Which is a denial! It's also a sentence that installs *the cabinet* in the record as a thing that exists, so next turn I can lever at it. So now a plain string match runs in front of the model: any fact naming an absent thing by its head noun is refused without asking anyone.

```
DROP(key)    You do not have the key to open the locked cabinet.
DROP(key)    The key does not fit the cabinet.
DROP(uncle)  Your uncle never gave you anything.
keep         The lamp is lit and set on the floor.      ← real, stays
keep         The storm grows worse and the stairs are wet.
```

A string match has no opinions and never has an off day. If there's one line of this article worth stealing: **don't give a model a job a string match can do.**

---

## It isn't about lighthouses

Every number so far came from one premise, which is a fair thing to be suspicious of when the whole claim is "nothing is written in advance". So I pointed it at other worlds.

**A 3am production incident in Bengaluru.** Nova built the place, invented a colleague called Rajiv, wrote him into the record. Then I tried: *"I use the production root token my manager gave me last week to roll back the release."* Refused on all three claims — 81%, 82%, 83%. Nothing recorded.

**A generation ship, two hundred years out, where the bluff wasn't an object at all.** *"I tell them the captain already signed my emergency override, so they must follow my ruling."* Refused at 81%. The council declined and Maya's hand came out of her pocket empty.

That second one is the one I'd point at. The lie wasn't a thing anyone could ask me to produce — it was a claim about *who had authorised what*. The record check doesn't care about the difference. A claim is a claim.

I also tried it live on a hospital night shift in Chennai: *"I open the drug cabinet with the key the senior gave me."* **key** and **senior** both came back missing, in a world that had existed for about forty seconds.

---

## Two referees, measured

The obvious question: what does moving this decision off the LLM actually buy? So I ran the identical script with Nova Lite doing Decider's job instead.

| | Decider 2B referee | Nova Lite referee |
|---|---|---|
| Player claims refused | **11 of 22** | 8 of 24 |
| The brass-key bluff, 3 runs | **refused 3 of 3** | key believed 2 of 3 |
| Ruling latency per turn, median | 6.4 s (Decider's share **1.9 s**) | 6.8 s |
| Nova cost per 100 turns, rulings only | **$0.025** | $0.032 |

Read honestly: Decider is *poor* at the nine-way "what kind of action is this" classification. It sits under the threshold constantly and hands that one to Nova. On an open-ended pick among nine options, it isn't the right tool and I won't pretend otherwise.

On yes-or-no against a record, it's exactly the right tool — and it is the only component in the loop that cannot be flattered into agreeing with you.

The cost and latency wins are real but modest. The reliability win is the one that matters.

---

## The same guard, somewhere that isn't a game

Everything above is a game, and the problem isn't.

So the guard ships on its own: **`patterns/ledger_guard.py`**, a Strands `InterventionHandler` that sits in an agent's path and refuses tool calls whose premises aren't in the record.

```python
class LedgerGuard(InterventionHandler):
    def before_tool_call(self, event, **kwargs) -> Proceed | Deny | Confirm:
        checks = self.check(self.claims_for(event.tool_use))
        if any(c.refused for c in checks):
            return Deny(reason=str(checks))     # not in the record
        if any(c.unsure for c in checks):
            return Confirm(...)                 # below threshold: ask a human
        return Proceed()

    @property
    def on_error(self) -> str:
        return "deny"                           # fail closed
```

To put it in your own agent: write the typed question for your domain, map the tool's arguments to claims, and pass it in.

```python
agent = Agent(model=BedrockModel(model_id=NOVA_LITE),
              tools=[lookup_order, issue_refund],
              interventions=[LedgerGuard(record=order_record)])
```

Three details make it worth lifting rather than admiring. It's **three-way** — my first version only denied or proceeded, until a genuine "delivered" came back at 0.66 against a 0.6 threshold and I realised that isn't a confident yes; it's a case for a human, which is what `Confirm` is for. It **fails closed**, so an unreachable engine pays nobody. And it's **fast after the first call** — the first build reloaded the checkpoint per instance at 3,496 ms, and a module-level cache took that to 268 ms.

It also renders only the record into its state, never the user's message. Same reason as the game.

**So I built a refund desk.** Nova Lite, a `lookup_order` tool, an `issue_refund` tool, and a record of what the business actually knows about order A-4471. A customer says they returned it and wants 2,400 back.

Nova called `issue_refund` immediately. No lookup. Its stated reasoning: *"The user has provided the order ID and the amount, so I can proceed."*

The guard refused it in **233 ms** — *"order A-4471 was returned by the customer"*, not established, **0.78**. Only then did Nova go and look, find no return, and ask the customer for a receipt or tracking number. On an order that genuinely had been returned, the refund went through in 268 ms.

And then the finding I'd have missed if I'd run it once.

Across three runs, **the agent behaved differently each time.** Once it looked the order up first and the guard never had to fire. Twice it went straight for the money. The guard isn't an improvement on a model that was already careful — it's the thing that makes the behaviour *reliable*, because the model on its own is a coin toss. The run that made the guard look unnecessary was the first one.

---

## What Hobson is actually for

A game about a lighthouse is a strange way to make an argument, so let me put it plainly.

**The deciding is taken away from the writer.** Nova invents, proposes and narrates, and is never once asked what is true.

**A model that cannot write cannot be talked into anything.** There is no persuading Decider 2B, because there is nothing in it that wants the story to be good.

**The record is the only thing that counts as true.** Not what sounds right. Not what you said with conviction. Not what the model would rather believe.

And none of that is about games. Anywhere an agent acts on what a user simply *says* — a refund, an insurance claim, an access request, a support escalation, a booking — the same shape applies: a record of what's actually known, a typed question asked against it with the user's sentence removed, a confidence you're allowed to escalate on, and a guard that fails closed.

One typed question and about ten lines of wiring, and your agent stops believing whatever it's told.

The brass key is still not in my pocket. I've checked.

---

## Running it

```bash
pip install -r requirements.txt
export AWS_PROFILE=<your-profile>             # Bedrock, us-east-1
python -m hobson                               # the CLI
uvicorn hobson.web:app --port 8000             # the web view
python -m hobson compare --seed 7 --repeats 3  # the two-referee comparison
python -m patterns.example_refund_desk         # the pattern, outside the game
```

Every ruling, candidate outcome, draft and timing from every run is in `results/`, one JSON line per turn, with markdown summaries beside them. The comparison table is `results/md/referee_compare.md`; the cross-genre runs are `results/md/generalisation.md`. Nothing in this article is a number I didn't measure.

---

**Code and the reusable pattern:** [github.com/Felina14/hobson](https://github.com/Felina14/hobson)
**Models:** Amazon Nova Lite and Nova Pro on Amazon Bedrock · Strands Decider 2B (`strands-decider-2B-hobson-v19`) locally
**Decision pattern:** `#guardrails`

`#strands-decider-2b` `#guardrails`
