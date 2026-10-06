# 🔌 TÀI LIỆU API (API REFERENCE) — AI Job Application Copilot

API Backend chạy trên FastAPI, cổng mặc định `http://localhost:8000`.

---

## 1. Endpoints

### 1.1 `GET /api/v1/health`
Kiểm tra trạng thái hoạt động của hệ thống.

**Response:**
```json
{
  "status": "ok",
  "version": "1.0.0",
  "environment": "development"
}
```

---

### 1.2 `POST /api/v1/analyze`
Phân tích toàn diện CV đối chiếu với Job Description.

**Content-Type:** `multipart/form-data`

**Parameters:**
- `jd_file` *(tùy chọn)*: Tệp JD định dạng `.pdf`, `.docx`, hoặc `.txt` (tối đa 10MB).
- `cv_file` *(tùy chọn)*: Tệp CV định dạng `.pdf`, `.docx`, hoặc `.txt` (tối đa 10MB).
- `jd_text` *(tùy chọn)*: Văn bản thuần của JD (tối đa 50,000 ký tự).
- `cv_text` *(tùy chọn)*: Văn bản thuần của CV (tối đa 50,000 ký tự).

*(Lưu ý: Bắt buộc phải cung cấp ít nhất một nguồn cho JD và một nguồn cho CV).*

**Phản hồi thành công (200 OK):**
```json
{
  "structured_jd": { ... },
  "structured_cv": { ... },
  "matches": [
    {
      "requirement": "Qt",
      "requirement_importance": "required",
      "status": "strong_match",
      "evidence": [
        {
          "source_section": "projects",
          "source_text": "VTuber Avatar Control Panel - Qt Widgets",
          "relevance_score": 0.95,
          "explanation": "Ứng viên đã sử dụng Qt Widgets và signals/slots"
        }
      ],
      "recommendation": "Đưa dự án này lên đầu danh sách và nhấn mạnh signal/slot",
      "priority": "already_strong",
      "confidence": 0.95
    }
  ],
  "alignment_score": {
    "overall": 84,
    "technical_skills": 91,
    "experience_relevance": 86,
    "responsibilities_alignment": 82,
    "keyword_coverage": 78,
    "education_alignment": 95,
    "cv_clarity": 83,
    "methodology_notes": "..."
  },
  "top_recommendations": [ ... ],
  "suggestions": [
    {
      "section": "Projects",
      "original_text": "Developed an application using C++ and Qt.",
      "suggested_text": "Developed a C++/Qt Widgets application for controlling VTuber avatar states, implementing interactive UI controls and signal/slot communication.",
      "change_description": "Thêm Qt Widgets và signal/slot",
      "reason": "JD yêu cầu Qt application development",
      "jd_requirement": "Qt",
      "evidence": "VTuber project",
      "priority": "must_fix",
      "accepted": null
    }
  ],
  "strong_count": 12,
  "partial_count": 4,
  "weak_count": 2,
  "missing_count": 3,
  "analyzed_at": "2026-10-06T20:00:00",
  "processing_time_seconds": 12.4
}
```

---

### 1.3 `POST /api/v1/report/markdown`
Chuyển đổi kết quả phân tích thành báo cáo Markdown hoàn chỉnh để tải về hoặc in ấn.
