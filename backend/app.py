"""
Flask application with refactored architecture.
Uses service layer, proper logging, and dependency injection.
"""
from flask import Flask, jsonify, request
from flask_cors import CORS

# Initialize settings first (creates directories)
from config import settings
settings.initialize()

# Now safe to import services that use logging
from services import ScraperService
from utils import get_logger, setup_logging


# Setup application logging
app_logger = setup_logging("umascrape.app")
logger = get_logger(__name__)

# Create Flask app
app = Flask(__name__)

# Configure CORS for production
cors_origins = [settings.FRONTEND_URL] if hasattr(settings, 'FRONTEND_URL') else "*"
CORS(app, origins=cors_origins)  # Enable CORS for React frontend

# Initialize service (singleton pattern for the app lifetime)
scraper_service = ScraperService()


@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint.
    Returns server status and configuration info.
    """
    logger.debug("Health check requested")
    
    return jsonify({
        'status': 'ok',
        'message': 'Backend is running',
        'version': '2.0.0',
        'characters_loaded': scraper_service.get_character_count()
    })


@app.route('/api/scrape', methods=['GET'])
def scrape():
    """
    Main scraping endpoint - returns scraped character data.
    
    Query params:
        q (optional): Character name or search query
    
    Returns:
        JSON response with success status and data or error
    """
    try:
        # Get search query from URL parameter (?q=search+term)
        search_query = request.args.get('q')
        
        logger.info(f"Scrape request received: query='{search_query or '(default)'}'")
        
        # Use service layer to get character events
        result = scraper_service.get_character_events(search_query)
        
        # Debug logging
        if result.success and result.data:
            logger.debug(f"Events found: {len(result.data.events)}")
            logger.debug(f"Sample event: {result.data.events[0] if result.data.events else 'None'}")
        
        # Return result as JSON
        response = result.to_dict()
        status_code = 200 if result.success else 500
        
        if result.success:
            logger.info(f"Scrape successful: {len(result.data.events)} events found")
        else:
            logger.error(f"Scrape failed: {result.error}")
        
        return jsonify(response), status_code
    
    except Exception as e:
        # Catch-all for unexpected errors
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg, exc_info=True)
        
        return jsonify({
            'success': False,
            'error': error_msg
        }), 500


@app.route('/api/characters', methods=['GET'])
def list_characters():
    """
    List all available characters in the repository.
    
    Returns:
        JSON response with character list
    """
    try:
        logger.debug("Characters list requested")
        
        characters = scraper_service.character_repo.get_all()
        
        character_list = [
            {'name': char.name, 'url': char.url}
            for char in characters
        ]
        
        return jsonify({
            'success': True,
            'count': len(character_list),
            'characters': character_list
        })
    
    except Exception as e:
        error_msg = f"Failed to list characters: {str(e)}"
        logger.error(error_msg, exc_info=True)
        
        return jsonify({
            'success': False,
            'error': error_msg
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    logger.warning(f"404 error: {request.url}")
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"500 error: {str(error)}", exc_info=True)
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500


if __name__ == '__main__':
    # Log startup information
    logger.info("=" * 60)
    logger.info("UmaScrape Backend Starting")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"Port: {settings.PORT}")
    logger.info(f"Characters loaded: {scraper_service.get_character_count()}")
    logger.info("=" * 60)
    
    logger.info(f"Starting Flask server on {settings.HOST}:{settings.PORT}")
    app.run(
        debug=settings.DEBUG,
        host=settings.HOST,
        port=settings.PORT
    )
