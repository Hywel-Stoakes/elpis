from ..blueprint import Blueprint
from . import databundle
from . import model
from . import transcription

from pathlib import Path
from threading import Thread
import watchdog


bp = Blueprint("api", __name__, url_prefix="/api")
bp.register_blueprint(databundle.bp)
bp.register_blueprint(model.bp)
bp.register_blueprint(transcription.bp)


@bp.route("/")
def whole_state():
    # TODO: implement this if needed
    return '{"yet to be named": "the enture model!"}'


@bp.route("/log.txt")
def log():
    log_file = Path('/elpis/state/tmp_log.txt')
    if log_file.exists():
        with log_file.open() as fin:
            return fin.read()
    else:
        return "No log file."


@bp.route("/logstream")
def logstream():
    pass
    # open websocket with browser

    # start new thread, passing websocket as arg to thread (may need functools.partial)
    # can't remember if we will need to set up a thread pool for a single thread.
    # have to use a thread, not a subprocess, so we can share the websocket object
    def handle_thread(websocket):
        pass
        # send initial logfile contents
        # start watchdog.observers.polling filewatcher watching logfile for watchdog.events.FileModifiedEvent(src_path)
        # loop until websocket connection closed
        #    trigger websocket.emit(json_with_log_contents) when log changes
        # when connection closes, this function ends and thread dies

    # end function
