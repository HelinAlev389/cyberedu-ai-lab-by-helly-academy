from flask import Blueprint, request, jsonify

feedback_bp = Blueprint('feedback', __name__)


@feedback_bp.route('/ai-walkthrough-feedback', methods=['POST'])
def ai_walkthrough_feedback():
    print("🔎 HEADERS:")
    print(dict(request.headers))
    print("🧾 RAW BODY:")
    print(request.data)

    try:
        data = request.get_json(force=True)
    except Exception as e:
        print("❌ JSON error:", str(e))
        return jsonify({"status": "error", "message": "Invalid JSON format"}), 400

    walkthrough_id = data.get("walkthrough_id", "unknown")
    rating = data.get("rating", None)
    comment = data.get("comment", "")

    print("📥 Feedback:")
    print(f"- walkthrough_id: {walkthrough_id}")
    print(f"- rating: {rating}")
    print(f"- comment: {comment}")

    return jsonify({
        "status": "success",
        "message": "Feedback received",
        "data": {
            "walkthrough_id": walkthrough_id,
            "rating": rating,
            "comment": comment
        }
    }), 200
