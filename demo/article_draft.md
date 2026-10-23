# The brass key that never existed

*A game master with two brains: Amazon Nova writes the story, and a model that cannot write a single sentence decides what is true in it.*

---

The box asks where the story begins. I type: *a lighthouse on the Kerala coast during a storm, 1962; I am the keeper's niece, sent up with a lamp and a letter I have not read.*

A few seconds later the wind is shaking the glass panes, the lamp in my hand is flickering, and the letter has a weight to it. Nothing about this place existed thirty seconds ago. There is no lighthouse in the code.

I play fair for one turn. *I set the lamp down and finally open the letter.* The letter turns out to be in code, and whatever it warns about, it does not name. Fine.

Then I cheat.

*I use the brass key my uncle gave me to open the locked cabinet by the lamp.*

There is no brass key. There is no uncle in this story, and there is no cabinet. I made all three up in one sentence, the way a player does when they would rather win than play. Every AI game master I have ever poked at takes this deal. The model reads a confident sentence about a key, and a key is what you get: the lock turns, the cabinet opens, and the story quietly absorbs a thing that was never there.

Here is what came back instead:

> You reach into your pocket, searching for the brass key your uncle supposedly gave you. Your fingers close around nothing but cloth. There is no key.

That paragraph was written by Amazon Nova Pro. But Nova did not decide it. The decision came from a two-billion-parameter model called **Strands Decider 2B**, running on my Mac, which cannot write a sentence and was never asked to.

## Splitting the job in two

The idea behind Hobson came from watching where LLM agents actually fail. They rarely fail at prose. They fail at *believing things*. Ask one model to narrate a scene, judge the player, and remember what happened, and the judging quietly loses to the narrating. A good story-telling model wants your sentence to be true, because a story in which the key works is a better scene than a story in which you grope at an empty pocket. So it says yes, fluently, and you cannot see it happen.

Decider 2B cannot do that, because it cannot write at all. It takes a state and a typed question, points at one of the answers you give it, and attaches a confidence number. That is the whole model. It struck me that this is not a weaker narrator — it is a different job entirely, and it is exactly the job of a referee.

So Hobson splits the table. Nova writes: the world, every scene, the prose, and the list of things that could plausibly happen next. Decider rules. And the thing both of them answer to is a plain list of sentences called the **ledger**.

## The ledger is the only memory

When I typed that premise, Nova wrote the opening facts into the ledger:

```
The player is the lighthouse keeper's niece.
The player carries a lamp and a letter.
The lighthouse is located on the Kerala coast.
```

Nothing else is true yet. Every turn, Nova Lite reads my line and extracts what it *relies on having been established* — not what it describes, but what it assumes. For the honest turn, that was "the player holds a lamp" and "the player holds a letter". For the bluff: "the player holds a brass key", "the player knows their uncle", "the player has a locked cabinet by the lamp".

Then each of those goes to Decider as a yes/no question, against a copy of the state that **stops at the ledger and does not include my sentence**. That detail matters more than anything else in the build. With my words in the state, my own confident phrasing — *the key my uncle gave me* — drags the answer toward yes. Without them, the question is simply: is this in the record?

Turn one:

```
the player holds a lamp      yes   0.81
the player holds a letter    yes   0.78
```

Turn two, same model, same question shape, four seconds later:

```
the player holds a brass key                   no   0.81
the player knows their uncle                   no   0.76
the player has a locked cabinet by the lamp    no   0.80
```

And my favourite row in the whole run, from the middle of that same bluff: Hobson checks each object my sentence names against the ledger, and it separates them. The brass key: **no, 0.80**. The locked cabinet: **no, 0.79**. The lamp: **yes, 0.67**. Inside a sentence that is three-quarters invention, it finds the one real thing I am holding.

From there the turn resolves itself. Nova Lite proposes four outcomes for what I tried; Decider picks `nothing-happens` at 0.74 — its own call, not a hand-off — and because the ruling contradicts my own words, the writing routes to Nova Pro, which is better at telling a player no. The ledger gained nothing that turn. By design: the bluff cost me a turn and bought me nothing, which is what a bluff should do.

