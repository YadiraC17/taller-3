from flask import jsonify


def success(message, data=None, status=200, pagination=None):
    body = {"success": True, "message": message}
    if data is not None:
        body["data"] = data
    if pagination is not None:
        body["pagination"] = pagination
    return jsonify(body), status


def failure(message, status=400, errors=None):
    body = {"success": False, "message": message}
    if errors:
        body["errors"] = errors
    return jsonify(body), status