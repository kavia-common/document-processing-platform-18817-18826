from flask import jsonify


def error_response(message: str, status_code: int = 400):
    payload = {"message": message, "status": status_code}
    response = jsonify(payload)
    response.status_code = status_code
    return response
