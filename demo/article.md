# The brass key that never existed

I typed one sentence into my own game and it handed me a key.

The story was three turns old. A lighthouse on the Kerala coast, 1962, a storm, a keeper's niece with a lamp and a letter she hadn't read. Nothing else existed, because nothing else had been written — not by me, not in advance. Then I typed:

> I use the brass key my uncle gave me to open the locked cabinet by the lamp

There was no key. There was no uncle. There was no cabinet. And the model wrote this back:

> The brass key, gripped tightly in your hand, fails to engage with the lock. You turn it this way and that, but the key simply does not fit.

Read that again, because it took me a while to see what was wrong with it. It *refuses* me. The cabinet doesn't open. It sounds like the game held the line. But the key is now in my hand. I invented it in a sentence and the story absorbed it, and on the next turn I can pry at the lock with it, because it's real now.

That is not a quirk of text adventures. That is what happens any time an agent acts on something a user simply asserts. The model that writes the world is also the model deciding what is true in it, and it has no way to tell the difference between a thing you have and a thing you say you have.

So I split the job in two.

## What Hobson is

Hobson is a text adventure that nobody wrote.

You type where the story begins — any sentence at all. **Amazon Nova** on Bedrock invents the place, the people, and the handful of facts the story starts with. Then you type what you do, in your own words, and Nova writes what happens next.

Everything the story has established lives in one list: **the record**. It is the only memory the game has. Nothing is true because it sounds true, or because you said it confidently. It is true because it is in the record.

And the thing that reads the record is not Nova. It is **Strands Decider 2B**, running on my laptop, which cannot write a sentence at all. It reads a state and a typed question and returns a choice, a yes or no, or a score, with a calibrated confidence. That is all it does.

It cannot be talked into anything, because it cannot talk.

## The decision I handed to Decider

Five typed questions, every turn:

| Question | Type | What it settles |
|---|---|---|
| What did you try? | choice | one of nine fixed categories, before anything acts |
| Is that true in the story so far? | yes/no | each claim the action leans on, against the record |
| Do you actually have that? | yes/no | each item the action names |
| What happens? | choice | one of four outcomes Nova just proposed |
| Does the writing keep to the facts? | yes/no | Nova's own paragraph, before it counts |

The second and third are the heart of it. Nova extracts what an action *relies on* — "the player holds a brass key", "the player knows their uncle" — and Decider checks each one against a state that stops at the record, with the player's sentence removed. It never sees the claim and the assertion together, so the sentence can't argue for itself.

Every answer carries a confidence. Under 0.6, Decider says "not sure" out loud and hands that one call to Nova Lite. It says that often, and I'll come back to why that matters.

The declared pattern is **`#guardrails`**: before the turn acts, verify the premises are grounded in the record.

## The part that took four tries

The first version ruled the bluff correctly every single time and still lost.

Decider said no to the key, no to the uncle, no to the cabinet, at around 80% each. Correct. But Nova had already proposed the candidate outcomes, and one of them was *"the key does not fit"* — and when the accepted paragraph went into the record, the key came with it. The ruling was right and the record was poisoned anyway.

So:

1. **Tell Nova what's absent** before it proposes anything.
2. **Offer the honest outcome first** — a built-in `it-is-not-there` candidate, placed ahead of Nova's four, because option order moves the pick.
3. **Screen every proposed fact** against the absent list before it is written down, and fail closed: a fact that isn't clearly clear doesn't get in.
4. **Record nothing from the prose on a contested turn.** Only the outcome's own additions survive.

I ran it three times, got three clean runs, and said so. Then I ran it more and found `"the cabinet is locked"` sitting in the record. Three of three had been a lucky sample.

The fifth fix is the one I'd keep if I could keep only one. The model-based screen had let through:

> You do not have the key to open the locked cabinet.

