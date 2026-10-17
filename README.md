# copy-poradce

Skill pro Claude Code, který píše a reviduje české klientské texty (blogy, newslettery, direct e-maily, weby, landing pages) podle stylového profilu a sady pravidel copywritingu.

Osobní nástroj jednoho autora. Profil stylu a pravidla jsou vytěžené z korpusu 111 blogových článků, který v repu není.

## Co je uvnitř

- `SKILL.md`: postup dvou režimů (napsat text, revize a poradenství) a hranice použití
- `references/styl.md`: stylometrický profil, čísla, rysy, otvíráky, závěry, titulky
- `references/znalosti.md`: 144 pravidel se zdroji a uvedenými rozpory
- `scripts/stylo.py`: stylometrie hotového textu proti `scripts/profil.json` přes UDPipe na LINDAT (potřebuje internet)
- `scripts/prekryv.py`: počet doslovných 8-gramů sdílených s korpusem (má být 0)

## Install

Zkopíruj nebo naklonuj repo do adresáře skillů Claude Code:

```bash
git clone https://github.com/koprjaa/copy-poradce ~/.claude/skills/copy-poradce
```

Skripty jsou čistý Python 3 bez závislostí. `prekryv.py` vyžaduje proměnnou prostředí `COPY_KORPUS` s cestou k adresáři se soubory korpusu `.md`. Bez vlastního korpusu ho nespustíš.

## Use

V Claude Code popros zadání ("napiš newsletter o ...", "zreviduj tenhle text"). Skill se spustí sám.

Kontrola hotového textu:

```bash
python3 scripts/stylo.py porovnej scripts/profil.json text.md
COPY_KORPUS=/cesta/ke/korpusu python3 scripts/prekryv.py text.md
```
