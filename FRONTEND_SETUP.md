# Frontend Integration Guide

## Overview

Your project now includes a modern **Vite + React + TypeScript** frontend that integrates seamlessly with the FastAPI backend.

## Project Structure

```
astrava/
├── backend/              # FastAPI backend (port 8000)
├── frontend-vite/        # Modern React frontend (port 5173) ← ACTIVE
├── frontend_OLD_streamlit_deprecated/   # Legacy Streamlit (archived)
├── medreport-frontend/   # Next.js frontend (alternative)
├── start_backend.bat     # Start backend server
├── start_frontend.bat    # Start frontend server (updated)
└── START_PLATFORM.bat    # Start both services
```

## Quick Start

### Option 1: Start Both Services (Recommended)
```bash
START_PLATFORM.bat
```
This will open two terminal windows:
- Backend: http://localhost:8000
- Frontend: http://localhost:5173

### Option 2: Start Services Separately
```bash
# Terminal 1: Backend
start_backend.bat

# Terminal 2: Frontend
start_frontend.bat
```

### Option 3: Manual Start
```bash
# Terminal 1: Backend
cd d:\astrava
.venv\Scripts\activate.bat
uvicorn backend.app.main:app --reload --port 8000

# Terminal 2: Frontend
cd d:\astrava\frontend-vite
npm run dev
```

## Features

✓ **Modern UI**: Built with React 19 and Tailwind CSS
✓ **Component Library**: Radix UI components with beautiful styling
✓ **TypeScript**: Full type safety
✓ **API Integration**: Axios configured for backend communication
✓ **Responsive Design**: Works on mobile, tablet, and desktop
✓ **Hot Reload**: Automatic page refresh during development

## Environment Configuration

The frontend is pre-configured to connect to the backend:

**File**: `frontend-vite\.env`
```
VITE_API_URL=http://localhost:8000
```

To change the backend URL:
1. Edit `frontend-vite\.env`
2. Set `VITE_API_URL` to your backend URL
3. Restart the development server

## Available Commands

```bash
# Development server
npm run dev         # Start Vite dev server on port 5173

# Production build
npm run build       # Create optimized build in dist/

# Preview build
npm run preview     # Test production build locally

# Linting
npm run lint        # Check code with ESLint
```

## API Integration

The frontend uses Axios with the following configuration:

- **Base URL**: `http://localhost:8000` (from VITE_API_URL)
- **Timeout**: 90 seconds
- **Content-Type**: application/json

### Key API Endpoints Used

```
POST   /extract-text              Extract text from medical reports
POST   /process-report            Analyze report and get risk assessment
POST   /chatbot                   Chat with medical AI assistant
GET    /audio/explanation         Stream audio explanation
POST   /translate                 Translate text to other languages
GET    /doctor/alerts             Get community health alerts
```

See `frontend-vite/src/lib/api.ts` for all available API functions.

## Troubleshooting

### Frontend won't connect to backend
- Ensure backend is running on port 8000
- Check `VITE_API_URL` in `.env` file
- Verify firewall allows connections

### npm dependencies issue
```bash
cd frontend-vite
rm -r node_modules package-lock.json
npm install
```

### Port already in use
- Backend (8000): `netstat -ano | findstr :8000`
- Frontend (5173): `netstat -ano | findstr :5173`

### Build errors
```bash
cd frontend-vite
npm run lint        # Check for errors
npm run build       # Try building
```

## Project Statistics

- **Components**: 40+ reusable React components
- **UI Elements**: Full Radix UI component library
- **Styling**: Tailwind CSS with animations
- **Bundle Size**: ~188KB gzipped (production)
- **Build Time**: ~8 seconds

## Next Steps

1. ✓ Frontend integrated
2. ✓ Dependencies installed
3. Test the complete platform: `START_PLATFORM.bat`
4. Review `frontend-vite/src` for component structure
5. Customize components in `frontend-vite/src/components`
6. Add new features in `frontend-vite/src/pages`

## Frontend File Structure

```
frontend-vite/
├── src/
│   ├── components/
│   │   ├── custom/          # Custom app components
│   │   ├── sections/        # Page sections
│   │   └── ui/              # Radix UI components
│   ├── pages/               # Page components
│   ├── hooks/               # Custom React hooks
│   ├── lib/
│   │   ├── api.ts           # API client
│   │   └── utils.ts         # Utilities
│   ├── types/               # TypeScript types
│   ├── App.tsx              # Main app component
│   └── main.tsx             # Entry point
├── package.json             # Dependencies
├── tsconfig.json            # TypeScript config
├── vite.config.ts           # Vite config
├── tailwind.config.js       # Tailwind CSS
└── .env                     # Environment variables
```

## Support

For issues or questions:
1. Check the logs in the terminal windows
2. Review backend API docs: http://localhost:8000/docs
3. Check browser console (F12) for frontend errors
