#
# Project: copy-poradce
# File:    prekryv.py
#
# Description:
# Computes the number of shared n-grams between input files and a reference corpus.
#
# Author:
# Jan Alexandr Kopřiva
# jan.alexandr.kopriva@gmail.com
#
# License: AGPL-3.0-or-later
#

# Kontrola doslovného přebírání: sdílené 8-gramy slov mezi vygenerovanými texty a celým korpusem.
# python3 prekryv.py vystup1.md vystup2.md ...
import os
import pathlib
import re
import sys

ROOT = pathlib.Path(os.environ["COPY_KORPUS"])  # adresář s .md články, není součástí repa
N = 8
grams = lambda t: (lambda w: {tuple(w[i : i + N]) for i in range(len(w) - N + 1)})(
    re.findall(r"\w+", t.lower())
)
korpus = set().union(*(grams(f.read_text()) for f in ROOT.glob("[01]*.md")))
celkem = 0
for p in sys.argv[1:]:
    g = grams(pathlib.Path(p).read_text())
    hit = g & korpus
    celkem += len(hit)
    print(
        f"{p}: {len(hit)} sdílených {N}-gramů z {len(g)}", *[" ".join(h) for h in list(hit)[:3]], sep="\n  "
    )
print("CELKEM", celkem)
