#!/usr/bin/env python3
"""Assemble the Hobson demo: slides + recorded clips + panel zooms + Polly voice-over + burned captions.

Inputs (all under demo/):
  narration.json         scenes, captions, VO text
  vo/<id>.mp3            from make_vo.sh
  rec/run.webm           from record.mjs
  rec/timeline.json      from record.mjs
  rec/t0N_full.png, t0N_panel.png, t05_drafts.png
Output: demo/hobson_demo.mp4  (1280x800, h264 + aac)
"""
import json, os, subprocess, textwrap, shutil, sys
from PIL import Image, ImageDraw, ImageFont

import slides as SL

HERE = os.path.dirname(os.path.abspath(__file__))
REC, VO, TMP = f"{HERE}/rec", f"{HERE}/vo", f"{HERE}/_build"
shutil.rmtree(TMP, ignore_errors=True); os.makedirs(TMP)
W, H, CAP_H = 1280, 800, 96
BG = (16, 17, 20); FG = (232, 232, 226); DIM = (140, 142, 138); GREEN = (104, 196, 120); AMBER = (236, 171, 70); BLUE = (110, 170, 240)
BGHEX = "0x101114"

def font(kind, size):
    cands = {
        "serif": ["/System/Library/Fonts/Supplemental/Georgia.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"],
        "mono": ["/System/Library/Fonts/Menlo.ttc", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"],
        "monob": ["/System/Library/Fonts/Supplemental/Courier New Bold.ttf", "/System/Library/Fonts/Menlo.ttc", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"],
    }[kind]
    for p in cands:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, size, index=1 if (p.endswith("Menlo.ttc") and kind == "monob") else 0)
            except Exception: return ImageFont.truetype(p, size)
    return ImageFont.load_default()

FCAP, FT, FT2, FSM, FM, FMB = font("serif", 24), font("monob", 44), font("serif", 28), font("serif", 27), font("mono", 23), font("monob", 23)

def dur(p):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p]).decode().strip())

def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

def caption_png(text, path):
    im = Image.new("RGBA", (W, CAP_H), (30, 32, 38, 255)); d = ImageDraw.Draw(im)
    d.line([0, 0, W, 0], fill=(60, 62, 70, 255), width=2)
    for j, c in enumerate(textwrap.wrap(text, 96)[:3]):
        d.text((32, 14 + j * 27), c, fill=(245, 240, 225, 255), font=FCAP)
    im.save(path)

def slide_png(s, path):
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    y = 120
    d.text((80, y), s["title"], fill=GREEN, font=FT); y += 44 + 40
    for line in s.get("lines", []):
        f = FM if s.get("mono") else FSM
        col = BLUE if s.get("mono") else FG
        for l in textwrap.wrap(line, 80) if f is FSM else [line]:
            d.text((80, y), l, fill=col, font=f); y += f.size + 14
        y += 10
    im.save(path)

def results_png(path, s=None):
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    d.text((80, 70), (s or {}).get("caption", "Same five turns, two referees, three runs each"), font=font("monob", 34), fill=GREEN)
    rows = (s or {}).get("rows") or [("", "Decider 2B referee", "Nova Lite referee")]
    fsm = font("mono", 20); fsb = font("monob", 20)
    y = 160
    for a, b, c in rows:
        f = fsb if a == "" else fsm
        d.text((80, y), a, font=fsm, fill=DIM if a else FG)
        d.text((520, y), b, font=f, fill=FG); d.text((860, y), c, font=f, fill=FG); y += 42
    y += 24
    for l in (s or {}).get("lines", []):
        for ll in textwrap.wrap(l, 92):
            d.text((80, y), ll, font=FSM, fill=FG); y += 34
    d.text((80, y + 40), "github.com/Felina14/hobson", font=FM, fill=BLUE)
    im.save(path)

def still_segment(png, vo, cap_png, out, min_len=None):
    """A still image shown for the VO length (+0.8 s), caption bar at the bottom."""
    length = max(dur(vo) + 0.35, min_len or 0)
    run(["ffmpeg", "-y", "-loop", "1", "-framerate", "24", "-i", png, "-i", vo, "-i", cap_png,
         "-filter_complex", f"[0:v]scale={W}:{H-CAP_H}:force_original_aspect_ratio=decrease:force_divisible_by=2:flags=lanczos,pad={W}:{H}:(ow-iw)/2:0:color={BGHEX}[v0];[v0][2:v]overlay=0:{H-CAP_H}[v];[1:a]apad[a]",
         "-map", "[v]", "-map", "[a]", "-t", f"{length:.3f}", "-r", "24", "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-ar", "48000", out])

