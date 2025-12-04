from flask import Blueprint, request, jsonify
from app.models.person_profile import PersonInput
from app.services.profile_service import ProfileService
from pydantic import ValidationError

bp = Blueprint('api', __name__, url_prefix='/api/v1')
profile_service = ProfileService()

@bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "message": "LumironScraper API is running"
    }), 200

@bp.route('/search', methods=['POST'])
def search_person():
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400

        person_input = PersonInput(**data)

        force_refresh = data.get('force_refresh', False)

        result = profile_service.get_person_profile(
            person_input.first_name,
            person_input.last_name,
            person_input.company,
            force_refresh=force_refresh
        )

        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 500

    except ValidationError as e:
        return jsonify({
            "success": False,
            "error": "Validation error",
            "details": e.errors(include_url=False)
        }), 400

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "An unexpected error occurred"
        }), 500


@bp.route('/cache/stats', methods=['GET'])
def cache_stats():
    try:
        stats = profile_service.cache.get_stats()
        return jsonify({
            "success": True,
            "data": stats
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@bp.route('/cache/clear-expired', methods=['POST'])
def clear_expired_cache():
    try:
        deleted_count = profile_service.cache.clear_expired()
        return jsonify({
            "success": True,
            "message": f"Cleared {deleted_count} expired entries"
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

