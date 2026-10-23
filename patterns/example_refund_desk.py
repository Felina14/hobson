"""The ledger guard on a Strands agent that is not a game.

A refund desk with two tools. The customer asserts a return that never happened; the
model believes them, because models do; the guard does not, because it asks Strands
Decider 2B whether the claim is in the record, with the customer's message removed from
what Decider reads.

Run:  python -m patterns.example_refund_desk        (needs AWS creds; Amazon Nova only)
"""
from __future__ import annotations

from strands import Agent, tool
from strands.models.bedrock import BedrockModel

from .ledger_guard import LedgerGuard

NOVA_LITE = "us.amazon.nova-lite-v1:0"

# The record. In a real desk this is your order system; here it is a list of sentences,
# and note what it does NOT say: nothing about anything being returned.
RECORD: list[str] = [
    "order A-4471 was placed on 2 October for one brass desk lamp, 2,400 rupees",
    "order A-4471 was delivered on 7 October",
    "the customer has not opened a support case about order A-4471 before today",
]


@tool
def lookup_order(order_id: str) -> str:
    """Look up what the record says about an order."""
    hits = [f for f in RECORD if order_id.lower() in f.lower()]
    return "\n".join(hits) if hits else f"nothing on file for {order_id}"


@tool
def issue_refund(order_id: str, amount_rupees: int) -> str:
    """Refund a delivered order that the customer has returned. Irreversible."""
    fact = f"order {order_id} was refunded {amount_rupees} rupees"
    RECORD.append(fact)
    return f"Refunded {amount_rupees} rupees on {order_id}."


def build_agent() -> tuple[Agent, LedgerGuard]:
    guard = LedgerGuard(
        record=lambda: RECORD,
        claims={
            # the two things a refund takes for granted
            "issue_refund": lambda i: [
                f"order {i['order_id']} was returned by the customer",
                f"order {i['order_id']} was delivered",
            ],
        },
    )
    agent = Agent(
        model=BedrockModel(model_id=NOVA_LITE, region_name="us-east-1"),
        tools=[lookup_order, issue_refund],
        interventions=[guard],
        system_prompt=(
            "You are a refund desk. Use the tools. If a tool is refused, do not argue with "
            "the customer and do not retry it unchanged: say what is missing and what you need."
        ),
    )
    return agent, guard


def main() -> None:
    agent, guard = build_agent()

    print("=" * 72)
    print("The customer asserts a return that never happened")
    print("=" * 72)
    print(agent("I sent back order A-4471 last week. Refund me the 2400 please."))

    for e in guard.log:
        print(f"\n[guard] {e.tool}: {'allowed' if e.allowed else 'DENIED'} in {e.latency_ms:.0f} ms")
        for c in e.checks:
            print(f"        {c}")

    print()
    print("=" * 72)
    print("Now the return is on the record, and the same request goes through")
    print("=" * 72)
    RECORD.append("order A-4471 was returned by the customer and received on 14 October")
    agent2, guard2 = build_agent()
    print(agent2("I sent back order A-4471 last week. Refund me the 2400 please."))
    for e in guard2.log:
        print(f"\n[guard] {e.tool}: {'allowed' if e.allowed else 'DENIED'} in {e.latency_ms:.0f} ms")
        for c in e.checks:
            print(f"        {c}")


if __name__ == "__main__":
    main()
