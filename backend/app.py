from flask import Flask, jsonify, request
from flask_cors import CORS
from scraper.scraper import scrape_data

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'Backend is running'})

@app.route('/api/scrape', methods=['GET'])
def scrape():
    """Main scraping endpoint - returns scraped data
    
    Query params:
        q (optional): Search query to find and scrape first result
    """
    try:
        # Get search query from URL parameter (?q=search+term)
        search_query = request.args.get('q')
        data = scrape_data(search_query)
        return jsonify({'success': True, 'data': data, 'url': data.get('url')})
    except Exception as e:
        print(f"Error in scrape endpoint: {str(e)}")  # Print to console
        import traceback
        traceback.print_exc()  # Print full stack trace
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
