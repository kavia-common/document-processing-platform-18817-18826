from flask import request, g
from flask_smorest import Blueprint
from ..schemas import DocumentResponseSchema
from .auth import require_auth
from ..services.search_service import SearchService

blp = Blueprint("Search", "search", url_prefix="/search", description="Search documents")


@blp.route("")
class SearchResource:
    @blp.response(200, DocumentResponseSchema(many=True))
    @require_auth
    def get(self):
        """
        Search documents with query params: q, category, tag, limit, offset.
        """
        q = request.args.get("q")
        category = request.args.get("category")
        tag = request.args.get("tag")
        limit = int(request.args.get("limit", "25"))
        offset = int(request.args.get("offset", "0"))
        results = SearchService().search_documents(
            user_id=g.current_user.id, query=q, category=category, tag=tag, limit=limit, offset=offset
        )
        return results
