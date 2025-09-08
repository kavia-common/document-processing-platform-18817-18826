from marshmallow import Schema, fields, validate


class PaginationSchema(Schema):
    page = fields.Int(load_default=1, metadata={"description": "Page number (1-based)."})
    page_size = fields.Int(load_default=25, validate=validate.Range(min=1, max=200), metadata={"description": "Items per page."})


class UserRegisterSchema(Schema):
    email = fields.Email(required=True)
    name = fields.Str(required=False, allow_none=True)
    password = fields.Str(required=True, load_only=True)


class UserLoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)


class TokenSchema(Schema):
    access_token = fields.Str(required=True)


class DocumentUploadSchema(Schema):
    title = fields.Str(required=True)
    description = fields.Str(required=False, allow_none=True)
    tags = fields.Str(required=False, allow_none=True)


class DocumentResponseSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    filename = fields.Str()
    mime_type = fields.Str()
    extension = fields.Str()
    category = fields.Str(allow_none=True)
    tags = fields.Str(allow_none=True)
    description = fields.Str(allow_none=True)
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
    latest_version_id = fields.Int(allow_none=True)


class DocumentVersionResponseSchema(Schema):
    id = fields.Int()
    storage_path = fields.Str()
    checksum = fields.Str(allow_none=True)
    size_bytes = fields.Int(allow_none=True)
    ocr_text = fields.Str(allow_none=True)
    ocr_json = fields.Dict(allow_none=True)
    created_at = fields.DateTime()


class JobResponseSchema(Schema):
    id = fields.Int()
    document_id = fields.Int()
    version_id = fields.Int(allow_none=True)
    status = fields.Str()
    task_type = fields.Str()
    message = fields.Str(allow_none=True)
    created_at = fields.DateTime()
    started_at = fields.DateTime(allow_none=True)
    finished_at = fields.DateTime(allow_none=True)
