import os
import json
import docx
import pandas as pd

CARTELLA_DATI_PULITI = "dati_puliti"
OUTPUT_JSON = "corpus_troiane_arricchito.json"

def leggi_testo_file(filepath):
    """
    Legge il testo del file in base alla sua estensione (.txt, .docx, .xlsx).
    """
    estensione = os.path.splitext(filepath)[1].lower()
    testo = ""
    
    if estensione == '.docx':
        doc = docx.Document(filepath)
        testo = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
    elif estensione in ['.xlsx', '.xls']:
        df = pd.read_excel(filepath)
        testo = "\n".join(df.astype(str).values.flatten())
    elif estensione == '.txt':
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            testo = f.read().strip()
            
    return testo

def mappa_metadati_file(nome_file):
    """
    Mappa il format corretto in base al nome del file dello script.
    """
    nome_lower = nome_file.lower()
    
    if "reportage" in nome_lower:
        format_podcast = "Reportage"
    elif "intimistico" in nome_lower or "intimist" in nome_lower:
        format_podcast = "Intimistico"
    elif "divulgativo" in nome_lower or "divulg" in nome_lower:
        format_podcast = "Divulgativo"
    else:
        format_podcast = "Non specificato"
        
    return {
        "format": format_podcast,
        "opera_origine": "Le Troiane",
        "autore_originale": "Euripide",
        "anno_rappresentazione_originale": "415 a.C.",
        "contesto_storico_originale": "Guerra del Peloponneso / Assedio di Melo"
    }

def crea_corpus_arricchito():
    corpus_arricchito = []
    
    estensioni_valide = ('.txt', '.docx', '.xlsx', '.xls')
    
    # Prende tutti i file validi ma ESCLUDE i file di analisi/confronto ed i file temporanei
    files = [
        f for f in os.listdir(CARTELLA_DATI_PULITI) 
        if f.endswith(estensioni_valide) 
        and not f.startswith('~$')
        and not f.lower().startswith('analisi_')
        and not f.lower().startswith('confronto_')
    ]
    files.sort()
    
    for idx, filename in enumerate(files, start=1):
        filepath = os.path.join(CARTELLA_DATI_PULITI, filename)
        
        testo_podcast = leggi_testo_file(filepath)
        
        if not testo_podcast:
            continue
            
        metadati = mappa_metadati_file(filename)
        
        record = {
            "id_script": f"script_{idx:02d}",
            "nome_file": filename,
            "metadati": metadati,
            "testo_script": testo_podcast
        }
        
        corpus_arricchito.append(record)
        
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(corpus_arricchito, f, ensure_ascii=False, indent=2)
        
    print(f"Completato! Elaborati {len(corpus_arricchito)} file di script dei podcast.")
    print(f"File salvato in: {OUTPUT_JSON}")

if __name__ == "__main__":
    crea_corpus_arricchito()