// Drive the real Hobson web view and record it.
// Prereq: uvicorn hobson.web:app --port 8000 is running, and `npm i playwright` (uses the Chromium Playwright ships).
// Usage: node demo/record.mjs            -> demo/rec/run.webm, demo/rec/timeline.json, demo/rec/<turn>_full.png, <turn>_panel.png
import { chromium } from "playwright";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const here = path.dirname(fileURLToPath(import.meta.url));
const OUT = path.join(here, "rec");
fs.rmSync(OUT, { recursive: true, force: true });
fs.mkdirSync(OUT, { recursive: true });

const narration = JSON.parse(fs.readFileSync(path.join(here, "narration.json"), "utf8"));
const turns = narration.scenes.filter(s => s.kind === "clip" && s.action);
const SEED = process.env.SEED || "7";
const W = 1280, H = 800;

const browser = await chromium.launch();
const ctx = await browser.newContext({
  viewport: { width: W, height: H },
  deviceScaleFactor: 1,
  recordVideo: { dir: OUT, size: { width: W, height: H } },
});
const page = await ctx.newPage();
const t0 = Date.now();
const mark = (name) => ({ name, t: (Date.now() - t0) / 1000 });
const timeline = [];

await page.goto(`http://localhost:8000/?seed=${SEED}`, { waitUntil: "networkidle" });
await page.waitForSelector("#story .scene", { timeout: 60000 });
await page.waitForTimeout(1500);
timeline.push({ ...mark("open_start"), turn: 0 });
await page.screenshot({ path: path.join(OUT, "t00_full.png") });
await page.waitForTimeout(6000);
timeline.push({ ...mark("open_end"), turn: 0 });

for (const s of turns) {
  const n = s.turn;
  const timingBefore = await page.textContent("#timing").catch(() => "");
  timeline.push({ ...mark("type_start"), turn: n });
  await page.click("#action");
  await page.type("#action", s.action, { delay: 55 });
  await page.waitForTimeout(500);
  await page.press("#action", "Enter");
  timeline.push({ ...mark("submitted"), turn: n });
  // wait until the timing line changes (rulings + narration landed) and rows have animated in
  await page.waitForFunction(
    (prev) => { const t = document.querySelector("#timing")?.textContent || ""; return t && t !== prev; },
    timingBefore, { timeout: 120000 }
  );
  await page.waitForTimeout(2500);
  timeline.push({ ...mark("result"), turn: n });
  await page.screenshot({ path: path.join(OUT, `t0${n}_full.png`) });
  // panel crop for the zoom shots
  const panel = await page.$("#rows");
  const box = await panel.boundingBox();
  const timing = await (await page.$("#timing")).boundingBox();
  await page.screenshot({
    path: path.join(OUT, `t0${n}_panel.png`),
    clip: { x: box.x - 12, y: box.y - 12, width: box.width + 24, height: (timing.y + timing.height) - box.y + 24 },
  });
  await page.waitForTimeout(4000);
  timeline.push({ ...mark("hold_end"), turn: n });
}

// drafts fold-out + ledger
await page.click("#drafts summary");
await page.waitForTimeout(600);
await page.evaluate(() => document.querySelector("#drafts").scrollIntoView({ block: "start", behavior: "smooth" }));
await page.waitForTimeout(1200);
timeline.push({ ...mark("drafts_start"), turn: 5 });
await page.screenshot({ path: path.join(OUT, "t05_drafts.png") });
await page.waitForTimeout(6000);
timeline.push({ ...mark("drafts_end"), turn: 5 });

const video = page.video();
await ctx.close();
const vpath = await video.path();
fs.renameSync(vpath, path.join(OUT, "run.webm"));
await browser.close();
fs.writeFileSync(path.join(OUT, "timeline.json"), JSON.stringify(timeline, null, 2));
console.log("recorded", path.join(OUT, "run.webm"));
console.table(timeline);
