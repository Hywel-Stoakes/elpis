import os
from flask import redirect
from flask_socketio import SocketIO
socketio = SocketIO()
import elpis.api
from elpis.app import Flask

from elpis.paths import GUI_STATIC_DIR, GUI_PUBLIC_DIR

from elpis.kaldi.interface import KaldiInterface
from pathlib import Path


def create_app(test_config=None):
    # Setup static resources
    # create and configure the app
    # auto detect for yarn watch or yarn build
    static_dir_watch = '/js'
    static_dir_build = '/static'
    if 'js' in os.listdir(GUI_PUBLIC_DIR):
        # using yarn watch
        static_dir = static_dir_watch
    else:
        static_dir = static_dir_build

    # if os.environ.get('FLASK_ENV') == 'production':
    #     static_dir = static_dir_build
    # else:
    #     static_dir = static_dir_watch
    print('using static_dir:', static_dir)
    app = Flask(__name__,
                instance_relative_config=True,
                static_folder=GUI_PUBLIC_DIR + static_dir,
                static_url_path=static_dir)

    app.config.from_mapping(
        SECRET_KEY='dev'
    )
    interface_path = Path('/elpis/state')
    if not interface_path.exists():
        app.config['INTERFACE'] = KaldiInterface(interface_path)
    else:
        app.config['INTERFACE'] = KaldiInterface.load(interface_path)
    app.config['CURRENT_DATABUNDLE'] = None
    app.config['CURRENT_MODEL'] = None

    app.register_blueprint(elpis.api.bp)
    print(app.url_map)

    @app.route('/index.html')
    def index_file():
        """Redirects to '/' for React."""
        return redirect('/')

    @app.route('/', defaults={'path': ''})
    @app.route("/<path:path>")
    def index(path):
        print('in index with:', path)
        with open(f"{GUI_PUBLIC_DIR}/index.html", "r") as fin:
            content = fin.read()
            return content

    @app.route('/favicon.ico')
    def favicon():
        with open(f"{GUI_PUBLIC_DIR}/favicon.ico", "rb") as fin:
            return fin.read()

    return app


if __name__ == "__main__":
    app = create_app()
    socketio.run(app)
