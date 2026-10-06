# 🎯 CHIẾN LƯỢC SO KHỚP (MATCHING STRATEGY) & BẢN ĐỒ BẰNG CHỨNG

Tài liệu giải thích cơ chế so khớp ngữ nghĩa, liên kết bằng chứng và chính sách không bịa đặt.

---

## 1. Vấn Đề Của So Khớp Từ Khóa Đơn Thuần

So khớp từ khóa truyền thống (Keyword Matching) thường gặp hai lỗi phổ biến:
1. **Bỏ sót ngữ cảnh:** Ứng viên viết *"Developed Qt Widgets app with signal/slot"* nhưng JD yêu cầu *"GUI development using C++"*. Keyword search đơn thuần sẽ coi đây là trượt (Miss).
2. **Ảo tưởng khớp (False Positive):** CV chỉ có *"Attended webinar about Kubernetes"* nhưng được tính điểm ngang với kỹ sư vận hành K8s production.

---

## 2. Mô Hình So Khớp Đa Tầng (Multi-tier Matching)

```text
Yêu cầu từ JD
     │
     ├── 1. Khớp từ khóa & Biệt danh (Exact & Alias Match)
     │      (Ví dụ: C++ = Modern C++, Qt = Qt Widgets / QML)
     │
     ├── 2. Khớp ngữ nghĩa chuyên sâu (Semantic Match via LLM)
     │      Phân tích ngữ cảnh thực tế của dự án và quá trình làm việc
     │
     └── 3. Đối chiếu bằng chứng (Evidence Extraction)
            Trích xuất trực tiếp câu văn, dự án hoặc kỹ năng từ CV gốc
```

---

## 3. Phân Loại Mức Độ Khớp (Match Status)

| Trạng thái | Định nghĩa | Ví dụ JD | Bằng chứng CV |
|---|---|---|---|
| 🟢 **Strong Match** | Có bằng chứng trực tiếp, thực hành rõ ràng | *"Qt development"* | *"Dự án VTuber Control Panel sử dụng Qt Widgets & signals/slots"* |
| 🟡 **Partial Match** | Có kỹ năng liên quan nhưng chưa đủ chiều sâu | *"Linux development"* | *"Lập trình trên Raspberry Pi với Embedded Linux"* |
| 🟠 **Weak Evidence** | Bằng chứng mờ nhạt hoặc công nghệ phụ trợ | *"Linux development"* | Chỉ ghi *"Raspberry Pi"* mà không nhắc tới Linux |
| 🔴 **Missing** | Hoàn toàn không có bằng chứng trong CV | *"Docker containerization"* | Không tìm thấy bất kỳ từ khóa hay dự án nào liên quan |

---

## 4. Chính Sách "No Fabrication" (Tuyệt Đối Không Bịa Đặt)

Khi phát hiện yêu cầu thuộc trạng thái `missing`:
- Hệ thống **bắt buộc** đưa ra cảnh báo:
  > *"Không tìm thấy trong CV. Chỉ bổ sung vào CV nếu bạn thực sự có kinh nghiệm thực tế này."*
- Hệ thống **tuyệt đối không** tự ý viết vào CV kinh nghiệm, chứng chỉ, công ty hoặc chỉ số mà ứng viên không có.
