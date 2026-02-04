# Backend (FastAPI)

Endpoints:
- `/prepare?url=`
- `/stream/{token}`
- `/download/{token}?quality=best|audio`

Notes:
- Uses in-memory sessions
- Not persistent across restarts
- Add Redis for production
