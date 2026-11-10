import os
import re
import json
import pandas as pd
from docx import Document
from pathlib import Path

script_dir = Path(__file__).parent if "__file__" in locals() else Path.cwd()

def pulisci_testo(testo):
    if not isinstance(testo, str):
        return ""
    testo = testo.replace("“", '"').replace("”", '"').replace("’", "'").replace("`", "'")
    testo = re.sub(r'\[\d+\]', '', testo)
    testo = re.sub(r'[ \t]+', ' ', testo)
    testo = re.sub(r'\n\s*\n+', '\n\n', testo)
    return testo.strip()

def carica_testo_file(percorso):
    if percorso.suffix == '.docx':
        doc = Document(percorso)
        testo_completo = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        return "\n".join(testo_completo)
    elif percorso.suffix == '.txt':
        with open(percorso, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    return None

corpus_pulito = []

# Cerca tutti i file .txt e .docx nella cartella (sia script_ che Script_)
estensioni = ['*.txt', '*.docx']
file_trovati = []
for ext in estensioni:
    file_trovati.extend(list(script_dir.glob(f"script_*{ext[1:]}")))
    file_trovati.extend(list(script_dir.glob(f"Script_*{ext[1:]}")))

# Rimuove eventuali duplicati mantenendo l'ordine
file_trovati = list(dict.fromkeys(file_trovati))

cartella_output = script_dir / "dati_puliti"
cartella_output.mkdir(exist_ok=True)

for percorso in file_trovati:
    # Ignora i file temporanei di Word o i file di output puliti già generati
    if percorso.name.startswith("~$") or percorso.name.endswith("_pulito.docx"):
        continue
        
    testo_grezzo = carica_testo_file(percorso)
    if testo_grezzo:
        testo_pulito = pulisci_testo(testo_grezzo)
        
        # Assegna la categoria in base al nome
        nome_lower = percorso.stem.lower()
        if "reportage" in nome_lower:
            categoria = "Reportage"
        elif "intimista" in nome_lower:
            categoria = "Intimista"
        elif "divulgativo" in nome_lower:
            categoria = "Divulgativo"
        else:
            categoria = "Generale"

        corpus_pulito.append({
            "titolo": percorso.stem,
            "categoria": categoria,
            "file_origine": percorso.name,
            "lunghezza_caratteri": len(testo_pulito),
            "numero_parole": len(testo_pulito.split()),
            "testo": testo_pulito
        })

        # Salva la versione Word (.docx) sia dentro dati_puliti che nella cartella principale
        doc_out = Document()
        doc_out.add_heading(percorso.stem, level=1)
        for paragrafo in testo_pulito.split("\n\n"):
            doc_out.add_paragraph(paragrafo)
        
        doc_out.save(cartella_output / f"{percorso.stem}_pulito.docx")
        doc_out.save(script_dir / f"{percorso.stem}_pulito.docx")

        print(f"✅ Processato: {percorso.name} [{categoria}] ({len(testo_pulito.split())} parole)")

# 1. Salva in JSON dentro dati_puliti
with open(cartella_output / "corpus_podcast_pulito.json", "w", encoding="utf-8") as f:
    json.dump(corpus_pulito, f, ensure_ascii=False, indent=4)

# 2. Salva le tabelle Excel e CSV in tutte le destinazioni
df_corpus = pd.DataFrame(corpus_pulito)

# Salva nella cartella 'dati_puliti'
df_corpus.to_excel(cartella_output / "confronto_script_pulito.xlsx", index=False)
df_corpus.to_csv(cartella_output / "confronto_script_pulito.csv", index=False, encoding="utf-8-sig")

# Salva nella cartella principale (nuovo nome)
df_corpus.to_excel(script_dir / "confronto_script_pulito.xlsx", index=False)
df_corpus.to_csv(script_dir / "confronto_script_pulito.csv", index=False, encoding="utf-8-sig")

# Aggiorna anche il file originario nella cartella principale
df_corpus.to_excel(script_dir / "Confronto_Format_Troiane.xlsx", index=False)

print(f"\n🎉 Processati con successo {len(corpus_pulito)} script!")
print(f"📁 Aggiornati 'confronto_script_pulito.xlsx' e il file originario 'Confronto_Format_Troiane.xlsx'!")