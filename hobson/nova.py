"""Copied from decider-gauntlet/gauntlet/adapters/nova.py (NovaAdapter only). Bedrock baseline: Nova Micro / Lite / Pro answering the same typed questions.
Constrained output: the model must reply with exactly one option token. Confidence is
not available from the API, so it is recorded as None-equivalent (0.0) and flagged.
Region and profile come from the environment (AWS_PROFILE=<your-profile>, us-east-1)."""
from __future__ import annotations

import json

import boto3

from .base import Decision, timed

MODELS = {
    "micro": "us.amazon.nova-micro-v1:0",
    "lite": "us.amazon.nova-lite-v1:0",
    "pro": "us.amazon.nova-pro-v1:0",
}


class NovaAdapter:
    def __init__(self, tier: str = "lite", region: str = "us-east-1"):
        self.name = f"nova-{tier}"
        self.model_id = MODELS[tier]
        self.client = boto3.client("bedrock-runtime", region_name=region)

    def _converse(self, system: str, user: str):
        def call():
            return self.client.converse(
                modelId=self.model_id,
                system=[{"text": system}],
                messages=[{"role": "user", "content": [{"text": user}]}],
                inferenceConfig={"maxTokens": 8, "temperature": 0.0},
            )
        r, ms = timed(call)
        text = r["output"]["message"]["content"][0]["text"].strip()
        u = r["usage"]
        return text, ms, u["inputTokens"], u["outputTokens"], r

    def noul(self, state, question, criteria=None):
        crit = f" true means: {criteria.get('true','')}. false means: {criteria.get('false','')}." if criteria else ""
        text, ms, i, o, r = self._converse(
            f"Answer the question about the STATE with exactly one word: true or false.{crit}",
            f"STATE:\n{state}\n\nQUESTION: {question}")
        p = 1.0 if text.lower().startswith("true") else 0.0
        return Decision("noul", p, 0.0, {"true": p, "false": 1 - p}, ms, i, o, text)

    def choice(self, state, question, options):
        menu = "\n".join(f"- {k}: {v}" for k, v in options.items())
        text, ms, i, o, r = self._converse(
            "Answer with exactly one option name from the list, nothing else.",
            f"STATE:\n{state}\n\nQUESTION: {question}\nOPTIONS:\n{menu}")
        pick = next((k for k in options if text.lower().startswith(k.lower())), text)
        return Decision("choice", pick, 0.0, {}, ms, i, o, text)

    def score(self, state, question, levels):
        menu = ", ".join(f"{n}={l}" for n, l in enumerate(levels))
        text, ms, i, o, r = self._converse(
            "Answer with a single integer index from the scale, nothing else.",
            f"STATE:\n{state}\n\nQUESTION: {question}\nSCALE: {menu}")
        try: val = float(int(text.split()[0]))
        except Exception: val = float("nan")
        return Decision("score", val, 0.0, {}, ms, i, o, text)
