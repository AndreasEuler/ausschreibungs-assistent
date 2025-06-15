

from fastapi import FastAPI, Query
import openai
import os
import pymysql
from datetime import datetime
from playwright.async_api import async_playwright
import asyncio

app = FastAPI()

# OpenAI Setup
openai.api_key = os.getenv("OPENAI_API_KEY")

# DB-Verbindung
def get_db_connection():
    return pymysql.connect(
        host="mariadb106",
        user="db278740_40",
        password="Wk729:hNbjzq",
        database="db278740_40",
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )

# Scraper für Brandenburg
async def scrape_vergabemarktplatz(query: str):
    results = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://vergabemarktplatz.brandenburg.de")
        await page.fill("input[type='search']", query)
        await page.keyboard.press("Enter")
        await page.wait_for_timeout(5000)
        items = await page.query_selector_all(".search-hit-entry-title a")
        for item in items[:5]:
            title = await item.inner_text()
            item_href = await item.get_attribute("href")
            results.append((title.strip(), f"https://vergabemarktplatz.brandenburg.de{item_href}", "Beschreibung fehlt"))
        await browser.close()
    return results

@app.get("/scrape/")
async def scrape(query: str = Query(..., description="Suchbegriff zur Ausschreibung")):
    entries = await scrape_vergabemarktplatz(query)
    conn = get_db_connection()
    with conn.cursor() as cursor:
        for titel, link, beschreibung in entries:
            cursor.execute(
                "INSERT INTO ausschreibungen (titel, beschreibung, link, quelle, zeitpunkt) VALUES (%s, %s, %s, %s, %s)",
                (titel, beschreibung, link, "brandenburg", datetime.now())
            )
    conn.commit()
    conn.close()
    return {"eingetragene_eintraege": len(entries)}

@app.get("/query/")
def query(frage: str = Query(..., description="Was soll GPT aus der Datenbank filtern?")):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM ausschreibungen ORDER BY zeitpunkt DESC LIMIT 10")
        results = cursor.fetchall()
    conn.close()

    prompt = f"Hier sind die letzten 10 Ausschreibungen: {results}. Welche passen zu: '{frage}'?"
    completion = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    antwort = completion.choices[0].message["content"]
    return {"antwort": antwort}
