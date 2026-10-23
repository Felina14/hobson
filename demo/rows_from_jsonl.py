"""Rebuild the web /start+/turn responses from a run's jsonl rows, for the replay recorder."""
import json, re, sys

LABELS = {"dice":"What did you try?","ledger":"Is that true in the story so far?",
          "requires":"Does the story back that up?","grounds":"Do you actually have that?",
          "outcome":"What happens?","continuity":"Does the writing keep to the facts?",
          "editor":"Which draft reads better?"}
DICE = {"move":"Go somewhere, enter or leave a place","talk":"Speak to a character: ask, persuade, greet, threaten verbally",
        "take":"Pick up, steal, buy or receive an item","use":"Use, give or combine an item the player holds",
        "attack":"Physical violence or force against a character or object",
        "bluff":"Claim something is true, or show or present something, to deceive",
        "examine":"Look at, search or inspect something without changing it",
        "impossible":"Something the world rules or the setting make impossible: fly, teleport, magic, pay with money not held",
        "other":"None of the above or unclear"}
human = lambda s: str(s).replace("-"," ").replace("_"," ")

def base(d, label, answer, note=""):
    c = d.get("confidence")
    return {"key": d["name"], "label": label, "answer": answer, "note": note,
            "confidence": None if c is None else round(float(c),2),
            "unsure": bool(d["unsure"]), "via": d["via"],
            "decider_said": d.get("decider_value") if d["via"]=="nova" else None}

def rows_for(r):
    by = {}
    for d in r["rulings"]: by.setdefault(d["name"], []).append(d)
    out = []
    d = by["dice"][0]
    out.append(base(d, LABELS["dice"], human(d["value"]), DICE.get(d["value"],"")))
    for d in by.get("ledger", []):
        out.append(base(d, LABELS["ledger"], "Yes" if d["value"] else "No, that never happened", d["detail"]))
    o = by["outcome"][0]
    out.append(base(o, LABELS["outcome"], human(o["value"]), r["effect"]))
    cond = ""
    m = re.search(r"The condition is not met \((.+?)\); it does not happen\.", r["effect"] or "")
    if m: cond = m.group(1)
    for d in by.get("requires", []) + by.get("grounds", []):
        if d["name"] == "requires" and d["detail"] != o["value"]: continue
        what = d["detail"] if d["name"] == "grounds" else (cond or d["detail"])
        out.append(base(d, LABELS[d["name"]], "Yes" if d["value"] else "No", what))
    out.append({"key":"danger","label":"How dangerous was that?","answer":f"{r['danger']} of 5",
                "note":"comes with the outcome Nova proposed, not asked","confidence":None,"unsure":False,"via":"world"})
    contested = any(not x["value"] for x in by.get("ledger",[])+by.get("grounds",[]) if x["via"]=="decider") \
                or any(not x["value"] for x in by.get("requires",[]) if x["detail"]==o["value"])
    why = ("contested ruling: the stronger writer" if contested and r["danger"] <= 2
           else f"danger {r['danger']}: " + ("high stakes, the stronger writer" if r["narrator"]=="pro" else "low stakes, the faster one"))
    out.append({"key":"route","label":"Who writes the next paragraph?",
                "answer":"Nova Pro" if r["narrator"]=="pro" else "Nova Lite","note":why,
                "confidence":None,"unsure":False,"via":"world"})
    for d in by.get("continuity", []):
        out.append(base(d, LABELS["continuity"], ("No, it broke the ledger" if d["value"] else "Yes"),
                        d["detail"] or "the paragraph Nova wrote was checked against every fact in the ledger"))
    for d in by.get("editor", []):
        v = d.get("decider_value") if isinstance(d.get("decider_value"), dict) else {}
        if d["via"] == "continuity": ans, note = "Draft A", d["detail"]
        elif v.get("tie"): ans, note = "A tie, kept draft A", f"{v['score_a']:.1f} vs {v['score_b']:.1f} out of 6"
        elif v: ans, note = f"Draft {d['value']}", f"{v['score_a']:.1f} vs {v['score_b']:.1f} out of 6 · swap {'agrees' if v['swap_agrees'] else 'disagrees'}"
        else: ans, note = f"Draft {d['value']}", ""
        c = d.get("confidence")
        out.append({"key":"editor","label":LABELS["editor"],"answer":ans,"note":note,
                    "confidence":None if c is None else round(float(c),2),"unsure":bool(d["unsure"]),"via":d["via"]})
    return out

def build(jsonl, run, opening, title, premise, start_ledger, start_scene):
    rows = [json.loads(l) for l in open(jsonl)]
    rows = [r for r in rows if r["run"] == run]
    cap = [{"url":"/start","body":{"seed":7,"referee":"decider","premise":premise},"ms":5000,
            "res":{"scene":start_scene,"opening":opening,"ledger":list(start_ledger),"image":None,
                   "title":title,"premise":premise}}]
    ledger = list(start_ledger)
    for r in rows:
        ledger += [f for f in r["new_facts"] if f not in ledger]
        cap.append({"url":"/turn","body":{"action":r["action"]},
                    "ms":int(r["decider_ms"]+r["nova_rulings_ms"]+r["nova_narration_ms"]),
                    "res":{"scene":r["scene"],"image":None,"candidates":r.get("candidates",{}),
                           "rows":rows_for(r),"drafts":r["drafts"],"picked":r["picked"],
                           "paragraph":r["paragraph"],"opening":"","ends":False,
                           "ledger":list(ledger),"new_facts":r["new_facts"],
                           "timing":{"decider_ms":round(r["decider_ms"]),
                                     "nova_ms":round(r["nova_rulings_ms"]+r["nova_narration_ms"])},
                           "referee":"decider"}})
    return cap

if __name__ == "__main__":
    import argparse
    a = argparse.ArgumentParser(); a.add_argument("jsonl"); a.add_argument("run"); a.add_argument("meta"); a.add_argument("out")
    g = a.parse_args()
    m = json.load(open(g.meta))
    cap = build(g.jsonl, g.run, m["opening"], m["title"], m["premise"], m["ledger"], m["scene"])
    json.dump(cap, open(g.out,"w"), indent=1)
    print("turns:", len(cap)-1, "->", g.out)
