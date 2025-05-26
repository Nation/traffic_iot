from flask import Flask, render_template, request, jsonify
from datetime import datetime
import logging
import os

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global state tracking
current_state = {
    'light': 'OFF',  # R, Y, G, or OFF
    'timestamp': datetime.now().isoformat(),
    'source': 'system',  # 'esp8266' or 'web' or 'system'
    'esp8266_last_seen': None  # Track when ESP8266 last connected
}

# State history (keep last 100 entries)
state_history = []
MAX_HISTORY = 100

def add_to_history(state, source):
    """Add state change to history"""
    entry = {
        'light': state,
        'timestamp': datetime.now().isoformat(),
        'source': source
    }
    state_history.append(entry)
    
    # Keep only last MAX_HISTORY entries
    if len(state_history) > MAX_HISTORY:
        state_history.pop(0)
    
    logger.info(f"State changed to {state} from {source}")

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html', current_state=current_state)

@app.route('/set/<state>')
def set_light_esp(state):
    """API endpoint for ESP8266 to set light state"""
    state = state.upper()
    
    if state not in ['R', 'Y', 'G']:
        logger.warning(f"Invalid state received from ESP8266: {state}")
        return jsonify({
            'status': 'error',
            'message': f'Invalid state: {state}. Use R, Y, or G'
        }), 400
    
    # Update global state
    current_state['light'] = state
    current_state['timestamp'] = datetime.now().isoformat()
    current_state['source'] = 'esp8266'
    current_state['esp8266_last_seen'] = datetime.now().isoformat()
    
    # Add to history
    add_to_history(state, 'esp8266')
    
    logger.info(f"ESP8266 set light to: {state}")
    
    return jsonify({
        'status': 'success',
        'light': state,
        'timestamp': current_state['timestamp'],
        'message': f'Light set to {state}',
        'source': 'esp8266'
    })

@app.route('/api/set', methods=['POST'])
def set_light_web():
    """API endpoint for web interface to set light state"""
    data = request.get_json()
    
    if not data or 'state' not in data:
        return jsonify({
            'status': 'error',
            'message': 'No state provided'
        }), 400
    
    state = data['state'].upper()
    
    if state not in ['R', 'Y', 'G', 'OFF']:
        return jsonify({
            'status': 'error',
            'message': f'Invalid state: {state}. Use R, Y, G, or OFF'
        }), 400
    
    # Update global state
    current_state['light'] = state
    current_state['timestamp'] = datetime.now().isoformat()
    current_state['source'] = 'web'
    
    # Add to history
    add_to_history(state, 'web')
    
    logger.info(f"Web interface set light to: {state}")
    
    return jsonify({
        'status': 'success',
        'light': state,
        'timestamp': current_state['timestamp'],
        'message': f'Light set to {state}'
    })

@app.route('/api/status')
def get_status():
    """Get current light status - ESP8266 polls this for remote commands"""
    # Update ESP8266 last seen if this is a status check from ESP8266
    user_agent = request.headers.get('User-Agent', '')
    if 'ESP8266' in user_agent:
        current_state['esp8266_last_seen'] = datetime.now().isoformat()
    
    return jsonify(current_state)

@app.route('/api/history')
def get_history():
    """Get state change history"""
    return jsonify({
        'history': state_history[-20:],  # Return last 20 entries
        'total_entries': len(state_history)
    })

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'current_light': current_state['light']
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'status': 'error',
        'message': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({
        'status': 'error',
        'message': 'Internal server error'
    }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting Flask server on port {port}")
    logger.info(f"Debug mode: {debug_mode}")
    
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
