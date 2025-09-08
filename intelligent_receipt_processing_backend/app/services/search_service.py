from typing import List, Optional
from sqlalchemy import or_
from ..models import db, Document, DocumentVersion


class SearchService:
    """
    DB search over title, category, tags, and OCR text from latest version.
    """

    # PUBLIC_INTERFACE
    def search_documents(self, user_id: int, query: Optional[str] = None, category: Optional[str] = None, tag: Optional[str] = None, limit: int = 25, offset: int = 0) -> List[Document]:
        """Search documents belonging to a user with optional filters.

        Parameters:
        - user_id: Owner user id to scope the search.
        - query: Full-text-like search over title, category, tags, and OCR text.
        - category: Exact match on document.category.
        - tag: Substring match against the comma-separated tags field.
        - limit: Max items to return.
        - offset: Offset for pagination.

        Returns:
        - List[Document]: Documents matching the criteria.
        """
        q = db.session.query(Document).join(DocumentVersion, isouter=True).filter(Document.created_by_id == user_id)

        if query:
            pattern = f"%{query.lower()}%"
            q = q.filter(or_(Document.title.ilike(pattern),
                             Document.category.ilike(pattern),
                             Document.tags.ilike(pattern),
                             DocumentVersion.ocr_text.ilike(pattern)))

        if category:
            q = q.filter(Document.category == category)

        if tag:
            q = q.filter(Document.tags.ilike(f"%{tag}%"))

        q = q.order_by(Document.updated_at.desc()).limit(limit).offset(offset)
        return q.all()
