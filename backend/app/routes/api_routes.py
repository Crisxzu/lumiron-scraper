from flask import Blueprint, request, jsonify, Response, stream_with_context
from app.models.person_profile import PersonInput
from app.services.profile_service import ProfileService
from pydantic import ValidationError
import json
import time

bp = Blueprint('api', __name__, url_prefix='/api/v1')
profile_service = ProfileService()

# Global dict pour stocker les progress updates (simple in-memory, en prod utiliser Redis)
progress_store = {}

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


@bp.route('/search-stream', methods=['POST'])
def search_person_stream():
    """
    SSE endpoint pour suivre la progression du scraping en temps réel
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400

        person_input = PersonInput(**data)
        force_refresh = data.get('force_refresh', False)

        def generate():
            """Générateur SSE pour stream les updates"""
            import uuid
            job_id = str(uuid.uuid4())

            try:
                # Initialiser le progress
                yield f"data: {json.dumps({'type': 'progress', 'step': 'init', 'message': 'Initialisation...', 'percent': 0})}\n\n"
                time.sleep(0.1)

                # Vérifier le cache
                yield f"data: {json.dumps({'type': 'progress', 'step': 'cache', 'message': 'Vérification du cache...', 'percent': 5})}\n\n"
                cached_result = profile_service.cache.get(person_input.first_name, person_input.last_name, person_input.company, force_refresh=force_refresh)

                if cached_result and not force_refresh:
                    yield f"data: {json.dumps({'type': 'progress', 'step': 'cache_hit', 'message': 'Données trouvées en cache !', 'percent': 100})}\n\n"
                    yield f"data: {json.dumps({'type': 'complete', 'success': True, 'data': cached_result['profile_data'], 'cached': True, 'cache_age_seconds': cached_result['cache_age_seconds']})}\n\n"
                    return

                # Collecte de données
                yield f"data: {json.dumps({'type': 'progress', 'step': 'scraping', 'message': 'Collecte des sources web...', 'percent': 10})}\n\n"
                time.sleep(0.5)

                yield f"data: {json.dumps({'type': 'progress', 'step': 'pappers', 'message': 'Récupération données légales (Pappers)...', 'percent': 20})}\n\n"
                time.sleep(0.5)

                yield f"data: {json.dumps({'type': 'progress', 'step': 'serper', 'message': 'Recherche Google (30+ URLs)...', 'percent': 30})}\n\n"
                time.sleep(0.5)

                yield f"data: {json.dumps({'type': 'progress', 'step': 'firecrawl', 'message': 'Scraping des pages (15 scrapes, ~2min)...', 'percent': 40})}\n\n"

                # Lancer le scraping réel
                scraped_data = profile_service.scraper.scrape_person_data(
                    person_input.first_name,
                    person_input.last_name,
                    person_input.company
                )

                num_sources = len(scraped_data.get("scraped_content", []))
                yield f"data: {json.dumps({'type': 'progress', 'step': 'scraped', 'message': f'Scraping terminé ({num_sources} sources)', 'percent': 70})}\n\n"

                scraped_content_list = [
                    data for data in scraped_data["scraped_content"]
                    if data.get('success')
                ]

                if not scraped_content_list:
                    yield f"data: {json.dumps({'type': 'error', 'message': 'Aucune donnée valide trouvée'})}\n\n"
                    return

                # Analyse avec LLM
                yield f"data: {json.dumps({'type': 'progress', 'step': 'llm', 'message': 'Analyse IA en cours (GPT-4o, ~30s)...', 'percent': 80})}\n\n"

                profile_data = profile_service.llm.analyze_profile(
                    person_input.first_name,
                    person_input.last_name,
                    person_input.company,
                    scraped_content_list,
                    scraped_data.get("pappers_data"),
                    scraped_data.get("dvf_data"),
                    scraped_data.get("hatvp_data")
                )

                profile_data["sources"] = scraped_data.get("sources", [])

                # Mise en cache
                yield f"data: {json.dumps({'type': 'progress', 'step': 'caching', 'message': 'Mise en cache...', 'percent': 95})}\n\n"
                profile_service.cache.set(
                    person_input.first_name,
                    person_input.last_name,
                    person_input.company,
                    scraped_data,
                    profile_data
                )

                # Terminé
                yield f"data: {json.dumps({'type': 'complete', 'success': True, 'data': profile_data, 'cached': False})}\n\n"

            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

        return Response(
            stream_with_context(generate()),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no',
                'Connection': 'keep-alive'
            }
        )

    except ValidationError as e:
        return jsonify({
            "success": False,
            "error": "Validation error",
            "details": e.errors(include_url=False)
        }), 400

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

