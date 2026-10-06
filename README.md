# AI Job Application Copilot

Công cụ phân tích và tối ưu hóa CV theo từng vị trí công việc cụ thể, dựa trên bằng chứng thực tế — không bịa đặt.

## ✨ Tính năng chính

- **JD ↔ CV Matching**: So khớp semantic giữa Job Description và CV
- **Evidence Mapping**: Map bằng chứng từ CV cho mỗi yêu cầu JD
- **Gap Analysis**: Phân loại Strong / Partial / Weak / Missing
- **Priority System**: MUST FIX → SHOULD FIX → NICE TO HAVE
- **CV Rewriting**: Gợi ý viết lại Before/After với giải thích
- **Alignment Score**: Điểm tổng hợp minh bạch (0-100)

## 🏗️ Tech Stack

| Component | Technology |
|---|---|
| Frontend | Next.js 14 + TypeScript + Tailwind + shadcn/ui |
| Backend | Python 3.11+ + FastAPI + Pydantic v2 |
| AI | Google Gemini (swappable via LLM abstraction) |
| Doc Parsing | PyMuPDF (PDF) + python-docx (DOCX) |

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Gemini API key ([Get one here](https://aistudio.google.com/apikey))

### 1. Clone & Setup Backend

```bash
cd ai-copilot/backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env and add your GEMINI_API_KEY

# Run server
uvicorn app.main:app --reload --port 8000
```

### 2. Setup Frontend

```bash
cd ai-copilot/frontend

# Install dependencies
npm install

# Run dev server
npm run dev
```

### 3. Open in browser

```
Frontend: http://localhost:3000
Backend API: http://localhost:8000/docs
```

## 🐳 Docker (Alternative)

```bash
cd ai-copilot
docker-compose up
```

## 📁 Project Structure

```
ai-copilot/
├── frontend/          # Next.js frontend
│   └── src/
│       ├── app/       # Pages
│       ├── components/ # UI components
│       ├── lib/       # API client, types, utils
│       └── stores/    # Zustand state
├── backend/           # FastAPI backend
│   └── app/
│       ├── api/       # Endpoints & schemas
│       ├── domain/    # Data models & interfaces
│       ├── services/  # Business logic
│       ├── providers/ # LLM & document parsers
│       └── utils/     # Utilities
├── docs/              # Documentation
└── docker-compose.yml
```

## 🧪 Running Tests

```bash
cd backend
pip install -r requirements-dev.txt
pytest -v
```

## 📖 Documentation

- [Product Specification](docs/product-specification.md)
- [Technical Specification](docs/technical-specification.md)
- [Scoring Methodology](docs/scoring-methodology.md)
- [API Reference](http://localhost:8000/docs)

## 🔒 Privacy

- CV không được lưu trữ trên server
- File tạm được xóa ngay sau khi xử lý
- Không log nội dung CV hay API keys
- Stateless processing — mỗi request độc lập

## 📝 License

MIT
