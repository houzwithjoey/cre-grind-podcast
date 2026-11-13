"""Render a two-host podcast script to MP3.

Script format: one turn per paragraph, prefixed "MAYA:" or "DEV:".
Lines starting with "#" are ignored (section notes). "[MUSIC]" inserts a 2s pause.
Usage: python3 render.py script.txt out.mp3
Per-line audio is cached in ./cache/<script-stem>/ so an interrupted render resumes.
"""
import sys, os, re, hashlib, subprocess
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro

HERE = os.path.dirname(os.path.abspath(__file__))
# The CRE Grind: MAYA/DEV. CRE Deal Makers: NORA (lead narrator) / THEO (co-host), a bit faster.
VOICES = {"MAYA": ("af_heart", 1.05), "DEV": ("am_michael", 1.03),
          "NORA": ("af_bella", 1.12), "THEO": ("am_fenrir", 1.10)}
SR = 24000

# Spoken forms for terms the TTS would mangle.
PRON = {
    r"\bCMBS\b": "C M B S", r"\bCRE\b": "C R E", r"\bMTA\b": "M T A", r"\bKKR\b": "K K R", r"\bPIMCO\b": "pim co", r"\bQTS\b": "Q T S", r"L'Oréal": "Lor-ee-al", r"\bCBRE\b": "C B R E", r"\bKBRA\b": "K B R A", r"\bHUD\b": "H U D", r"\bREITs?\b": lambda m: "reets" if m.group(0).endswith("s") else "reet",
    r"\bDSCR\b": "D S C R", r"\bLTV\b": "L T V", r"\bLTC\b": "L T C", r"\bNOI\b": "N O I", r"\bIRR\b": "I R R",
    r"\bSOFR\b": "sofer", r"\bCLOs?\b": lambda m: "C L Os" if m.group(0).endswith("s") else "C L O",
    r"\bGSEs?\b": lambda m: "G S Es" if m.group(0).endswith("s") else "G S E", r"\bFed\b": "Fed",
    r"\bbps\b": "basis points", r"\bbp\b": "basis points", r"\bMSA\b": "M S A", r"\bRevPAR\b": "rev par",
    r"\bADR\b": "A D R", r"\bTI\b": "T I", r"\bNNN\b": "triple net", r"\bLP\b": "L P", r"\bGP\b": "G P",
    r"\bQ([1-4])\b": r"Q \1", r"\bvs\.?": "versus", r"\be\.g\.": "for example", r"\bi\.e\.": "that is",
    r"\bWALT\b": "walt", r"\bFFO\b": "F F O", r"\bAFFO\b": "A F F O", r"\bNAV\b": "N A V",
    r"\bA-note\b": "A note", r"\bB-note\b": "B note", r"\bIO\b": "interest only", r"\bSASB\b": "sass-bee",
    r"\bSF\b": "square feet", r"\bpsf\b": "per square foot", r"\bYoY\b": "year over year",
}

def speakable(t):
    for pat, rep in PRON.items():
        t = re.sub(pat, rep, t)
    t = re.sub(r"(\d)%", r"\1 percent", t)
    t = re.sub(r"\$(\d[\d,.]*)\s*(billion|million|trillion)", r"\1 \2 dollars", t)
    t = t.replace("—", ", ").replace("–", " to ")
    return t

def parse(path):
    turns, cur = [], None
    for raw in open(path, encoding="utf-8"):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line == "[MUSIC]":
            turns.append(("PAUSE", 2.0)); cur = None; continue
        m = re.match(r"^(" + "|".join(VOICES) + r"):\s*(.*)$", line)
        if m:
            cur = [m.group(1), m.group(2)]; turns.append(cur)
        elif cur:
            cur[1] += " " + line
    return turns

def chunks(text, n=380):
    # Kokoro handles ~500 chars well; split long turns at sentence boundaries.
    sents = re.split(r"(?<=[.!?])\s+", text)
    out, buf = [], ""
    for s in sents:
        if len(buf) + len(s) > n and buf:
            out.append(buf); buf = s
        else:
            buf = (buf + " " + s).strip()
    if buf: out.append(buf)
    return out

def main(script, out):
    k = Kokoro(os.path.join(HERE, "kokoro-v1.0.onnx"), os.path.join(HERE, "voices-v1.0.bin"))
    cache = os.path.join(HERE, "cache", os.path.splitext(os.path.basename(script))[0]); os.makedirs(cache, exist_ok=True)
    turns = parse(script); pieces = []; prev = None
    for i, t in enumerate(turns):
        if t[0] == "PAUSE":
            pieces.append(np.zeros(int(SR * t[1]), dtype=np.float32)); continue
        who, text = t
        voice, speed = VOICES[who]
        if prev is not None:
            gap = 0.45 if prev != who else 0.3
            pieces.append(np.zeros(int(SR * gap), dtype=np.float32))
        for c in chunks(speakable(text)):
            h = hashlib.md5(f"{voice}{speed}{c}".encode()).hexdigest()[:16]
            f = os.path.join(cache, h + ".npy")
            if os.path.exists(f):
                a = np.load(f)
            else:
                a, _ = k.create(c, voice=voice, speed=speed, lang="en-us"); np.save(f, a.astype(np.float32))
            pieces.append(a); pieces.append(np.zeros(int(SR * 0.12), dtype=np.float32))
        prev = who
        print(f"{i+1}/{len(turns)}", flush=True)
    audio = np.concatenate(pieces)
    wav = out.replace(".mp3", ".wav"); sf.write(wav, audio, SR)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
                    "-ac", "1", "-b:a", "96k", out], check=True)
    os.remove(wav)
    print(f"DONE {out} {len(audio)/SR/60:.1f} min")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
