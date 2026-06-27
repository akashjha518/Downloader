# Backend (FastAPI)

Endpoints:
- `/prepare?url=`
- `/download/{token}?quality=best|audio`

Notes:
- Uses in-memory sessions
- Not persistent across restarts
- Add Redis for production