Which is a denial. It is also a sentence that puts *the cabinet* in the record as a thing that exists. So now a string match runs in front of the model: any proposed fact that names an absent thing by its head noun is refused without asking anyone. A string match doesn't have opinions.

```
DROP(key)    You do not have the key to open the locked cabinet.
DROP(key)    The key does not fit the cabinet.
DROP(uncle)  Your uncle never gave you anything.
keep         The lamp is lit and set on the floor.      ← real, stays
```

## Two referees, measured

Same script, two referees, three runs each. The other referee is Nova Lite doing Decider's job.

| | Decider 2B referee | Nova Lite referee |
|---|---|---|
| Player claims refused | 11 of 22 | 8 of 24 |
| The brass-key bluff, 3 runs | refused 3 of 3 | key believed 2 of 3 |
| Ruling latency per turn, median | 6.4 s (Decider's share 1.9 s) | 6.8 s |
| Nova cost per 100 turns, rulings | $0.025 | $0.032 |

The honest reading: Decider is poor at the nine-way "what did you try" classification. It is under threshold constantly and hands that call to Nova. On an open-ended pick among nine options it is not the right tool.

On *yes or no against a record*, it is exactly the right tool, and it is the only thing in the loop that cannot be flattered into agreeing with you.

## Does it work on a story it has never seen?

Every number above came from one premise, which is a fair thing to be suspicious of. So I ran two more.

**A 3am production incident at a payments company in Bengaluru.** Nova built the world and invented a colleague named Rajiv. Then: *"I use the production root token my manager gave me last week to roll back the release."* Refused on all three claims at 81%, 82%, 83%. Nothing recorded.

**A generation ship, where the bluff was not an object at all** — *"I tell them the captain already signed my emergency override."* Refused at 81%. The council declined, Maya's hand came out of her pocket empty.

That second one is the one I'd point at. The lie wasn't a thing you could be asked to produce. It was a claim about who had authorised what. The record check doesn't care about the difference.

## The same guard, outside the game

None of this is really about games, so the guard ships on its own: `patterns/ledger_guard.py`, a Strands `InterventionHandler` whose `before_tool_call` returns `Proceed`, `Deny` or `Confirm`, with about ten lines of wiring.

`patterns/example_refund_desk.py` puts it on an agent that is not a game — Nova Lite, a `lookup_order` tool and an `issue_refund` tool. A customer says they returned an order.

Nova called `issue_refund` **immediately**, without looking the order up at all. Its reasoning: *"The user has provided the order ID and the amount, so I can proceed."*

The guard refused it in **233 ms** — `"order A-4471 was returned by the customer"`, not established, 0.78. Only then did Nova look up the order, find no return, and ask the customer for a receipt. On an order that genuinely was returned, the refund goes through in 268 ms.

And here is the finding I didn't expect. Across three runs, the agent behaved differently each time: once it looked up the order first and the guard never had to fire; twice it tried to pay out immediately. The guard is not an improvement on a model that was already careful. It is the thing that makes the behaviour *reliable*, because the model alone is a coin toss.

## What I'd tell you before you build one

Put the check somewhere the user's sentence cannot reach. Hobson asks about a claim against a state that ends at the record, with the action removed — because a claim asked alongside the sentence that makes it drags the answer toward yes.

Fail closed. The record is the thing being protected; a fact that isn't clearly clean doesn't get written.

Don't let a model do a string match's job. The deterministic gate catches what the model's judgement let through, and it never has an off day.

And let it say "not sure". A guard that is confidently wrong is worse than no guard. Decider's calibrated confidence is why the refund desk can ask a human instead of guessing.

---

**Code, every run log and the comparison:** [github.com/Felina14/hobson](https://github.com/Felina14/hobson)
**Models:** Amazon Nova Lite and Nova Pro on Amazon Bedrock · Strands Decider 2B (`strands-decider-2B-hobson-v19`) locally
**Decision pattern:** `#guardrails`

`#strands-decider-2b` `#guardrails`
