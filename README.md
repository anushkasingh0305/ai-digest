# AI Digest

AI-powered content digest system with React frontend and Flask backend.

## Project Structure

```
ai_digest/
├── backend/          # Flask API server
│   ├── src/          # Source code
│   │   ├── server.py
│   │   └── services/
│   └── requirements.txt
│
└── frontend/         # React TypeScript app
    ├── public/
    ├── src/
    │   ├── components/
    │   ├── services/
    │   └── utils/
    └── package.json
```

## Setup Instructions

### Backend Setup

1. Navigate to backend directory:
   ```bash
   cd backend
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the server:
   ```bash
   python -m src.server
   ```
   
   Server runs on http://localhost:5000

### Frontend Setup

1. Navigate to frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start development server:
   ```bash
   npm start
   ```
   
   App runs on http://localhost:3000

## Default Credentials

- **Username:** admin
- **Password:** admin

## API Endpoints

- `GET /health` - Health check
- `GET /info` - System information
- `POST /api/auth/login` - User authentication
- `GET /api/config` - Get configuration
- `GET /api/digests` - List digests
- `GET /api/webhooks` - List webhooks
- `POST /api/pipeline/run` - Run pipeline

See `/api/*` for all available endpoints.

## Technologies

### Backend
- Flask (Python web framework)
- PyJWT (JWT authentication)
- Flask-CORS (Cross-origin support)

### Frontend
- React 18 with TypeScript
- Axios (HTTP client)
- CSS3 (Styling)

## Development

Both frontend and backend run independently:
- Backend: Flask development server (port 5000)
- Frontend: React development server (port 3000)
- CORS is configured to allow frontend-backend communication
