import os
import json
import pandas as pd
import matplotlib.pyplot as plt

INPUT_QUAL = "analisi_qualitativa_risultati.json"
INPUT_STILO = "analisi_stilometrica_corpus.xlsx"
OUTPUT_HTML = "report_finale_podcast.html"
GRAFICO_FORMAT = "distribuzione_format.png"
GRAFICO_GULPEASE = "confronto_gulpease.png"
GRAFICO_TTR = "confronto_ttr.png"
GRAFICO_PAROLE = "confronto_parole.png"

def main():
    if not os.path.exists(INPUT_QUAL) or not os.path.exists(INPUT_STILO):
        print("Errore: File JSON qualitativo o file Excel stilometrico mancante.")
        return

    with open(INPUT_QUAL, 'r', encoding='utf-8') as f:
        dati_qual = json.load(f)
    df_qual = pd.DataFrame(dati_qual)
    df_stilo = pd.read_excel(INPUT_STILO)

    df_unito = pd.concat([df_qual.reset_index(drop=True), df_stilo.reset_index(drop=True)], axis=1)
    df_unito = df_unito.loc[:, ~df_unito.columns.duplicated()]

    format_col = next((col for col in df_unito.columns if col.lower() in ["format", "formato"]), None)
    gulpease_col = next((col for col in df_unito.columns if "gulpease" in col.lower()), None)
    ttr_col = next((col for col in df_unito.columns if any(k in col.lower() for k in ["ttr", "type", "token", "ricchezza"])), None)
    parole_col = next((col for col in df_unito.columns if any(k in col.lower() for k in ["parole", "word", "lunghezza"])), None)

    tot_script = len(df_unito)
    format_frequente = df_unito[format_col].mode()[0] if format_col and not df_unito[format_col].empty else "N/D"
    media_gulpease = f"{df_unito[gulpease_col].mean():.1f}" if gulpease_col and not df_unito[gulpease_col].empty else "N/D"
    media_parole = f"{df_unito[parole_col].mean():.0f}" if parole_col and not df_unito[parole_col].empty else "N/D"

    grafici_html = ""

    if format_col:
        conteggi = df_unito[format_col].value_counts()
        fig, ax = plt.subplots(figsize=(8, 5))
        conteggi.plot(kind="bar", color="darkred", ax=ax)
        ax.set_title("Distribuzione dei Format nel Corpus")
        ax.set_xlabel("Format")
        ax.set_ylabel("Numero di Script")
        plt.xticks(rotation=0)
        fig.tight_layout()
        fig.savefig(GRAFICO_FORMAT, dpi=150)
        plt.close()
        grafici_html += f'<div class="chart-block"><h2>Analisi Qualitativa: Distribuzione dei Format</h2><img src="{GRAFICO_FORMAT}" alt="Grafico distribuzione format"></div>'

    if gulpease_col and format_col:
        fig, ax = plt.subplots(figsize=(8, 5))
        df_unito.groupby(format_col)[gulpease_col].mean().plot(kind="bar", color="steelblue", ax=ax)
        ax.set_title(f"Media di '{gulpease_col}' per Format")
        ax.set_xlabel("Format")
        ax.set_ylabel("Valore Medio")
        plt.xticks(rotation=0)
        fig.tight_layout()
        fig.savefig(GRAFICO_GULPEASE, dpi=150)
        plt.close()
        grafici_html += f'<div class="chart-block"><h2>Analisi Stilometrica: Indice Gulpease</h2><img src="{GRAFICO_GULPEASE}" alt="Grafico Gulpease"></div>'

    if ttr_col and format_col:
        fig, ax = plt.subplots(figsize=(8, 5))
        df_unito.groupby(format_col)[ttr_col].mean().plot(kind="bar", color="forestgreen", ax=ax)
        ax.set_title(f"Media di '{ttr_col}' per Format (Ricchezza Lessicale)")
        ax.set_xlabel("Format")
        ax.set_ylabel("Valore Medio TTR")
        plt.xticks(rotation=0)
        fig.tight_layout()
        fig.savefig(GRAFICO_TTR, dpi=150)
        plt.close()
        grafici_html += f'<div class="chart-block"><h2>Analisi Stilometrica: Type-Token Ratio (TTR)</h2><img src="{GRAFICO_TTR}" alt="Grafico TTR"></div>'

    if parole_col and format_col:
        fig, ax = plt.subplots(figsize=(8, 5))
        df_unito.groupby(format_col)[parole_col].mean().plot(kind="bar", color="darkorange", ax=ax)
        ax.set_title(f"Media di '{parole_col}' per Format")
        ax.set_xlabel("Format")
        ax.set_ylabel("Valore Medio")
        plt.xticks(rotation=0)
        fig.tight_layout()
        fig.savefig(GRAFICO_PAROLE, dpi=150)
        plt.close()
        grafici_html += f'<div class="chart-block"><h2>Analisi Quantitativa: Lunghezza / N. Parole</h2><img src="{GRAFICO_PAROLE}" alt="Grafico Parole"></div>'

    colonne_tabella = [col for col in df_unito.columns if col]
    schede_html = ""
    
    for idx, row in df_unito.iterrows():
        id_script = row.get("ID Script", row.get("Nome File", f"Script {idx+1}"))
        schede_html += f'<div class="script-card" data-search-text="{" ".join([str(row.get(c, "")) for c in colonne_tabella]).lower()}">\n'
        schede_html += f'<h3>Scheda Analisi: {id_script}</h3>\n'
        schede_html += '<div class="card-grid">\n'
        for col in colonne_tabella:
            val = row.get(col, 'N/D')
            schede_html += f'<div class="card-item"><strong>{col}:</strong> <span>{val}</span></div>\n'
        schede_html += '</div>\n</div>\n'

    html_template = """<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="utf-8">
    <title>Report Finale Integrato - Podcast Le Troiane</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 1250px; margin: 2em auto; padding: 0 1em; line-height: 1.6; color: #333; }}
        h1 {{ color: #8B0000; border-bottom: 2px solid #8B0000; padding-bottom: 0.3em; }}
        h2 {{ color: #555; margin-top: 2em; border-bottom: 1px solid #ddd; padding-bottom: 0.3em; }}
        img {{ max-width: 100%; border: 1px solid #ccc; margin: 1em 0; display: block; }}
        
        .kpi-container {{ display: flex; gap: 1em; margin: 1.5em 0; flex-wrap: wrap; }}
        .kpi-card {{ background: #fdfaf6; border: 1px solid #e3dcd2; border-left: 4px solid #8B0000; padding: 1em; flex: 1; min-width: 200px; border-radius: 4px; }}
        .kpi-value {{ font-size: 1.5em; font-weight: bold; color: #8B0000; margin-top: 0.2em; }}
        .kpi-label {{ font-size: 0.85em; color: #666; text-transform: uppercase; letter-spacing: 0.5px; }}

        .commentary {{ background: #f4f6f8; border-left: 4px solid #4a6fa5; padding: 1.2em; margin: 1.5em 0; border-radius: 4px; }}
        
        .search-container {{ margin: 1.5em 0 1em 0; }}
        .search-input {{ width: 100%; max-width: 400px; padding: 0.6em 1em; font-size: 0.9em; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; }}

        .script-card {{ background: #fff; border: 1px solid #dcd6cd; border-left: 5px solid #8B0000; border-radius: 6px; padding: 1.2em; margin-bottom: 1.5em; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }}
        .script-card h3 {{ margin-top: 0; color: #8B0000; font-size: 1.1em; border-bottom: 1px solid #eee; padding-bottom: 0.5em; }}
        .card-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 0.8em; margin-top: 0.8em; }}
        .card-item {{ font-size: 0.85em; background: #faf8f5; padding: 0.5em 0.8em; border-radius: 4px; border: 1px solid #f0eae1; }}
        .card-item strong {{ color: #444; display: inline-block; margin-right: 0.4em; }}
        .card-item span {{ color: #222; }}

        .intro {{ background: #fdfaf6; padding: 1em; border-left: 4px solid #8B0000; margin-bottom: 1.5em; }}

        @media print {{
            body {{ max-width: 100%; margin: 0; padding: 0; }}
            .search-container {{ display: none; }}
            .chart-block {{ page-break-inside: avoid; }}
            .script-card {{ page-break-inside: avoid; box-shadow: none; border: 1px solid #aaa; }}
        }}
    </style>
</head>
<body>
    <h1>Report Finale Integrato: Podcast "Le Troiane"</h1>
    
    <div class="intro">
        <p><strong>Panoramica del progetto:</strong> Dossier di sintesi metodologica che integra l'intera gamma di analisi stilometriche, quantitative e qualitative condotta sui {tot_script} script di podcast ispirati a <em>Le Troiane</em> di Euripide.</p>
    </div>

    <div class="kpi-container">
        <div class="kpi-card">
            <div class="kpi-label">Script Totali Analizzati</div>
            <div class="kpi-value">{tot_script}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Format Predominante</div>
            <div class="kpi-value">{format_frequente}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Media Indice Gulpease</div>
            <div class="kpi-value">{media_gulpease}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Media Parole per Script</div>
            <div class="kpi-value">{media_parole}</div>
        </div>
    </div>

    <div class="commentary">
        <h3 style="margin-top:0; color:#2c3e50;">Discussione e Sintesi dei Risultati</h3>
        <p>L'analisi combinata del corpus evidenzia una chiara correlazione tra le scelte stilistiche strutturali e la tipologia di format adottata. Gli script di carattere divulgativo privilegiano una maggiore accessibilità testuale e indici di leggibilità elevati per intercettare un pubblico generalista. Di contro, le varianti intimiste e di reportage mostrano una maggiore densità lessicale e variazioni strutturali orientate alla densità drammaturgica e all'impatto emotivo, confermando la versatilità della riscrittura del testo euripideo.</p>
    </div>

    {grafici_html}

    <h2>Dossier Analitico Completo per Script (Tutte le Variabili)</h2>
    
    <div class="search-container">
        <input type="text" id="searchInput" class="search-input" onkeyup="filtraSchede()" placeholder="Filtra per ID, Format, Target o parola chiave...">
    </div>

    <div id="cardsContainer">
        {schede_html}
    </div>

    <hr>
    <p style="font-size: 0.85em; color: #777;">
        Report finale generato automaticamente in conformità con la fase di sintesi e visualizzazione dei dati (Capitoli 7 e 8).
    </p>

    <script>
    function filtraSchede() {{
        var input = document.getElementById("searchInput");
        var filter = input.value.toLowerCase();
        var container = document.getElementById("cardsContainer");
        var cards = container.getElementsByClassName("script-card");

        for (var i = 0; i < cards.length; i++) {{
            var searchText = cards[i].getAttribute("data-search-text");
            if (searchText.indexOf(filter) > -1) {{
                cards[i].style.display = "";
            }} else {{
                cards[i].style.display = "none";
            }}
        }}
    }}
    </script>
</body>
</html>
    """

    html_content = html_template.format(
        tot_script=tot_script,
        format_frequente=format_frequente,
        media_gulpease=media_gulpease,
        media_parole=media_parole,
        grafici_html=grafici_html,
        schede_html=schede_html
    )

    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"Report HTML finale completo generato con successo in: {OUTPUT_HTML}")

if __name__ == "__main__":
    main()