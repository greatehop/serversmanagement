from app import appcreator
from app import extensions as ext
from tools.core import Scheduler


app = appcreator.create_app()


@app.cli.command()
def run_app():
    # run daemon in background
    daemon = Scheduler()
    daemon.start()

    # run web app
    ext.socketio.run(app, host='0.0.0.0', port=5000)


if __name__ == '__main__':
    run_app()
