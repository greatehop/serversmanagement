from app import app, socketio
from tools.core import Scheduler

if __name__ == '__main__':
    # run daemon in background
    daemon = Scheduler()
    daemon.start()

    # run web app
    socketio.run(app, host='0.0.0.0', port=5000)
