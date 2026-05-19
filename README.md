# STP & Human Touches — Streamlit App

Forenklet STP-dashbord for SpareBank 1 Forvaltning.

## Kjør lokalt

```bash
pip install -r requirements.txt
streamlit run app.py
```

App åpnes på http://localhost:8501

## Faner

### 📊 Oversikt
- **Overall STP-grad** (KPI)
- **Samlet Human Touches** (KPI)
- **Svakeste arbeidsflyt** (KPI)
- **STP-grad per arbeidsflyt** — horisontalt søylediagram, fargekodet
- **Human Touches per arbeidsflyt** — horisontalt søylediagram
- **Heatmap** — STP-grad per arbeidsflyt × steg

### ⚙️ Data
Fire kolonner:
1. **Arbeidsflyt (navn)** — overordnet prosess (Tegning, Innløsning, etc.)
2. **Navn på steg i arbeidsflyt** — delsteg
3. **STP-grad** — prosent 0–100
4. **Human Touch** — antall manuelle inngrep

Funksjoner: legg til / endre / slett rader, lagre, tilbakestill, last ned CSV.

## Tema

Lys / Mørk modus byttes med radioknapp øverst til høyre.
Begge modusene bruker SpareBank 1-paletten — Vann/Fjell på lys bakgrunn,
Frost/Syrin på mørk bakgrunn for god kontrast.

## Branding

SpareBank 1 fargepalett:
- Vann (primær), Fjell (sekundær), Frost, Syrin, Sand
- Nordlys (innenfor SLA), Sol (varsel), Bær (brudd)
