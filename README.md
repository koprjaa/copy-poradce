# copy-poradce

Copywritingový skill pro Claude Code: píše a reviduje klientské texty (blogy, newslettery, direct e-maily, weby, landing pages) v úderném českém autorském stylu a radí dle ověřených pravidel. Zadání a pracovní režimy (napsat text / revize a poradenství) jsou v [SKILL.md](SKILL.md) — repo se instaluje jako dovednost Claude Code (`~/.claude-work/skills/copy-poradce`).

## Co je uvnitř

- [SKILL.md](SKILL.md) — postup obou režimů, hranice (nepodepisovat cizím jménem, žádná doslovná převzetí z korpusu)
- `references/styl.md` — stylometrický profil autora: čísla, rysy, kontrastní páry, otvíráky/závěry/titulky, čemu se vyhnout; číst celý před psaním
- `references/znalosti.md` — 144 pravidel copywritingu sloučených z 452 dílčích záznamů (88 článků), každé s pokynem, zdůvodněním a zdroji, rozpory mezi články otevřeně uvedeny
- `scripts/stylo.py` — stylometrie hotového textu proti profilu (`profil.json`) přes UDPipe/LINDAT, potřebuje internet; `mimo_iqr` = rysy mimo běžný rozsah autora
- `scripts/prekryv.py` — kontrola, že text nesdílí s korpusem doslovné 8-gramy (musí být 0)
