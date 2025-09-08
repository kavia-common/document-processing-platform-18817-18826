from typing import Optional


class CategorizationService:
    """
    Simple rule-based categorization for demonstration.
    """

    # PUBLIC_INTERFACE
    def categorize(self, title: str, ocr_text: str) -> Optional[str]:
        """Return a category label from the content/title.

        Parameters:
        - title: Document title string.
        - ocr_text: Extracted OCR text from the document.

        Returns:
        - Optional[str]: Category label (e.g., invoice, receipt, tax, legal, uncategorized).
        """
        text = f"{title} {ocr_text}".lower()
        if any(k in text for k in ["invoice", "billed", "amount due"]):
            return "invoice"
        if any(k in text for k in ["receipt", "store", "pos", "total", "cash", "change"]):
            return "receipt"
        if any(k in text for k in ["tax", "irs", "government"]):
            return "tax"
        if any(k in text for k in ["contract", "agreement", "nda"]):
            return "legal"
        return "uncategorized"
