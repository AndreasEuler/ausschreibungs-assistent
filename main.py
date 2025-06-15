from fastapi import FastAPI, Query
import os
import openai
from openai import OpenAI

app = FastAPI()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.get("/ausschreibungen/")
def get_ausschreibungen(frage: str = Query(..., description="Worum soll es bei der Ausschreibung gehen?")):
    prompt = f"Welche öffentlichen Ausschreibungen könnten zur folgenden Beschreibung passen: {frage}?"

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        antwort = response.choices[0].message.content
        return {"antwort": antwort}
    except Exception as e:
        return {"error": str(e)}
