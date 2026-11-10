import json
import re
import os
import pandas as pd
import spacy

# Carica il modello linguistico italiano di spaCy
try:
    nlp = spacy.load("it_core_news_sm")
except Exception:
    print("Modello spaCy non trovato. Esegui nel terminale: python -m spacy download it_core_news_sm")

INPUT_JSON = "corpus_troiane_arricchito.json"
OUTPUT_EXCEL = "analisi_stilometrica_corpus.xlsx"

def calcola_gulpease(testo):
    """
    Calcola l'indice Gulpease: 89 + (300 * nr_frasi - 10 * nr_lettere) / nr_parole
    """
    frasi = [f for f in re.split(r'[.!?]+', testo) if f.strip()]
    parole = re.findall(r'\b\w+\b', testo)
    lettere = sum(len(p) for p in parole)
    
    num_frasi = len(frasi) if len(frasi) > 0 else 1
    num_parole = len(parole) if len(parole) > 0 else 1
    
    gulpease = 89 + ((300 * num_frasi) - (10 * lettere)) / num_parole
    return round(gulpease, 2)

def analizza_script(record):
    testo = record["testo_script"]
    metadati = record["metadati"]
    doc = nlp(testo)
    
    # Tokenizzazione parole
    tokens_alphanumeric = [token.text.lower() for token in doc if token.is_alpha]
    num_tokens = len(tokens_alphanumeric)
    num_types = len(set(tokens_alphanumeric))
    
    # 1. Type-Token Ratio (TTR) - Ricchezza Lessicale
    ttr = round(num_types / num_tokens, 4) if num_tokens > 0 else 0
    
    # 2. Lunghezza media frasi e parole
    frasi = list(doc.sents)
    num_frasi = len(frasi) if len(frasi) > 0 else 1
    lunghezza_media_frasi = round(num_tokens / num_frasi, 2)
    lunghezza_media_parole = round(sum(len(t) for t in tokens_alphanumeric) / num_tokens, 2) if num_tokens > 0 else 0
    
    # 3. Indice Gulpease (Leggibilità)
    gulpease = calcola_gulpease(testo)
    
    # 4. Parti del Discorso (POS Tagging)
    pos_counts = {"NOUN": 0, "VERB": 0, "ADJ": 0, "PRON": 0}
    for token in doc:
        if token.pos_ in pos_counts:
            pos_counts[token.pos_] += 1
            
    perc_sostantivi = round((pos_counts["NOUN"] / num_tokens) * 100, 2) if num_tokens > 0 else 0
    perc_verbi = round((pos_counts["VERB"] / num_tokens) * 100, 2) if num_tokens > 0 else 0
    perc_aggettivi = round((pos_counts["ADJ"] / num_tokens) * 100, 2) if num_tokens > 0 else 0
    perc_pronomi = round((pos_counts["PRON"] / num_tokens) * 100, 2) if num_tokens > 0 else 0
    
    return {
        "ID Script": record["id_script"],
        "Nome File": record["nome_file"],
        "Format": metadati["format"],
        "Totale Parole (Tokens)": num_tokens,
        "Vocabolario Unico (Types)": num_types,
        "Ricchezza Lessicale (TTR)": ttr,
        "Indice Gulpease": gulpease,
        "Parole/Frase (Media)": lunghezza_media_frasi,
        "Lunghezza Media Parola": lunghezza_media_parole,
        "% Sostantivi": perc_sostantivi,
        "% Verbi": perc_verbi,
        "% Aggettivi": perc_aggettivi,
        "% Pronomi": perc_pronomi
    }

def esegui_analisi_corpus():
    if not os.path.exists(INPUT_JSON):
        print(f"Errore: Il file {INPUT_JSON} non esiste. Esegui prima arricchisci_corpus_troiane.py!")
        return

    with open(INPUT_JSON, 'r', encoding='utf-8') as f:
        corpus = json.load(f)
        
    risultati = [analizza_script(record) for record in corpus]
    
    # Tabella con dettaglio di ogni singolo script
    df_dettaglio = pd.DataFrame(risultati)
    
    # Tabella con le medie per Format (Reportage, Intimistico, Divulgativo)
    df_medie = df_dettaglio.groupby("Format").agg({
        "Totale Parole (Tokens)": "mean",
        "Ricchezza Lessicale (TTR)": "mean",
        "Indice Gulpease": "mean",
        "Parole/Frase (Media)": "mean",
        "Lunghezza Media Parola": "mean",
        "% Sostantivi": "mean",
        "% Verbi": "mean",
        "% Aggettivi": "mean",
        "% Pronomi": "mean"
    }).round(2).reset_index()
    
    # Salva entrambi i fogli nel file Excel (sovrascrive quello vecchio)
    with pd.ExcelWriter(OUTPUT_EXCEL) as writer:
        df_dettaglio.to_excel(writer, sheet_name="Dettaglio Script", index=False)
        df_medie.to_excel(writer, sheet_name="Confronto Format", index=False)
        
    print(f"Analisi completata con successo! File salvato/aggiornato in: {OUTPUT_EXCEL}")

if __name__ == "__main__":
    esegui_analisi_corpus()