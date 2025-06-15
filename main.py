from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import os
from openai import OpenAI
from playwright.sync_api import sync_playwright
from datetime import datetime

app = FastAPI()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.get("/ausschreibungen/")
def get_ausschreibungen(frage: str = Query(...)):
    prompt = f"Welche öffentlichen Ausschreibungen könnten zur folgenden Beschreibung passen: {frage}?"
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        antwort = response.choices[0].message.content
        return JSONResponse(content={"antwort": antwort}, media_type="application/json; charset=utf-8")
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, media_type="application/json; charset=utf-8")

@app.get("/scrape/")
def scrape_evergabe(query: str = "app entwicklung", max_results: int = 5):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto("https://www.evergabe-online.de/")
            page.wait_for_load_state("networkidle")

            # Cookie-Banner akzeptieren, wenn vorhanden
            try:
                page.click("text=Akzeptieren", timeout=3000)
            except:
                pass

            # Robusterer Selektor verwenden
            page.wait_for_selector("input[type='search']", timeout=10000)
            page.fill("input[type='search']", query)
            page.keyboard.press("Enter")
            page.wait_for_timeout(5000)

            results = page.query_selector_all("article.search-result")
            data = []
            for result in results[:max_results]:
                title_el = result.query_selector("h3 a")
                if not title_el:
                    continue
                title = title_el.inner_text()
                link = title_el.get_attribute("href")
                beschreibung = result.inner_text().split("\n")[1] if "\n" in result.inner_text() else ""
                data.append({
                    "titel": title.strip(),
                    "link": "https://www.evergabe-online.de" + link.strip(),
                    "beschreibung": beschreibung.strip(),
                    "abgerufen_am": datetime.now().isoformat()
                })

            browser.close()
            return JSONResponse(content={"ergebnisse": data}, media_type="application/json; charset=utf-8")
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, media_type="application/json; charset=utf-8")
