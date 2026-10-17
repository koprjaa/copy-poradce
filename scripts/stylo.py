#
# Project: copy-poradce
# File:    stylo.py
#
# Description:
# Computes Czech stylometric features using the UDPipe REST API.
#
# Author:
# Jan Alexandr Kopřiva
# jan.alexandr.kopriva@gmail.com
#
# License: MIT
#

# Stylometrie českých textů přes UDPipe (LINDAT REST). Bez externích závislostí.
# python3 stylo.py profil train_set.txt          -> profil.json (rozsahy + centroid lemmat)
# python3 stylo.py porovnej profil.json a.md b.md -> rysy + Burrowsova Delta k autorovi
import hashlib
import json
import pathlib
import re
import statistics as st
import sys
import urllib.parse
import urllib.request

HERE = pathlib.Path(__file__).parent
ROOT = HERE.parent
CACHE = pathlib.Path("/tmp/copy-poradce-conllu")
CACHE.mkdir(exist_ok=True)


def plain(md):
    lines = md.splitlines()
    if lines and lines[0].startswith("# ") and len(lines) > 3 and lines[3].startswith("http"):
        lines = lines[4:]  # hlavička z stahni.py: titulek, meta, url
    t = "\n".join(lines)
    t = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", t)
    t = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", t)
    t = re.sub(r"[*_#>`]+", "", t)
    return re.sub(r"\n{3,}", "\n\n", t).strip()


def parse(text):
    f = CACHE / (hashlib.sha1(text.encode()).hexdigest() + ".conllu")
    if not f.exists():
        data = urllib.parse.urlencode(
            {"model": "czech", "tokenizer": "", "tagger": "", "data": text}
        ).encode()
        r = urllib.request.urlopen(
            "https://lindat.mff.cuni.cz/services/udpipe/api/process", data, timeout=120
        )
        f.write_text(json.load(r)["result"])
    sents, cur = [], []
    for line in f.read_text().splitlines():
        if line.startswith("# newpar"):
            sents.append("PAR")
        elif not line.strip():
            if cur:
                sents.append(cur)
                cur = []
        elif not line.startswith("#"):
            c = line.split("\t")
            if "-" not in c[0] and "." not in c[0]:
                cur.append((c[1], c[2].lower(), c[3], c[5]))
    if cur:
        sents.append(cur)
    return sents


def features(md):
    text = plain(md)
    sents = parse(text)
    toks = [t for s in sents if s != "PAR" for t in s]
    words = [t for t in toks if t[2] != "PUNCT"]
    n = max(len(words), 1)
    slen = [sum(t[2] != "PUNCT" for t in s) for s in sents if s != "PAR"]
    pars, c = [], 0
    for s in sents:
        if s == "PAR":
            if c:
                pars.append(c)
            c = 0
        else:
            c += 1
    if c:
        pars.append(c)
    pos = lambda p: sum(t[2] == p for t in words) / n
    lem = [t[1] for t in words]
    win = 100
    mattr = (
        st.mean(len(set(lem[i : i + win])) / win for i in range(max(len(lem) - win, 1)))
        if len(lem) > win
        else len(set(lem)) / n
    )
    finite = [t for t in words if "VerbForm=Fin" in t[3] or "Mood=Imp" in t[3]]
    nf = max(len(finite), 1)
    pers = lambda p, num: sum(f"Person={p}" in t[3] and f"Number={num}" in t[3] for t in finite) / nf
    k = 1000 / n
    raw = md  # markdown kvůli tučnému, nadpisům, odrážkám
    return {
        "slov": n,
        "veta_prumer": round(st.mean(slen), 2),
        "veta_median": st.median(slen),
        "veta_p90": sorted(slen)[int(len(slen) * 0.9)] if slen else 0,
        "kratke_vety_do5": round(sum(x <= 5 for x in slen) / len(slen), 3),
        "vet_na_odstavec": round(st.mean(pars), 2),
        "VERB": round(pos("VERB"), 4),
        "NOUN": round(pos("NOUN"), 4),
        "ADJ": round(pos("ADJ"), 4),
        "ADV": round(pos("ADV"), 4),
        "PRON": round(pos("PRON"), 4),
        "MATTR100": round(mattr, 4),
        "osoba1sg": round(pers(1, "Sing"), 3),
        "osoba2sg_ty": round(pers(2, "Sing"), 3),
        "osoba2pl_vy": round(pers(2, "Plur"), 3),
        "otazky_podil": round(sum(1 for s in sents if s != "PAR" and s[-1][0] == "?") / len(slen), 3),
        "vykricniky_podil": round(sum(1 for s in sents if s != "PAR" and s[-1][0] == "!") / len(slen), 3),
        "pomlcky_k": round((text.count("–") + text.count("—")) * k, 2),
        "tecky3_k": round((text.count("…") + text.count("...")) * k, 2),
        "dvojtecky_k": round(text.count(":") * k, 2),
        "zavorky_k": round(text.count("(") * k, 2),
        "uvozovky_k": round((text.count("„") + text.count('"')) * k, 2),
        "tucne_k": round(raw.count("**") / 2 * k, 2),
        "nadpisy_k": round(len(re.findall(r"^#{2,} *[^\s\[!]", raw, re.M)) * k, 2),
        "odrazky_k": round(len(re.findall(r"^\s*[-*] ", raw, re.M)) * k, 2),
        "CAPS_k": round(len(re.findall(r"\b[A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ]{3,}\b", raw)) * k, 2),
        "_lemmata": lem,
    }


