# 📊 PHƯƠNG PHÁP TÍNH ĐIỂM CV ↔ JD ALIGNMENT SCORE

Tài liệu giải thích cách tính toán điểm số tương thích giữa CV của ứng viên và Mô tả công việc (JD).

---

## 1. Nguyên Tắc Cốt Lõi

1. **Minh bạch, không giả tạo độ chính xác (No Fake Precision):**
   - Điểm số được làm tròn đến số nguyên (0–100).
   - Hệ thống không tuyên bố các số liệu vô căn cứ như *"Bạn có 93.42% cơ hội trúng tuyển"*.
2. **Đo lường mức độ tương thích (Alignment), không đánh giá năng lực con người:**
   - Điểm số phản ánh mức độ phù hợp giữa nội dung viết trong CV và các yêu cầu cụ thể của JD mục tiêu.
3. **Evidence-based:**
   - Điểm chỉ tăng khi có bằng chứng thực tế được tìm thấy trong CV gốc.

---

## 2. Bảng Trọng Số Đánh Giá (6 Chiều)

| Chiều đánh giá | Trọng số | Mô tả & Cách tính |
|---|---|---|
| **Kỹ năng kỹ thuật (Technical Skills)** | **30%** | So khớp các kỹ năng bắt buộc (trọng số x3) và kỹ năng ưu tiên (trọng số x1). |
| **Kinh nghiệm thực tế (Experience Relevance)** | **25%** | Mức độ liên quan của các dự án thực tế và quá trình làm việc với vị trí ứng tuyển. |
| **Trách nhiệm công việc (Responsibilities)** | **20%** | Khả năng đáp ứng các đầu việc cốt lõi được mô tả trong JD. |
| **Phủ từ khóa (Keyword Coverage)** | **10%** | Tỷ lệ xuất hiện của các từ khóa kỹ thuật và biệt danh/từ đồng nghĩa (aliases). |
| **Trình độ học vấn (Education Alignment)** | **10%** | Mức độ phù hợp của chuyên ngành (CNTT, Điện tử, Viễn thông...) và bậc học. |
| **Độ rõ ràng & Bố cục (CV Clarity)** | **5%** | Cấu trúc mạch lạc, thông tin liên lạc đầy đủ, mục tiêu nghề nghiệp rõ ràng. |

---

## 3. Công Thức Chi Tiết

### 3.1 Kỹ năng kỹ thuật (30%)

Mỗi yêu cầu trong JD được gán điểm cơ sở:
- **Strong Match:** 1.0 (Có bằng chứng trực tiếp, thực hành rõ ràng)
- **Partial Match:** 0.6 (Có kỹ năng tương tự hoặc liên quan)
- **Weak Evidence:** 0.3 (Đề cập mờ nhạt hoặc công nghệ phụ trợ)
- **Missing / Unknown:** 0.0 (Không tìm thấy bằng chứng)

Trọng số yêu cầu:
- **Bắt buộc (Required):** Hệ số 3.0
- **Ưu tiên (Preferred):** Hệ số 1.0

$$\text{Technical Score} = \frac{\sum (\text{Điểm cơ sở} \times \text{Hệ số})}{\sum \text{Hệ số}} \times 100$$

### 3.2 Phủ từ khóa (Keyword Coverage - 10%)

Kiểm tra sự xuất hiện của danh sách từ khóa trong JD đối chiếu với nội dung toàn văn của CV (hỗ trợ các biến thể ký hiệu như C++, C#, .NET và bảng từ đồng nghĩa SKILL_ALIASES).

$$\text{Keyword Score} = \frac{\text{Số từ khóa xuất hiện}}{\text{Tổng số từ khóa trong JD}} \times 100$$

### 3.3 Điểm tổng thể (Overall Alignment Score)

$$\text{Overall} = \text{round}(0.30 \cdot \text{Tech} + 0.25 \cdot \text{Exp} + 0.20 \cdot \text{Resp} + 0.10 \cdot \text{Kw} + 0.10 \cdot \text{Edu} + 0.05 \cdot \text{Clarity})$$
