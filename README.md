# RESTART JVA Letter Generator API

Backend-Service für die Werkschau-Demo des JVA Dashboards.

## Features
- Generiert personalisierten ersten Brief mit Reso
- FastAPI REST API
- Anthropic Claude Integration
- CORS-enabled für Browser-Zugriff

## Deployment auf Railway

### 1. Neues Railway Project erstellen
```bash
# In diesem Ordner:
railway init
```

### 2. Umgebungsvariablen setzen
In Railway Dashboard → Variables:
```
ANTHROPIC_API_KEY=dein-api-key-hier
PORT=8000
```

### 3. Deployen
```bash
railway up
```

### 4. URL kopieren
Nach dem Deployment gibt Railway dir eine URL wie:
`https://dein-service.up.railway.app`

Diese URL dann im Frontend eintragen!

## Lokales Testen

```bash
# Dependencies installieren
pip install -r requirements.txt

# API Key setzen
export ANTHROPIC_API_KEY="dein-key"

# Server starten
uvicorn main:app --reload

# Testen:
# http://localhost:8000/docs
```

## API Endpoints

### POST /generate-letter
Generiert einen personalisierten Brief.

**Request Body:**
```json
{
  "firstName": "Max",
  "lastName": "Müller", 
  "birthDate": "1990-05-15",
  "language": "Deutsch",
  "hafthaus": "Haus L",
  "haftraum": "Haftraum 102",
  "releaseDate": "2026-04-18",
  "topics": "Schreiner, verschuldet, suche WG"
}
```

**Response:**
```json
{
  "content": "Hi Max,\n\nich heiße Reso...",
  "generatedAt": "2026-01-18T15:30:00"
}
```

## Frontend Integration

Im HTML die API URL anpassen:
```javascript
const API_URL = 'https://deine-railway-url.up.railway.app';
```
