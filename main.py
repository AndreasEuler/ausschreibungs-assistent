from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import os
from openai import OpenAI

app = FastAPI()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.get("/ausschreibungen/")
def get_ausschreibungen(frage: str = Query(..., description="Worum soll es bei der Ausschreibung gehen?")):
    prompt = f"Welche öffentlichen Ausschreibungen könnten zur folgenden Beschreibung passen: {frage}?"

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # oder gpt-4o, falls verfügbar
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        antwort = response.choices[0].message.content
        return JSONResponse(content={"antwort": antwort}, media_type="application/json; charset=utf-8")
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, media_type="application/json; charset=utf-8")
