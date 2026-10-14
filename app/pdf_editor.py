import fitz  # PyMuPDF


def merge_pdfs(pdf_list: list[bytes]) -> bytes:
    """複数のPDFを結合する"""
    result = fitz.open()

    for pdf_bytes in pdf_list:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        result.insert_pdf(doc)
        doc.close()

    output = result.tobytes()
    result.close()
    return output


def split_pdf(pdf_bytes: bytes, pages: str) -> bytes:
    """PDFから指定ページを抽出する"""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    result = fitz.open()

    # "1,3,5" または "1-3" に対応
    page_nums = _parse_pages(pages, len(doc))

    for num in page_nums:
        if 0 <= num < len(doc):
            result.insert_pdf(doc, from_page=num, to_page=num)

    output = result.tobytes()
    result.close()
    doc.close()
    return output


def rotate_pdf(pdf_bytes: bytes, angle: int, pages: str = "all") -> bytes:
    """PDFのページを回転する"""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    if pages == "all":
        target_pages = range(len(doc))
    else:
        target_pages = _parse_pages(pages, len(doc))

    for num in target_pages:
        if 0 <= num < len(doc):
            page = doc[num]
            page.set_rotation((page.rotation + angle) % 360)

    output = doc.tobytes()
    doc.close()
    return output


def _parse_pages(pages: str, total: int) -> list[int]:
    """'1,3,5' または '1-3' を0始まりのリストに変換"""
    result = []
    for part in pages.split(","):
        part = part.strip()
        if "-" in part:
            start, end = part.split("-")
            start = int(start.strip()) - 1
            end = int(end.strip()) - 1
            result.extend(range(start, end + 1))
        else:
            result.append(int(part) - 1)
    return result