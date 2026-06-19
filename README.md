# doc-protect-tool — Xuất PDF chống sao chép / AI (dùng chung)

Tool **độc lập**, dùng lại cho mọi sản phẩm (OneGate, SSO, Dashboard, ECitizen…). Nhận 1 PDF đã có text,
trả về PDF **ảnh thuần** (không text layer) + **watermark** + **mã hoá AES-256** (cấm copy/sửa, cho in),
**giữ link clickable** (URI annotation đè lên ảnh).

## Cài đặt
```powershell
pip install -r requirements.txt          # PyMuPDF, pikepdf
copy .env.example .env                    # rồi chỉnh cấu hình trong .env
```

## Dùng
```powershell
python make_pdf.py <in_text.pdf> <out.pdf> [title] [author]
```
- `in_text.pdf`: PDF có text (vd Word export ra).
- Cấu hình ở `.env` cùng thư mục (hoặc biến môi trường): `WATERMARK`, `RASTER_DPI`, `JPEG_QUALITY`,
  `USER_PASSWORD`, `PDF_TITLE`, `PDF_AUTHOR`, `PDF_SUBJECT`. `title`/`author` truyền qua argv sẽ ghi đè.
- `.env` **không** được commit (xem `.gitignore`); dùng `.env.example` làm mẫu.

## Yêu cầu
`pip install -r requirements.txt`. Tự tạo text-PDF từ .docx (cần Microsoft Word) là việc của tool gọi nó
(vd onegate-doc-tool/make_pdfs.ps1 convert docx→PDF rồi gọi tool này).

## Nguyên tắc
- Bảo vệ **trung thực**: KHÔNG hidden-text/poisoning/metadata giả. PDF ảnh chỉ là rào cản —
  OCR/AI nhìn ảnh vẫn đọc được; chốt chặn thật là DLP/kiểm soát truy cập.
- Quan hệ: `onegate-doc-tool` (và các *-doc-tool khác) chỉ dựng `.docx` rồi **gọi tool này** để xuất PDF.
