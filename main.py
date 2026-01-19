from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from anthropic import Anthropic
import os
from datetime import datetime
from typing import Optional

app = FastAPI(title="RESTART JVA Letter Generator API")

# CORS configuration for browser access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ParticipantData(BaseModel):
    firstName: str
    lastName: str
    birthDate: str
    language: str
    hafthaus: str
    haftraum: str
    releaseDate: str
    topics: str

class LetterResponse(BaseModel):
    content: str
    generatedAt: str

@app.get("/")
async def root():
    return {
        "service": "RESTART Letter Generator API",
        "status": "online",
        "version": "1.0.0"
    }

@app.post("/generate-letter", response_model=LetterResponse)
async def generate_letter(data: ParticipantData):
    """
    Generate a personalized first letter from Reso based on participant data.
    """
    try:
        # Get API key from environment
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=500, 
                detail="API key not configured"
            )
        
        # Initialize Anthropic client
        client = Anthropic(api_key=api_key)
        
        # Calculate days until release
        release_date = datetime.strptime(data.releaseDate, "%Y-%m-%d")
        today = datetime.now()
        days_until_release = (release_date - today).days
        
        # Build the prompt for Reso
        prompt = build_reso_prompt(data, days_until_release)
        
        # Call Anthropic API with Reso's system prompt
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            system=get_reso_system_prompt(data.language),
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        # Extract letter content
        letter_content = message.content[0].text
        
        return LetterResponse(
            content=letter_content,
            generatedAt=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating letter: {str(e)}"
        )

def get_reso_system_prompt(language: str) -> str:
    """
    Returns Reso's system prompt adapted for letter writing.
    Based on your Reso v3 system prompt but focused on letter generation.
    """
    language_instruction = f"IMPORTANT: Write the entire letter in {language}. Do not mix languages."
    
    return f"""Du bist Reso, der KI-Assistent des RESTART-Programms für die digitale Reintegration von Haftentlassenen.

DEINE ROLLE:
- Du bist KEIN Sozialarbeiter, Richter oder Justizbeamter
- Du bist wie ein Navi und Notizzettel für die Zeit nach der Haft
- Du bist hilfsbereit, verständnisvoll und respektvoll
- Du kommunizierst auf Augenhöhe ohne bevormundend zu sein

KOMMUNIKATIONSSTIL:
- Verwende einfache, klare Sprache (B1-Niveau)
- Sei persönlich und freundlich, aber professionell
- Keine Emojis, kein Markdown, keine Formatierung
- Kurze Sätze, verständliche Wörter
- Ermutigend aber realistisch

BRIEF-SPEZIFISCHE REGELN:
- Dies ist Brief 1 - der Einführungsbrief
- Maximal 1 A4-Seite (ca. 400-500 Wörter)
- Struktur: Begrüßung → Vorstellung → Bezug zu Situation → Ausblick → Abschied
- Gehe KONKRET auf die genannten Themen ein
- Mache klar, dass die Briefe freiwillig sind und keinen Einfluss auf die Haft haben

{language_instruction}

WICHTIG:
- Schreibe NUR den Brief-Inhalt
- Keine Meta-Kommentare oder Erklärungen
- Beginne direkt mit "Hi [Name],"
- Ende mit "Viele Grüße" und "Reso" in separaten Zeilen"""

def build_reso_prompt(data: ParticipantData, days_until_release: int) -> str:
    """
    Builds the user prompt for Reso to generate the first letter.
    """
    return f"""Schreibe den ersten Einführungsbrief für:

NAME: {data.firstName} {data.lastName}
SPRACHE: {data.language}
ENTLASSUNG: in {days_until_release} Tagen ({data.releaseDate})
BESONDERE THEMEN/SITUATION: {data.topics}

Der Brief soll:
1. Mit "Hi {data.firstName}," beginnen
2. Dich kurz als Reso vorstellen (ca. 2-3 Sätze)
3. Klarstellen, dass die Briefe freiwillig sind und keinen Einfluss auf Haft/Auflagen haben
4. DIREKT und KONKRET auf 1-2 der genannten Themen eingehen: {data.topics}
5. Einen kurzen Ausblick auf kommende Briefe geben
6. Mit "Viele Grüße" und dann "Reso" (in neuer Zeile) enden

WICHTIG: 
- Maximal 1 A4-Seite
- Einfache, verständliche Sprache
- Persönlich und ermutigend
- Konkret auf die Situation eingehen"""

@app.get("/health")
async def health_check():
    """Health check endpoint for Railway"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
