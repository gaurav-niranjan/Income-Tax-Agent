"""Build fake raw pages that look like the PDF's printouts (header, body, footer)."""


def make_page(page_no: int, body: str, i: int = 1, n: int = 1) -> dict:
    """A raw page as extract.py stores it: header, body, footer with "Page i of n"."""
    text = (
        "\n\n           Income Tax Department\n"
        "           Ministry of Finance, Government of India\n\n"
        f"{body}\n\n\n"
        "                       Downloaded/Printed on 25/08/2026, 10:48 am from "
        f"www.incometaxindia.gov.in Page {i} of {n}"
    )
    return {"page": page_no, "text": text}
