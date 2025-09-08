from typing import Tuple, Optional


class OCRService:
    """
    OCR abstraction. In production, integrate with Tesseract/AWS Textract/GCV.
    For now, returns a stub text and a basic JSON structure.
    """

    # PUBLIC_INTERFACE
    def extract_text(self, abs_path: str, mime_type: Optional[str] = None) -> Tuple[str, dict]:
        """Extract text from a file at the given absolute path.

        Parameters:
        - abs_path: Absolute filesystem path to the file to OCR.
        - mime_type: Optional mime-type hint.

        Returns:
        - tuple(text: str, json_details: dict): OCR text and metadata.
        """
        # Placeholder: actual OCR logic would read the file and process it.
        text = f"OCR processed content from: {abs_path}"
        json_details = {"engine": "stub", "confidence": 0.75, "pages": 1}
        return text, json_details
