import os
import subprocess
import shlex
from flask import redirect
from flask_socketio import SocketIO
socketio = SocketIO()
from elpis.app import Flask

from elpis.paths import GUI_PUBLIC_DIR, CURRENT_MODEL_DIR

from elpis.kaldi.interface import KaldiInterface
from pathlib import Path


def log(content: str):
    log_path = os.path.join(CURRENT_MODEL_DIR, 'log.txt')
    with open(log_path, 'w+') as fout:
        fout.write(content)


def run_to_log(cmd: str) -> str:
    """Captures stdout/stderr and writes it to a log file, then returns the
    CompleteProcess result object"""
    args = shlex.split(cmd)
    process = subprocess.Popen(
        args,
        cwd='/kaldi-helpers',
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    while True:
        output = process.stdout.readline()
        if output == "" and process.poll() is not None:
            break
        if output:
            socketio.emit("new_log",
                          {"new_log": output.strip()},
                          namespace="/logstream")
            print(output.strip())
    log(process.stdout.decode("utf-8"))
    return process


@socketio.on('connect', namespace="/logstream")
def on_connect():
    print("Websocket connected")


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
    import elpis.api
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
    socketio = SocketIO(app)
    socketio.run(app)
