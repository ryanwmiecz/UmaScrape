# UmaScrape

A full-stack web scraping application built with Flask (backend) and React (frontend) with real-time data visualization and animations.

## Project Structure

```
UmaScrape/
├── backend/                # Flask API
│   ├── scraper/           # Scraper module
│   │   ├── __init__.py
│   │   └── scraper.py     # Main scraping logic
│   ├── app.py             # Flask application
│   ├── requirements.txt   # Python dependencies
│   └── .env.example       # Environment variables template
│
├── frontend/              # React application
│   ├── src/
│   │   ├── services/      # API service layer
│   │   │   └── api.js
│   │   ├── App.jsx        # Main component
│   │   ├── App.css
│   │   ├── index.css
│   │   └── main.jsx
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── .env.example
│
└── README.md
```

## Tech Stack

**Backend:**
- Flask - Lightweight Python web framework
- BeautifulSoup4 - Web scraping
- Flask-CORS - Cross-origin resource sharing
- Requests - HTTP library

**Frontend:**
- React 18 - UI library
- Vite - Build tool and dev server
- Axios - HTTP client
- CSS3 - Styling and animations

## Setup Instructions

### Backend Setup

1. Navigate to backend directory:
   ```powershell
   cd backend
   ```

2. Create virtual environment:
   ```powershell
   python -m venv venv
   ```

3. Activate virtual environment:
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

4. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

5. Create `.env` file (copy from `.env.example`):
   ```powershell
   copy .env.example .env
   ```

6. Run the Flask server:
   ```powershell
   python app.py
   ```
   Backend will run on `http://localhost:5000`

### Frontend Setup

1. Navigate to frontend directory:
   ```powershell
   cd frontend
   ```

2. Install dependencies:
   ```powershell
   npm install
   ```

3. Create `.env` file (copy from `.env.example`):
   ```powershell
   copy .env.example .env
   ```

4. Run the development server:
   ```powershell
   npm run dev
   ```
   Frontend will run on `http://localhost:3000`

## Development Workflow

1. **Backend (Flask):**
   - Modify scraping logic in `backend/scraper/scraper.py`
   - Add new API endpoints in `backend/app.py`
   - Flask auto-reloads on file changes (debug mode)

2. **Frontend (React):**
   - Create components in `frontend/src/components/`
   - Update API calls in `frontend/src/services/api.js`
   - Add styles in component CSS files
   - Vite provides hot module replacement

## API Endpoints

- `GET /api/health` - Health check endpoint
- `GET /api/scrape` - Fetch scraped data

## Customization Guide

### Implementing Your Scraper

1. Open `backend/scraper/scraper.py`
2. Replace the example URL with your target website
3. Implement your scraping logic using BeautifulSoup
4. Return data in a structured format (dict/list)

### Adding Animations

The project includes basic CSS animations. To add more:
- Use CSS transitions/animations in `.css` files
- Consider libraries like Framer Motion or React Spring for complex animations
- Animation classes are defined in `App.css`

## Best Practices

- **Rate Limiting:** Add delays between requests to be respectful
- **Error Handling:** Already implemented in API service layer
- **Caching:** Consider caching scraped data to reduce requests
- **Environment Variables:** Never commit `.env` files

## Deployment Considerations

**Backend:**
- Use production WSGI server (Gunicorn, waitress)
- Disable Flask debug mode
- Set proper CORS origins

**Frontend:**
- Run `npm run build` to create production build
- Update API URL in `.env` for production
- Deploy static files to CDN/hosting service

## Troubleshooting

**CORS Errors:**
- Ensure Flask-CORS is installed
- Check backend is running on port 5000

**Module Not Found:**
- Activate virtual environment for backend
- Run `pip install -r requirements.txt`
- Run `npm install` for frontend

**Connection Refused:**
- Verify both servers are running
- Check ports 3000 (frontend) and 5000 (backend)

## License

MIT
