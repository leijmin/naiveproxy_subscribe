from flask import Flask
import os
import logging
from logging.handlers import RotatingFileHandler
from api.health import HealthAPI
from api.subscription import SubscriptionAPI


def create_app():
    app = Flask(__name__)
    
    # 配置环境
    env = os.getenv('FLASK_ENV', 'production')
    app.config['ENV'] = env
    app.config['DEBUG'] = env == 'development'
    
    # 配置日志
    if env == 'production':
        # 确保日志目录存在
        if not os.path.exists('logs'):
            os.makedirs('logs')
            
        # 配置日志处理器
        file_handler = RotatingFileHandler(
            'logs/app.log',
            maxBytes=1024 * 1024,  # 1MB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.ERROR)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.ERROR)
        app.logger.info('Subscription service startup')

    # 注册路由
    app.add_url_rule('/api', view_func=HealthAPI.as_view('health'))
    app.add_url_rule('/api/sub', view_func=SubscriptionAPI.as_view('subscription'))
    return app

app = create_app()

if __name__ == '__main__':
    env = os.getenv('FLASK_ENV', 'production')
    if env == 'development':
        app.run(host='127.0.0.1', port=int(os.getenv('PORT', 5000)), debug=True)
    else:
        app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=False) 