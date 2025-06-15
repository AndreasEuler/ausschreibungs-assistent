# Ausschreibungs-Assistent (Beispielprojekt)

Dieses Beispielprojekt zeigt, wie du mit FastAPI und der OpenAI GPT-API eine einfache Anwendung erstellen kannst, die passende Ausschreibungen vorschlägt.

## Endpunkt

`GET /ausschreibungen/?frage=Was soll entwickelt werden`

Beispiel:

`/ausschreibungen/?frage=App zur Sprachförderung für Kinder`

## Deployment

1. Repository auf GitHub hochladen
2. Bei [Render.com](https://render.com) registrieren
3. Neues Web Service anlegen und dieses Repository verknüpfen
4. OPENAI_API_KEY als Umgebungsvariable hinzufügen