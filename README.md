# CodePrism 🔮
### Universal Multi-Language Compiler & Intelligent Code Platform
#### One Shared Compiler Engine • Desktop Web IDE • Installable PWA (Android, iOS, Windows, Mac) • Local RAM Session & Device Storage • Real-Time Cloud Sync • Production Ready

[![PWA Ready](https://img.shields.io/badge/PWA-Installable_on_Android_%2B_iOS_%2B_PC-10B981?logo=pwa&logoColor=white)](https://web.dev/progressive-web-apps/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://docker.com)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/Frontend-React_18_%2B_TypeScript-61DAFB?logo=react&logoColor=black)](https://react.dev)
[![Monaco Editor](https://img.shields.io/badge/Editor-Monaco_IDE-1E1E1E?logo=visualstudiocode&logoColor=white)](https://microsoft.github.io/monaco-editor/)
[![GCC](https://img.shields.io/badge/Compiler-GCC_C%2B%2B-00599C?logo=c%2B%2B&logoColor=white)](https://gcc.gnu.org)
[![Java](https://img.shields.io/badge/JVM-Java_25-ED8B00?logo=openjdk&logoColor=white)](https://openjdk.org)
[![.NET](https://img.shields.io/badge/.NET-SDK_9-512BD4?logo=dotnet&logoColor=white)](https://dotnet.microsoft.com)

> **Code once. Compile anywhere. Understand everything.**

**CodePrism** is a universal multi-language compiler, execution, and code intelligence platform packaged as an **Installable Progressive Web App (PWA)**, **Dual Save Subsystem (RAM Session + Native Device Storage Download)**, **Cloud Versioning Snapshots**, and a **Self-Contained Containerized Production Architecture**.

---

## 🚀 1-Click Production Deployment

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/ai-mohitkumar/CodePrism)

### Option 1: Render (1-Click Cloud Deployment)
1. Go to [Render Dashboard](https://dashboard.render.com).
2. Click **New +** $\to$ **Blueprint** (or **Web Service**).
3. Connect repository **`ai-mohitkumar/CodePrism`**.
4. Render will automatically detect `render.yaml` and `Dockerfile`, build the React frontend and Python/GCC/JDK compiler engine, and deploy on free tier!
5. Your live app is immediately accessible at `https://codeprism.onrender.com`!

---

### Option 2: Docker (Single Self-Contained Container)
```bash
# Build and run the entire CodePrism platform
docker build -t codeprism .
docker run -d -p 8080:8080 --name codeprism-app codeprism
```
Visit **`http://localhost:8080`** — includes both the compiled Web IDE, PWA service worker, and the FastAPI compiler engine!

---

### Option 3: Docker Compose
```bash
docker compose up -d --build
```

---

### Option 4: Other Cloud Platforms (Railway, Fly.io, GCP Cloud Run, AWS ECS)
Point to `Dockerfile` $\to$ Set port to `${PORT}` $\to$ Automatic multi-stage container deployment with healthcheck at `/health`.

---

### Option 4: Local Development
```powershell
# 1. Start FastAPI Backend (http://127.0.0.1:8080)
.\run_backend.bat

# 2. Start PWA Web Studio (http://localhost:5173 or http://172.22.77.149:5173)
.\run_frontend.bat
```

---

## 💾 Dual Save Subsystem (RAM Session + Device Storage)

```
                    User writes code
                           ↓
             Types filename → "bubble_sort.py"
                           ↓
                      Clicks Save
                    ↙             ↘
            RAM Save               Device Save
      (In-memory buffer +     (Triggers native browser
       localStorage backup)     Blob file download)
```

- **💾 Save to Session (RAM / `localStorage`)**: Instant, zero-latency local buffer mapped to a dedicated **"Session Saves"** explorer section. Survives browser refresh!
- **📥 Download to Device**: Triggers native browser Blob file download straight to user's `Downloads/` directory (`bubble_sort.py`, `solution.cpp`, `Main.java`, etc.).
- **⌨️ `Ctrl+S` / `Cmd+S` Shortcut**: Instantly saves to RAM Session & triggers debounced cloud sync without opening browser save dialogs.
- **🏷️ Interactive Tab Renaming**: Double-click tab name to rename; auto-detects language extension (`.py` $\to$ Python, `.cpp` $\to$ C++, `.ts` $\to$ TypeScript, etc.).
- **● Unsaved Indicator**: Live dot indicator in the tab bar showing uncommitted buffer edits.

---

## ☁️ Cloud Projects & Versioning System

- **⚡ Real-Time Autosave**: Debounced background sync (`2.5s`) saving all workspace files with a live status badge (`🟢 Synced ✓` / `⏳ Saving...`).
- **📜 Git-Like Revision Snapshots**: Capture named milestone versions (`v1.0 Milestone`, `Before Refactor`) with line count and file diff tracking.
- **⏪ 1-Click Rollback / Restore**: Restore any historical snapshot instantly with automatic pre-restore safety points.
- **📦 Project ZIP Export**: 1-click download of the complete multi-file project with directory structure and `codeprism.json` metadata.
- **🔗 Shareable Portfolio Links**: Generate public share tokens (`/share/{token}`) allowing peers and recruiters to run your code and inspect Big-O analysis live in browser.
- **📂 Multi-File Starter Templates**: Instant templates across Python, C++, Java, and TypeScript.

---

## 🧪 Automated Test Suite (29 Tests Passing)

```powershell
.\backend\venv\Scripts\pytest tests/
```

**Result**: `29 passed in 8.19s` ✅
- `test_compiler_engine.py`: Native C++ GCC compilation, Java JDK 25 bytecode generation, Python bytecode disassembly.
- `test_projects_sync.py`: Project save, autosave, version snapshots, revision restore, templates, ZIP export, and portfolio sharing.
- `test_ide_backend.py`: AST parsing, line diagnostic pointers, Big-O inferencing, step debugger, AI assistant.
- `test_universal_cloud.py`: Universal adapters (Java JDK 25, C# .NET 9, TypeScript, SQL), language registry, async job queue.
- `test_upload_analyzer.py`: Single file drag & drop, multi-file ZIP archive analysis, and dependency graph generation.