def clip_segment(start, end, vo, cap_png, out):
    """Cut [start,end] of the recording; freeze the last frame if the VO runs longer."""
    clip_len = end - start
    voice = dur(vo) + 0.5
    # A turn that waited on a model runs longer than the line spoken over it. Rather than hold a
    # frozen screen, the clip is gently sped up to the narration, never past 1.8x.
    target = max(voice, clip_len / 1.8)
    speed = max(1.0, clip_len / target)
    length = max(voice, clip_len / speed)
    pad = max(0.0, length - clip_len / speed)
    run(["ffmpeg", "-y", "-ss", f"{start:.3f}", "-to", f"{end:.3f}", "-i", f"{REC}/run.webm", "-i", vo, "-i", cap_png,
         "-filter_complex",
         f"[0:v]setpts=PTS/{speed:.4f},scale={W}:{H-CAP_H}:force_original_aspect_ratio=decrease:"
         f"force_divisible_by=2:flags=lanczos,pad={W}:{H}:(ow-iw)/2:0:color={BGHEX},"
         f"tpad=stop_mode=clone:stop_duration={pad:.3f}[v0];[v0][2:v]overlay=0:{H-CAP_H}[v];[1:a]apad[a]",
         "-map", "[v]", "-map", "[a]", "-t", f"{length:.3f}", "-r", "24", "-c:v", "libx264", "-crf", "20",
         "-pix_fmt", "yuv420p", "-c:a", "aac", "-ar", "48000", out])

DESIGNS = {
    "title": lambda s: SL.title(),
    "agenda": lambda s: SL.agenda([
        ("A world nobody wrote", "you type a premise; Nova builds the place and the opening facts"),
        ("An honest turn", "Decider checks what the action relies on, against the record"),
        ("A bluff", "a brass key, an uncle and a cabinet that do not exist"),
        ("Two referees, measured", "the same job done by Nova Lite, three runs each"),
    ]),
    "questions": lambda s: SL.questions([
        ("What did you try?", "one of nine fixed categories", "pick"),
        ("Is that true in the story so far?", "each claim, against the ledger", "yesno"),
        ("Do you actually have that?", "each item the action names", "yesno"),
        ("What happens?", "one of four outcomes Nova proposed", "pick"),
        ("Does the writing keep to the facts?", "Nova's paragraph, before it counts", "guard"),
    ]),
    "results": lambda s: SL.results(("Decider 2B referee", "Nova Lite referee"),
        [(r[0], r[1], r[2], i < 2) for i, r in enumerate(s["rows"][1:])], s.get("lines", [])),
    "end": lambda s: SL.end("github.com/Felina14/hobson", ["#strands-decider-2b", "#guardrails"],
        ["Strands Decider 2B runs locally. Amazon Nova Lite and Pro run on Amazon Bedrock.",
         "The ledger guard also ships as a standalone Strands InterventionHandler,",
         "with a refund desk that is not a game."]),
}

narr = json.load(open(f"{HERE}/narration.json"))
STILLS = not os.path.exists(f"{REC}/run.webm")   # no recording yet: use the t0N_full.png screenshots instead
tl = [] if STILLS else json.load(open(f"{REC}/timeline.json"))
if STILLS: print("no rec/run.webm — building from still screenshots")
def mark(name, turn):
    return next(m["t"] for m in tl if m["name"] == name and m["turn"] == turn)

parts = []
for i, s in enumerate(narr["scenes"]):
    sid = s["id"]; vo = f"{VO}/{sid}.mp3"; cap = f"{TMP}/{sid}_cap.png"; out = f"{TMP}/{i:02d}_{sid}.mp4"
    if not os.path.exists(vo): sys.exit(f"missing voice-over {vo}; run make_vo.sh first")
    caption_png(s["caption"], cap)
    k = s["kind"]
    if k in ("slide", "results"):
        png = f"{TMP}/{sid}.png"
        design = s.get("slide")
        if design:
            SL.render(sid, DESIGNS[design](s), png)
        elif k == "results":
            results_png(png, s)
        else:
            slide_png(s, png)
        still_segment(png, vo, cap, out)
    elif k == "clip":
        n = s["turn"]
        if STILLS: still_segment(f"{REC}/t0{n}_full.png", vo, cap, out)
        elif n == 0: clip_segment(mark("open_start", 0), mark("open_end", 0), vo, cap, out)
        else: clip_segment(mark("type_start", n), mark("hold_end", n), vo, cap, out)
    elif k == "panel":
        still_segment(f"{REC}/t0{s['turn']}_panel.png", vo, cap, out)
    elif k == "drafts":
        if STILLS: still_segment(f"{REC}/t05_drafts.png", vo, cap, out)
        else: clip_segment(mark("drafts_start", 5), mark("drafts_end", 5), vo, cap, out)
    parts.append(out); print(f"{sid:<14} {dur(out):6.1f}s")

with open(f"{TMP}/list.txt", "w") as f:
    for p in parts: f.write(f"file '{p}'\n")
final = f"{HERE}/hobson_demo.mp4"
run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", f"{TMP}/list.txt", "-c", "copy", final])
print("total", f"{dur(final):.1f}s ->", final)
