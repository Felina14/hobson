"""Python twin of demo/record.mjs: drive the page, record video, write rec/timeline.json and the PNGs assemble.py expects."""
import asyncio, json, os, shutil, sys, time
from playwright.async_api import async_playwright
OUT = sys.argv[1]; URL = sys.argv[2]; NARR = json.load(open(sys.argv[3]))
turns = [s for s in NARR["scenes"] if s["kind"] == "clip" and s.get("action")]
shutil.rmtree(OUT, ignore_errors=True); os.makedirs(OUT)
W, H = 1280, 800

async def main():
    tl = []; t0 = time.time()
    mark = lambda name, turn: tl.append({"name": name, "turn": turn, "t": round(time.time() - t0, 3)})
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={"width": W, "height": H}, device_scale_factor=1, record_video_dir=OUT, record_video_size={"width": W, "height": H})
        pg = await ctx.new_page()
        t0 = time.time()
        await pg.goto(URL, wait_until="networkidle")
        await pg.wait_for_timeout(800); mark("open_start", 0)
        prem = NARR.get("premise", "")
        if prem:
            await pg.click("#premise-input"); await pg.type("#premise-input", prem, delay=28)
            await pg.wait_for_timeout(600); await pg.press("#premise-input", "Enter")
        else:
            await pg.click("#premise .hint button:last-child")
        await pg.wait_for_selector("#story .scene", timeout=120000)
        await pg.wait_for_timeout(2500)
        await pg.screenshot(path=f"{OUT}/t00_full.png")
        await pg.wait_for_timeout(2000); mark("open_end", 0)
        for s in turns:
            n = s["turn"]
            before = await pg.text_content("#timing") or ""
            mark("type_start", n)
            await pg.click("#action"); await pg.type("#action", s["action"], delay=55)
            await pg.wait_for_timeout(500); await pg.press("#action", "Enter"); mark("submitted", n)
            await pg.wait_for_function("(prev) => { const t = document.querySelector('#timing')?.textContent || ''; return t && t !== prev; }", arg=before, timeout=120000)
            await pg.wait_for_timeout(2200); mark("result", n)
            await pg.screenshot(path=f"{OUT}/t0{n}_full.png")
            flow = await pg.query_selector("#hv-flow") or await pg.query_selector("#rows")
            box = await flow.bounding_box(); tb = await (await pg.query_selector("#timing")).bounding_box()
            await pg.screenshot(path=f"{OUT}/t0{n}_panel.png", clip={"x": box["x"] - 12, "y": box["y"] - 12, "width": box["width"] + 24, "height": (tb["y"] + tb["height"]) - box["y"] + 24})
            await pg.wait_for_timeout(1000); mark("hold_end", n)
        await pg.click("#drafts summary"); await pg.wait_for_timeout(600)
        await pg.evaluate("document.querySelector('#drafts').scrollIntoView({block:'start', behavior:'smooth'})")
        await pg.wait_for_timeout(1200); mark("drafts_start", 5)
        await pg.screenshot(path=f"{OUT}/t05_drafts.png")
        await pg.wait_for_timeout(6000); mark("drafts_end", 5)
        v = pg.video; await ctx.close(); path = await v.path(); await b.close()
    shutil.move(path, f"{OUT}/run.webm")
    json.dump(tl, open(f"{OUT}/timeline.json", "w"), indent=1)
    for m in tl: print(f"{m['t']:7.2f}  t{m['turn']}  {m['name']}")
asyncio.run(main())
