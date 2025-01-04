from flask.views import MethodView
from flask import jsonify
from utils.config_reader import read_config

class HealthAPI(MethodView):
    def get(self):
        try:
            read_config()
            return jsonify({
                'status': 'healthy',
                'message': 'Service is running normally'
            })
        except Exception as e:
            return jsonify({
                'status': 'unhealthy',
                'message': str(e)
            }), 500 