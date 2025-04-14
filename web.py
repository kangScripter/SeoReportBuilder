# run.py

from core import create_app
from flask_caching import Cache
app = create_app()

if __name__ == '__main__':
    # app.config['CACHE_TYPE'] = 'SimpleCache'
    # app.config['CACHE_DEFAULT_TIMEOUT'] = 300   
    # cache = Cache(app)
    # cache.init_app(app)
    
    app.run(debug=True)
