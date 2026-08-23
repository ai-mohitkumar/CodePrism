# Contributing to CodePrism 🔮

Thank you for your interest in contributing to CodePrism!

---

## 🛠️ Development Setup

### 1. Prerequisites
- **Node.js**: `v20+` & `npm`
- **Python**: `v3.12+`
- **C++ Compiler**: `g++` / `gcc`
- **Java**: `JDK 17+` (or `JDK 25`)

### 2. Install & Run
```bash
# Clone the repository
git clone https://github.com/<your-username>/CodePrism.git
cd CodePrism

# Backend setup
cd backend
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn main:app --host 127.0.0.1 --port 8080 --reload

# Frontend setup (in separate terminal)
cd ../frontend
npm install
npm run dev
```

---

## 🧪 Running Tests

Always ensure all automated tests pass before submitting a pull request:
```bash
pytest tests/ -v
cd frontend && npm run build
```

---

## 📂 Project Architecture

- **`backend/`**: FastAPI compiler engine, AST parser, Big-O inferencing, Runtime profiler, and Language Adapters.
  - `languages/`: Adapter registry for Python, C++, Java, JS/TS, C#, Rust, Go, SQL, Kotlin, Swift, Dart, PHP, Ruby, R.
  - `analysis/`: AST tree generator, Big-O complexity analyzer, Security & Quality scanners.
  - `api/`: REST routes for compile, execute, analyze, debug, projects, and mobile sync.
- **`frontend/`**: React 18 + TypeScript + Monaco Editor + Tailwind CSS + PWA.
  - `src/editor/`: Monaco Editor canvas, breakpoint gutters, and save bar.
  - `src/components/`: TopBar, Explorer, AnalysisModal, UploadModal, ProjectHistoryModal.
  - `src/pwa/`: Service worker registration and standalone install triggers.

---

## 📄 Pull Request Process

1. Fork the repo and create your feature branch: `git checkout -b feature/awesome-feature`
2. Commit your changes with clear messages: `git commit -m 'feat: add D language adapter'`
3. Push to your branch: `git push origin feature/awesome-feature`
4. Open a Pull Request on GitHub.
