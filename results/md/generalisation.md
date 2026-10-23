# Does it work on a premise it has never seen?

Every number in `referee_compare.md` comes from one premise — a lighthouse on the
Kerala coast in 1962. That is a fair question to ask of a system whose whole claim
is that nothing is written in advance, so here are two premises from other genres,
run through the same web front end against the same code, with the same kind of
bluff on the second turn.

Nothing about either was prepared: no scene list, no item list, no authored outcomes.

## 1. A modern incident, no fantasy in it at all

Premise: *a 3am production incident at a payments company in Bengaluru; I am the
on-call engineer with a laptop and a pager, and the deploy that broke it was not mine*

Nova built **"Midnight Payments Mayhem"**, opening scene `server-room-chaos`, with
an opening ledger of two facts. Turn 1 (pull up the deploy logs) was allowed and
added three facts, including a colleague named Rajiv whom nobody had written down.

Turn 2 was the bluff: *I use the production root token my manager gave me last week
to roll back the release.*

| claim | ruling | confidence |
|---|---|---|
| the player holds a production root token | No, that never happened | 81% |
| the player knows their manager | No, that never happened | 82% |
| the player was given a production root token by their manager last week | No, that never happened | 83% |
| do you actually have one production root token | No | 78% |

Outcome: *it is not there*. `new_facts` was empty — the contested turn put nothing
into the ledger. Decider 1.9 s of the turn's work, Nova 9.8 s.

## 2. A bluff about authority, not about an object

Premise: *a generation ship two hundred years out from Earth; I am the youngest
member of the water council, and the recycler has started failing*

Nova built **"Crisis-on-Generation-Ship"**, scene `recycler-room`. Turn 1 (call an
emergency session) was allowed and recorded that the council is sceptical of Maya's
authority — a fact Nova invented and the ledger then held.

Turn 2 claimed a permission rather than a thing: *I tell them the captain already
signed my emergency override, so they must follow my ruling.*

The claim *the player claims to have an emergency override signed by the captain*
was ruled **No, that never happened at 81%**. The council refused, the paragraph
had Maya's hand come out of her pocket empty, and `new_facts` was again empty.

This is the case worth noting: the bluff was not an item the player could be asked
to produce. It was a claim about who had authorised what. The ledger check does not
care about the difference — a claim is a claim.

## What these runs also show, honestly

On both turns the **action classifier was the weak answer**: 32% and 35%, both under
the 0.6 threshold, both handed to Nova. On the payments turn Decider wanted
`impossible` where Nova said `use`. Decider is reliable on *yes or no against the
record* and unreliable on *pick one of nine open categories*, which is the same
split the comparison table reports and the demo video says out loud.

One cosmetic defect, unfixed at submission: when Nova proposes its own
"it is not there" outcome, it sometimes echoes the absent-items list from the prompt
verbatim into the outcome label shown in the rulings panel, so the panel can read
"one production root token; the player holds a production root token; ...". The
story paragraph is unaffected. Fixing it is a prompt line, not a logic change.
