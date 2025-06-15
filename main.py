from fastapi import FastAPI, Query
import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

@app.get("/ausschreibungen/")
def get_ausschreibungen(frage: str = Query(..., description="Worum soll es bei der Ausschreibung gehen?")):
    prompt = f"Welche öffentlichen Ausschreibungen könnten zur folgenden Beschreibung passen: {frage}?"

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        antwort = response["choices"][0]["message"]["content"]
        return {"antwort": antwort}
    except Exception as e:
        return {"error": str(e)}