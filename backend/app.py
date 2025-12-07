from flask import Flask, jsonify
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
    """Main scraping endpoint - returns scraped data"""
    try:
        data = scrape_data()
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
