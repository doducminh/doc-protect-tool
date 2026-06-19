# -*- coding: utf-8 -*-
"""doc-protect-tool — Chuyển 1 PDF (có text) -> PDF CHỐNG SAO CHÉP / AI:
watermark -> rasterize thuần ảnh (DPI cấu hình) -> chèn lại URI link annotation -> mã hoá AES-256.
Bảo vệ trung thực: KHÔNG hidden-text/poisoning/metadata giả. Link vẫn clickable (annotation đè ảnh).

Dùng:  python make_pdf.py <input_text.pdf> <output_final.pdf> [title] [author]
Cấu hình: .env cùng thư mục (WATERMARK, RASTER_DPI, JPEG_QUALITY, USER_PASSWORD, PDF_TITLE, PDF_AUTHOR, PDF_SUBJECT)
hoặc biến môi trường cùng tên. Dùng lại được cho mọi sản phẩm (OneGate, SSO, Dashboard...).
"""
import sys
import os
import secrets
import fitz
import pikepdf

_HERE = os.path.dirname(os.path.abspath(__file__))


def _load_env():
    e = {}
    p = os.path.join(_HERE, ".env")
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            for line in f:
                s = line.strip()
                if not s or s.startswith("#") or "=" not in s:
                    continue
                k, v = s.split("=", 1)
                e[k.strip()] = v.strip()
    return e


_E = _load_env()


def cfg(key, default):
    v = _E.get(key, os.environ.get(key, ""))
    return v if v != "" else default


WM = cfg("WATERMARK", "CONFIDENTIAL  —  DO NOT DISTRIBUTE")
DPI = int(cfg("RASTER_DPI", "300"))
JPEG_QUALITY = int(cfg("JPEG_QUALITY", "82"))
USER_PASSWORD = _E.get("USER_PASSWORD", os.environ.get("USER_PASSWORD", ""))


def make(inp, outp, title=None, author=None, subject=None):
    title = title or cfg("PDF_TITLE", "Technical Handover (CONFIDENTIAL)")
    author = author or cfg("PDF_AUTHOR", "PSC")
    subject = subject or cfg("PDF_SUBJECT", "Project / Source code / Operations handover")
    tmp = outp + ".tmp.pdf"
    src = fitz.open(inp)
    out = fitz.open()
    mat = fitz.Matrix(DPI / 72.0, DPI / 72.0)
    link_count = 0
    for page in src:
        rect = page.rect
        links = [l for l in page.get_links() if l.get("uri")]
        page.insert_text(fitz.Point(rect.width - 24, rect.height - 55), WM, fontname="helv", fontsize=10,
                         color=(0.55, 0.55, 0.62), rotate=90, overlay=True)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        try:
            img = pix.tobytes("jpeg", jpg_quality=JPEG_QUALITY)
        except TypeError:
            img = pix.tobytes("jpeg")
        npage = out.new_page(width=rect.width, height=rect.height)
        npage.insert_image(rect, stream=img)
        for l in links:
            npage.insert_link({"kind": fitz.LINK_URI, "from": l["from"], "uri": l["uri"]})
            link_count += 1
    out.save(tmp, deflate=True, garbage=4)
    print("image-only pages:", out.page_count, "| link annotations re-inserted:", link_count)
    out.close(); src.close()

    owner = secrets.token_urlsafe(24)
    pdf = pikepdf.open(tmp)
    pdf.docinfo["/Title"] = title
    pdf.docinfo["/Author"] = author
    pdf.docinfo["/Subject"] = subject
    perms = pikepdf.Permissions(
        accessibility=True, extract=False, modify_annotation=False, modify_assembly=False,
        modify_form=False, modify_other=False, print_lowres=True, print_highres=True)
    pdf.save(outp, encryption=pikepdf.Encryption(owner=owner, user=USER_PASSWORD, R=6, allow=perms))
    pdf.close()
    os.remove(tmp)
    print("SAVED FINAL", outp, os.path.getsize(outp), "bytes | owner pw discarded")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python make_pdf.py <in_text.pdf> <out.pdf> [title] [author]")
        sys.exit(1)
    make(sys.argv[1], sys.argv[2],
         sys.argv[3] if len(sys.argv) > 3 else None,
         sys.argv[4] if len(sys.argv) > 4 else None)