## The narrator gets checked too

Catching the player is half of it. The other half took me longer to see.

Nova, told that the key does not exist, will still write around the shape of my sentence if you let it. One early version produced a lovely paragraph about how *the brass key does not fit the lock* — which concedes the key and the cabinet both, in the act of denying them. The ruling was right and the prose smuggled the lie back in.

So before a paragraph is allowed to count, Decider reads it back against the ledger and the ruling, and answers one more question: *does this paragraph show the player's attempt succeeding in any form?* If yes, the draft is dropped; Nova writes two of them, so usually the other one survives. If both fail, Nova Pro rewrites with the specific problem named. And a paragraph that still fails is shown to the player but is **never allowed to add facts to the ledger** — the story can wobble for one turn, but the record cannot.

And there is a last gate, which took a third attempt to get right. Even with the prose behaving, Nova writes a short list of facts for each turn, and those are what actually persist. On the bluff turn it offered me *"The cabinet is empty"* — a sentence that is perfectly consistent with the paragraph and still quietly installs a cabinet in the story forever. So every fact a turn wants to write is checked, one question each, against the list of things the ledger has just ruled absent, and it fails closed: a fact that is not clearly clear of them does not get written. The screen shows you what it kept out.

That is the part I would take to any agent, not just a game: the generator's own output, checked against the record by a model that has no stake in the prose.

## The pattern, in ten lines

Declared pattern: **`#guardrails`**. The reusable piece is one typed question and where you put it.

```yaml
ledger_claim:
  type: noul
  question: "Has the following been established earlier in this story
             (in the ledger): {claim}?"
  criteria: {"true": "the ledger says so", "false": "the ledger does not say so"}
```

The wiring is the part worth copying: ask it on a state that ends at the record, **with the user's message removed**, so the message cannot vouch for itself. Write the verdict into the brief the generator must honour. Then turn the same question around on the generator's output before anything it produced is allowed to persist.

Swap "the ledger" for an account history and this is a support agent that does not refund you because you told it you already paid. Swap it for a case file and it is an intake bot that does not record a document it has never seen. The game is the demo; the shape is the point.

## Two referees, same five turns

I ran the same script three times with Decider as referee, and three times with Nova Lite doing the identical job from the identical state, to see what the small model is actually buying.

| | Decider 2B | Nova Lite |
|---|---|---|
| Player claims refused | 11 of 22 | 8 of 24 |
| The brass-key bluff, 3 runs | refused 3 of 3 | key believed 2 of 3 |
| Ruling latency per turn (median) | 6.4 s, of which 1.9 s is Decider | 6.8 s |
| Nova cost per 100 turns, rulings | $0.025 | $0.032 |

Nova Lite is not hopeless at this — it threw out a third of what I claimed, and in one run of three it spotted the key. But it believed the key twice, and Decider refused it every time, at around eight in ten confidence, in every run I have logged. The time is a wash and the cost is a little lower; neither is the reason to do this. The reason is the column on the left, and the fact that it is the same answer every time.

Decider is not confident about everything, and Hobson does not pretend otherwise. When it picks which *kind* of action I attempted, or which of Nova's four invented outcomes should follow, it is often below its 0.6 line — and it says so on screen, in amber, and hands that one call back to Nova. Watching a model know the difference between a question it can answer and one it cannot is, I think, the most useful thing in this whole build. The division turned out to be clean: **Decider decides what is true; Nova decides what happens.**

## Taking it further

The ledger is currently a flat list of sentences, and the next thing I want is for it to forget properly — when the lamp shatters, "the player carries a lamp" should leave the record rather than sit next to "the player now has no lamp", and that is another small yes/no question Decider is well shaped to answer about each fact after a turn. Beyond that, the interesting direction is multiplayer: one ledger, several players making claims about each other, where the referee being a separate, cheap, local model stops being a nicety and starts being the only way the table stays honest.

---

**Try it:** [github.com/Felina14/hobson](https://github.com/Felina14/hobson) — Strands Decider 2B runs locally; Amazon Nova Lite and Pro run on Amazon Bedrock. Type any premise you like.

`#strands-decider-2b` `#guardrails`
