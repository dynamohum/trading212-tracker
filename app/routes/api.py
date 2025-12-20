from flask import Blueprint, jsonify, request, current_app
from app.services.trading212_service import t212_service
from app.services.returns_service import ReturnsService
import requests
import json

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/positions')
def get_positions():
    client = t212_service.get_client()
    if not client:
        return jsonify({"error": "API Key not configured"}), 500
        
    try:
        positions = client.get_all_positions()
        return jsonify({"items": positions, "mode": t212_service.mode})
    except requests.exceptions.HTTPError as e:
        status = e.response.status_code if e.response else 500
        return jsonify({"error": str(e), "status_code": status}), status
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/settings', methods=['GET', 'POST'])
def handle_settings():
    db = current_app.db_manager
    
    if request.method == 'POST':
        data = request.json
        if 'tracking' in data:
            db.set_setting('tracking_enabled', 'true' if data['tracking'] else 'false')
        if 'hidden_tickers' in data:
            if isinstance(data['hidden_tickers'], list):
                db.set_setting('hidden_tickers', json.dumps(data['hidden_tickers']))
        return jsonify({"status": "updated"})
    else:
        enabled = db.get_setting('tracking_enabled', 'false') == 'true'
        hidden_json = db.get_setting('hidden_tickers', '[]')
        try:
            hidden = json.loads(hidden_json)
        except:
            hidden = []
        return jsonify({"tracking": enabled, "hidden_tickers": hidden})

@bp.route('/returns')
def get_returns():
    service = ReturnsService(current_app.db_manager)
    return jsonify(service.calculate_returns())

@bp.route('/account/switch', methods=['POST'])
def switch_account():
    target = request.json.get('account')
    if t212_service.switch_account(target):
        return jsonify({"status": "switched", "account": t212_service.current_account})
    return jsonify({"error": "Invalid account"}), 400

@bp.route('/account/status')
def account_status():
    return jsonify(t212_service.get_account_status())
