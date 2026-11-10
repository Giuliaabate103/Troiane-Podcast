from google import genai

# Incolla la tua chiave API
API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=API_KEY)

try:
    print("Elenco modelli disponibili per la tua chiave:")
    for m in client.models.list():
        print(m.name)
except Exception as e:
    print(f"Errore di autenticazione o connessione: {e}")