#!/usr/bin/env python3
"""
Simplified Interview Server
Serves interview API endpoints for testing
"""

from flask import Flask, jsonify
from flask_cors import CORS
import logging

# Import interview API
from interview_api import interview_bp

# Initialize Flask app
app = Flask(__name__)

# Configure CORS
CORS(app, 
     resources={r"/api/*": {
         "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
         "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         "allow_headers": "*",
         "supports_credentials": True
     }})

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Register interview blueprint
app.register_blueprint(interview_bp)
logger.info("Interview API endpoints registered")

# Add health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'status': 'healthy',
        'message': 'Interview server is running'
    })

# List available routes
@app.route('/api/routes', methods=['GET'])
def list_routes():
    """List all available routes"""
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            'endpoint': rule.endpoint,
            'methods': list(rule.methods),
            'url': str(rule)
        })
    return jsonify({
        'success': True,
        'routes': routes
    })

if __name__ == '__main__':
    print("🚀 Starting Interview Server")
    print("=" * 50)
    print("Server running at: http://localhost:5000")
    print("Interview API endpoints are available")
    print("\nAvailable endpoints:")
    
    with app.test_request_context():
        for rule in app.url_map.iter_rules():
            if 'interview' in str(rule):
                print(f"  - {rule.methods} {rule}")
    
    print("\n✅ Server ready!")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5000, debug=True)