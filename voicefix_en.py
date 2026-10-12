"""English voice fallback for BoomBooKidsTV: if Microsoft edge-tts is blocked (HTTP 403),
use the free offline Piper voices instead.

cartoon: voicefix_en.install(cizgi_bolum, "say")   kids Short: voicefix_en.install(kids, "tts")
"""
import os
import subprocess
import sys
import time
import urllib.request
import wave
from pathlib import Path

import numpy as np

BASE = "https://huggingface.co/rhasspy/piper-voices/resolve/main/"
MODELS = {"lessac": "en/en_US/lessac/medium/en_US-lessac-medium",
          "amy": "en/en_US/amy/medium/en_US-amy-medium",
          "ryan": "en/en_US/ryan/medium/en_US-ryan-medium"}
# character -> (model, pitch factor, length scale)
CAST = {"anlatici": ("lessac", 1.0, 1.0), "mina": ("amy", 1.08, 0.95), "efe": ("amy", 1.22, 0.92),
        "dede": ("ryan", 0.92, 1.05), "kid": ("amy", 1.12, 1.0)}
STATE = {"edge_dead": False, "paths": {}}


def _log(*a):
    print(*a, flush=True)


def _model(name):
    if name in STATE["paths"]:
        return STATE["paths"][name]
    try:
        import piper  # noqa: F401
    except Exception:  # noqa: BLE001
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "piper-tts"], check=False)
    cache = Path.home() / ".cache" / "piper"
    cache.mkdir(parents=True, exist_ok=True)
    order = [name] + [n for n in MODELS if n != name]
    for n in order:
        v = MODELS[n]
        stem = v.split("/")[-1]
        try:
            for suf in (".onnx", ".onnx.json"):
                p = cache / (stem + suf)
                if not p.exists() or p.stat().st_size < 100:
                    with urllib.request.urlopen(BASE + v + suf, timeout=180) as r:
                        p.write_bytes(r.read())
            STATE["paths"][name] = str(cache / (stem + ".onnx"))
            _log("  piper voice:", name, "->", stem)
            return STATE["paths"][name]
        except Exception as e:  # noqa: BLE001
            _log("  piper voice download failed:", stem, e)
    raise RuntimeError("no piper voice")


def piper_audio(text, who, work, idx, sr):
    model, pitch, length = CAST.get(who, CAST["anlatici"])
    raw, wav = Path(work) / f"p{idx}_raw.wav", Path(work) / f"p{idx}.wav"
    subprocess.run([sys.executable, "-m", "piper", "-m", _model(model), "-f", str(raw),
                    "--length-scale", str(length)], input=text.encode("utf-8"), check=True, timeout=300)
    with wave.open(str(raw)) as w:
        base_sr = w.getframerate()
    af = f"asetrate={int(base_sr * pitch)},aresample={sr},atempo={1 / pitch:.4f}" if pitch != 1.0 else f"aresample={sr}"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw), "-ac", "1", "-af", af, "-ar", str(sr), str(wav)],
                   check=True)
    with wave.open(str(wav)) as w:
        return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768


def install(mod, fname):
    orig = getattr(mod, fname)
    sr = mod.SR
    # edge-tts first, but give up quickly once it is blocked
    real_sleep = mod.time.sleep

    def edge_try(call):
        if STATE["edge_dead"]:
            return None
        mod.time.sleep = lambda s: real_sleep(min(s, 3))
        try:
            return call()
        except Exception as e:  # noqa: BLE001
            _log("  edge-tts unavailable, switching to free Piper voices:", str(e)[:120])
            STATE["edge_dead"] = True
            return None
        finally:
            mod.time.sleep = real_sleep

    if fname == "say":   # cartoon: say(lang, who, text, work, idx, offline) -> audio
        def say(lang, who, text, work, idx, offline):
            if offline:
                return orig(lang, who, text, work, idx, offline)
            r = edge_try(lambda: orig(lang, who, text, work, idx, offline))
            if r is not None:
                return r
            for a in range(2):
                try:
                    return piper_audio(text, who, work, idx, sr)
                except Exception as e:  # noqa: BLE001
                    _log("  piper retry", a, e)
                    real_sleep(3)
            raise RuntimeError("tts failed")
        setattr(mod, fname, say)
    else:                # kids Short: tts(text, work, i, offline) -> (audio, words)
        def tts(text, work, i, offline=False):
            if offline:
                return orig(text, work, i, offline)
            r = edge_try(lambda: orig(text, work, i, offline))
            if r is not None:
                return r
            for a in range(2):
                try:
                    audio = piper_audio(text, "kid", work, i, sr)
                    toks, dur = text.split(), len(audio) / sr
                    words = [(j * dur / len(toks), (j + 1) * dur / len(toks), tk) for j, tk in enumerate(toks)]
                    return audio, words
                except Exception as e:  # noqa: BLE001
                    _log("  piper retry", a, e)
                    real_sleep(3)
            raise RuntimeError("tts failed")
        setattr(mod, fname, tts)
