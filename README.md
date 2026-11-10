# Analisi Stilometrica e Qualitativa: *Le Troiane* di Euripide in Format Podcast

Questo progetto realizza un'analisi integrata (quantitativa e qualitativa) di 15 adattamenti in formato script podcast basati su *Le Troiane* di Euripide, esplorando tre differenti registri stilistici (Reportage, Intimista e Didattico/Divulgativo).

## 📌 Obiettivi del Progetto
- Analisi Stilometrica Quantitativa: Calcolo e confronto di metriche testuali chiave quali il Type-Token Ratio (TTR), la lunghezza media delle frasi e l'indice di leggibilità Gulpease.
- Analisi Qualitativa tramite LLM: Valutazione assistita dall'API di Google Gemini per analizzare tono di voce, struttura narrativa e scelte interpretative nei diversi format.
- Visualizzazione e Reportistica: Generazione di grafici comparativi e di un dossier/report finale riassuntivo in formato HTML e PDF.

## 📁 Struttura della Repository
- `dati_puliti/`: Contiene il corpus dei testi e degli script rielaborati.
- `analisi_corpus.py`: Script Python per il calcolo delle metriche stilometriche quantitative.
- `analisi_qualitativa_llm.py`: Script per l'estrazione delle analisi qualitative tramite l'API di Gemini.
- `genera_report_finale.py`: Script per la generazione e l'assemblaggio del report finale visivo.
- `*.xlsx` / `*.json`: Dataset ed elaborati con i dati quantitativi e qualitativi.
- `*.png`: Grafici comparativi generati dall'analisi dati.
- `report_finale_podcast.html`: Report interattivo e completo del progetto.

## 🛠️ Tecnologie Utilizzate
- **Python 3.x**
- **Librerie Python**: `pandas`, `matplotlib`, `seaborn`, `spacy`
- **Generative AI**: API di Google Gemini (`google-genai`) per l'analisi qualitativa
- **Formattazione**: HTML5 / CSS3 per il report finale

---
*Progetto accademico per la valutazione e l'adattamento delle opere classiche tramite strumenti d'IA e stilometria computazionale.*