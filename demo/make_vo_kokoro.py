#!/usr/bin/env python3
"""Voice-over with Kokoro (local, free). One MP3 per scene -> demo/vo/<id>.mp3
Usage: python3 make_vo_kokoro.py [voice] [speed]      default af_heart 0.95
Needs: pip install kokoro-onnx soundfile ; kokoro-v1.0.onnx + voices-v1.0.bin next to this file
(https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.0)
"""
import json, os, sys, subprocess
import soundfile as sf
from kokoro_onnx import Kokoro

HERE = os.path.dirname(os.path.abspath(__file__))
voice = sys.argv[1] if len(sys.argv) > 1 else "af_heart"
speed = float(sys.argv[2]) if len(sys.argv) > 2 else 0.95
lang = "en-gb" if voice.startswith("b") else "en-us"
os.makedirs(f"{HERE}/vo", exist_ok=True)
k = Kokoro(f"{HERE}/kokoro-v1.0.onnx", f"{HERE}/voices-v1.0.bin")
for s in json.load(open(f"{HERE}/narration.json"))["scenes"]:
    out = f"{HERE}/vo/{s['id']}.mp3"
    if os.path.exists(out): print("skip", s["id"]); continue
    audio, sr = k.create(s["vo"], voice=voice, speed=speed, lang=lang)
    wav = out[:-4] + ".wav"; sf.write(wav, audio, sr)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-c:a", "libmp3lame", "-q:a", "3", out], check=True)
    os.remove(wav); print(f"ok   {s['id']:<14} {len(audio)/sr:5.1f}s  {voice}")
