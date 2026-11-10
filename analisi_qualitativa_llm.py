import os
import json
import time
import re
import pandas as pd
from google import genai
from google.genai import types

API_KEY = os.getenv("GEMINI_API_KEY")
INPUT_JSON = "corpus_troiane_arricchito.json"
OUTPUT_JSON = "analisi_qualitativa_risultati.json"
OUTPUT_EXCEL = "analisi_qualitativa_corpus.xlsx"

client = genai.Client(api_key=API_KEY)

PROMPT_ISTRUZIONI = """
Sei un esperto di analisi del testo e drammaturgia applicata al media podcast.
Analizza il seguente script di un podcast basato su 'Le Troiane' di Euripide.

Estrai le seguenti informazioni qualitative in modo preciso e conciso:
1. Target di pubblico principale.
2. Tono di voce e stile comunicativo.
3. Struttura narrativa adottata.
4. Principali temi chiave trattati (max 3-4 temi).
5. Presenza e tipologia di citazioni testuali.
6. Uso di figure retoriche prevalenti.
7. Valutazione sintetica dell'efficacia rispetto al format dichiarato.
"""

def pulisci_testo(valore):
    """Rimuove i caratteri di controllo non stampabili che bloccano openpyxl/Excel."""
    if isinstance(valore, str):
        # Rimuove tutti i caratteri di controllo ASCII non validi per Excel
        return re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F-\x9F]', '', valore)
    elif isinstance(valore, list):
        return [pulisci_testo(x) for x in valore]
    elif isinstance(valore, dict):
        return {k: pulisci_testo(v) for k, v in valore.items()}
    return valore

def analizza_script_con_llm(record):
    testo = record["testo_script"]
    metadati = record["metadati"]
    
    prompt = f"{PROMPT_ISTRUZIONI}\n\nFORMAT DICHIARATO: {metadati['format']}\n\nTESTO SCRIPT:\n{testo}"
    
    tentativo = 1
    while tentativo <= 5:
        try:
            response = client.models.generate_content(
                model='gemini-3.8-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema={
                        "type": "OBJECT",
                        "properties": {
                            "target_pubblico": {"type": "STRING"},
                            "tono_di_voce": {"type": "STRING"},
                            "struttura_narrativa": {"type": "STRING"},
                            "temi_chiave": {
                                "type": "ARRAY",
                                "items": {"type": "STRING"}
                            },
                            "citazioni_testuali": {"type": "STRING"},
                            "figure_retoriche": {
                                "type": "ARRAY",
                                "items": {"type": "STRING"}
                            },
                            "valutazione_efficacia": {"type": "STRING"}
                        },
                        "required": [
                            "target_pubblico", 
                            "tono_di_voce", 
                            "struttura_narrativa", 
                            "temi_chiave", 
                            "citazioni_testuali", 
                            "figure_retoriche", 
                            "valutazione_efficacia"
                        ]
                    }
                )
            )
            
            analisi_json = json.loads(response.text)
            
            res = {
                "ID Script": record["id_script"],
                "Nome File": record["nome_file"],
                "Format": metadati["format"],
                "Target Pubblico": analisi_json.get("target_pubblico", ""),
                "Tono di Voce": analisi_json.get("tono_di_voce", ""),
                "Struttura Narrativa": analisi_json.get("struttura_narrativa", ""),
                "Temi Chiave": ", ".join(analisi_json.get("temi_chiave", [])),
                "Citazioni Testuali": analisi_json.get("citazioni_testuali", ""),
                "Figure Retoriche": ", ".join(analisi_json.get("figure_retoriche", [])),
                "Valutazione Efficacia": analisi_json.get("valutazione_efficacia", "")
            }
            
            return pulisci_testo(res)
            
        except Exception as e:
            print(f" -> Attesa per {record['id_script']} (tentativo {tentativo}): {e}")
            tentativo += 1
            time.sleep(15)

    return None

def esegui_analisi_qualitativa():
    if not os.path.exists(INPUT_JSON):
        print(f"Errore: File {INPUT_JSON} non trovato.")
        return

    with open(INPUT_JSON, 'r', encoding='utf-8') as f:
        corpus = json.load(f)

    risultati = []
    ids_gia_analizzati = set()
    if os.path.exists(OUTPUT_JSON):
        try:
            with open(OUTPUT_JSON, 'r', encoding='utf-8') as f:
                risultati_grezzi = json.load(f)
                # Puliamo anche tutti i risultati storici gia' presenti nel JSON
                risultati = [pulisci_testo(r) for r in risultati_grezzi]
                ids_gia_analizzati = {r["ID Script"] for r in risultati if "ID Script" in r}
                print(f"Trovati {len(ids_gia_analizzati)} script gia' completati.")
        except Exception:
            risultati = []

    print(f"Analisi su {len(corpus)} script totali ({len(corpus) - len(ids_gia_analizzati)} da elaborare)...")

    for record in corpus:
        script_id = record['id_script']
        
        if script_id in ids_gia_analizzati:
            print(f"Gia' presente, salto: {script_id}")
            continue

        print(f"Elaborazione in corso: {script_id} ({record['nome_file']})...")
        risultato = analizza_script_con_llm(record)
        
        if risultato is not None:
            risultati.append(risultato)
            ids_gia_analizzati.add(script_id)
            
            # Salvataggio JSON pulito
            with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
                json.dump(risultati, f, ensure_ascii=False, indent=2)
            
            # Salvataggio Excel con pulizia preventiva di tutti i campi
            risultati_puliti = [pulisci_testo(r) for r in risultati]
            df = pd.DataFrame(risultati_puliti)
            df.to_excel(OUTPUT_EXCEL, index=False)
            print(f" -> Salvato con successo!")
        else:
            print(f" -> Impossibile elaborare {script_id} al momento.")

        time.sleep(10)

    print(f"\nAnalisi Qualitativa COMPLETATA PER TUTTI GLI SCRIPT!")
    print(f"File salvati: {OUTPUT_JSON} e {OUTPUT_EXCEL}")

if __name__ == "__main__":
    esegui_analisi_qualitativa()