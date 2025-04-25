def generate_small_pdf(path="tiny_test.pdf"):
    content = (
        b"%PDF-1.1\n"
        b"1 0 obj\n"
        b"<< /Type /Catalog /Pages 2 0 R >>\n"
        b"endobj\n"
        b"2 0 obj\n"
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>\n"
        b"endobj\n"
        b"3 0 obj\n"
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 300 144] /Contents 4 0 R /Resources << >> >>\n"
        b"endobj\n"
        b"4 0 obj\n"
        b"<< /Length 44 >>\n"
        b"stream\n"
        b"BT /F1 24 Tf 100 100 Td (Hello, PDF!) Tj ET\n"
        b"endstream\n"
        b"endobj\n"
        b"xref\n"
        b"0 5\n"
        b"0000000000 65535 f \n"
        b"0000000010 00000 n \n"
        b"0000000060 00000 n \n"
        b"0000000117 00000 n \n"
        b"0000000222 00000 n \n"
        b"trailer\n"
        b"<< /Root 1 0 R /Size 5 >>\n"
        b"startxref\n"
        b"290\n"
        b"%%EOF\n"
    )

    with open(path, "wb") as f:
        f.write(content)
    print(f"✅ Tiny PDF generated at: {path}")

generate_small_pdf("hello.pdf")
