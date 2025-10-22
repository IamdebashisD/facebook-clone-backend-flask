from flask import jsonify, Response

def api_response(success: bool, message: str, data = None, status_code=200) -> Response:
    """
    Reusable function to format all API responses consistently.
    """
    return jsonify({
        "error_code": success,
        "message": message,
        "data": data 
    }), status_code
    