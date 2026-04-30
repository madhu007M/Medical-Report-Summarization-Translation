# 🚀 Frontend Integration - Quick Start Guide

## ✅ Setup Complete

Your frontend has been successfully integrated. Everything is tested and ready to run!

## 🚀 Start Application

### Option 1: One Click Start (Recommended)
```bash
START_PLATFORM.bat
```
- Starts backend on http://localhost:8000
- Starts frontend on http://localhost:5173
- Opens in 2 separate terminal windows

### Option 2: Start Separately
```bash
start_backend.bat       # Terminal 1
start_frontend.bat      # Terminal 2
```

### Option 3: Manual Start
```bash
# Backend terminal
cd d:\astrava
.venv\Scripts\activate.bat
uvicorn backend.app.main:app --reload --port 8000

# Frontend terminal  
cd d:\astrava\frontend-vite
npm run dev
```

## 📍 Access Points

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost:5173 | Main UI application |
| Backend | http://localhost:8000 | API server |
| API Docs | http://localhost:8000/docs | Interactive API documentation |

## 📁 Important Files

```
d:\astrava\
├── INTEGRATION_COMPLETE.md      ← Full integration details
├── FRONTEND_SETUP.md            ← Comprehensive frontend docs
├── START_PLATFORM.bat           ← Main startup script
├── start_backend.bat            ← Backend only
├── start_frontend.bat           ← Frontend only
├── TEST_COMPLETE_SETUP.bat     ← Verify setup
└── frontend-vite/               ← Your new frontend
    ├── src/                     ← Source code
    ├── package.json             ← Dependencies
    ├── .env                     ← Configuration
    └── vite.config.ts           ← Vite settings
```

## ⚙️ Configuration

The frontend is pre-configured to work with your backend:

**File**: `frontend-vite\.env`
```
VITE_API_URL=http://localhost:8000
```

To change the backend URL:
1. Edit `frontend-vite\.env`
2. Update `VITE_API_URL` value
3. Restart `start_frontend.bat`

## 📦 What's Included

- ✅ 75+ npm packages installed
- ✅ 40+ React components ready to use
- ✅ Full TypeScript support
- ✅ Tailwind CSS styling
- ✅ Radix UI components
- ✅ API client configured
- ✅ Build optimized for production

## 🧪 Verify Setup

Run this to verify everything is working:
```bash
TEST_COMPLETE_SETUP.bat
```

Should show:
```
✓ Python found
✓ Node.js found
✓ Virtual environment found
✓ Frontend dependencies found
✓ Backend application verified
```

## 🔧 Common Tasks

### Update Frontend
```bash
cd d:\astrava\frontend-vite
npm run build
```

### Run in Production Mode
```bash
cd d:\astrava\frontend-vite  
npm run preview
```

### Check for Code Issues
```bash
cd d:\astrava\frontend-vite
npm run lint
```

### Reinstall Dependencies
```bash
cd d:\astrava\frontend-vite
rm -r node_modules package-lock.json
npm install
```

## 🚨 Troubleshooting

### Frontend shows blank page
- Check browser DevTools (F12) for errors
- Ensure backend is running on port 8000
- Check `frontend-vite\.env` VITE_API_URL

### Port already in use
- Port 8000: A backend is already running
- Port 5173: Another Vite dev server is running
- Kill the process: `netstat -ano | findstr :PORT`

### Dependencies not installing
```bash
cd d:\astrava\frontend-vite
npm cache clean --force
npm install
```

### Changes not showing up
- Ensure Vite dev server is running
- Try hard refresh (Ctrl+F5)
- Check browser console for errors

## 📚 Documentation

- **Frontend Guide**: [FRONTEND_SETUP.md](FRONTEND_SETUP.md)
- **Full Integration**: [INTEGRATION_COMPLETE.md](INTEGRATION_COMPLETE.md)
- **Backend API**: http://localhost:8000/docs (when running)

## 🎯 Next Steps

1. **Start the platform**: `START_PLATFORM.bat`
2. **Open frontend**: Go to http://localhost:5173
3. **Test features**: Upload reports, chat, view dashboard
4. **Customize**: Edit components in `frontend-vite/src/`

## 💡 Tips

- Use `npm run dev` directly in terminal for faster development
- Vite provides instant hot reload during development
- Production build available with `npm run build`
- TypeScript provides IDE autocomplete and error checking

## ✨ You're All Set!

Everything is installed, configured, and verified.

**Run: START_PLATFORM.bat**

---
Integration Date: March 22, 2026
Status: ✅ Complete and Verified