def freqs(lem, vocab):
    n = max(len(lem), 1)
    c = {}
    for l in lem:
        c[l] = c.get(l, 0) + 1
    return [c.get(w, 0) / n for w in vocab]


def profil(listfile):
    files = [ROOT / l.strip() for l in open(listfile) if l.strip()]
    feats = [features(f.read_text()) for f in files]
    keys = [k for k in feats[0] if not k.startswith("_") and k != "slov"]
    q = lambda xs, p: sorted(xs)[int((len(xs) - 1) * p)]
    rozsahy = {
        k: {
            "p25": q([f[k] for f in feats], 0.25),
            "median": q([f[k] for f in feats], 0.5),
            "p75": q([f[k] for f in feats], 0.75),
        }
        for k in keys
    }
    allc = {}
    for f in feats:
        for l in f["_lemmata"]:
            allc[l] = allc.get(l, 0) + 1
    vocab = [w for w, _ in sorted(allc.items(), key=lambda x: -x[1])[:150]]
    M = [freqs(f["_lemmata"], vocab) for f in feats]
    mu = [st.mean(col) for col in zip(*M)]
    sd = [st.pstdev(col) or 1e-9 for col in zip(*M)]
    out = {"clanku": len(files), "rozsahy": rozsahy, "vocab": vocab, "mu": mu, "sd": sd}
    (HERE / "profil.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
    print(json.dumps(rozsahy, ensure_ascii=False, indent=1))
    print("top lemmata:", " ".join(vocab[:60]))


def porovnej(pfile, paths):
    p = json.load(open(pfile))
    z = lambda lem: [(f - m) / s for f, m, s in zip(freqs(lem, p["vocab"]), p["mu"], p["sd"])]
    res = {}
    for path in paths:
        f = features(pathlib.Path(path).read_text())
        r = {k: v for k, v in f.items() if not k.startswith("_")}
        # mimo IQR autora = kolik rysů padá mimo p25–p75
        r["mimo_iqr"] = [k for k, v in p["rozsahy"].items() if not (v["p25"] <= f[k] <= v["p75"])]
        # Burrowsova Delta k centroidu autora (průměr |z| přes top-150 lemmat), nižší = blíž
        r["delta_k_autorovi"] = round(st.mean(abs(x) for x in z(f["_lemmata"])), 3)
        res[path] = r
    return res


if __name__ == "__main__":
    if sys.argv[1] == "profil":
        profil(sys.argv[2])
    else:
        print(json.dumps(porovnej(sys.argv[2], sys.argv[3:]), ensure_ascii=False, indent=1))
