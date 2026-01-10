# langs-project-backend

Flask API for voice-driven NPC game.

## Local Run

1. Install dependencies: `pip install -r requirements.txt`
2. Set env vars: `export FLASK_APP=app.py` (or `set FLASK_APP=app.py` on Windows)
3. Run: `flask run --host=0.0.0.0 --port=8080`

## API Endpoints

- GET /api/health
- GET /api/data
- POST /api/npc/command

## Example curl

```bash
curl -X POST http://localhost:8080/api/npc/command \
  -H "Content-Type: application/json" \
  -d '{
    "npc": {
      "name": "Guard",
      "personality": "gruff but loyal",
      "mood": "neutral",
      "obedience": 0.8
    },
    "transcript": "Hello, guard!"
  }'
```

## NPC Payload Example

```json
{
  "name": "Guard",
  "personality": "gruff but loyal",
  "mood": "neutral",
  "obedience": 0.8
}
```
