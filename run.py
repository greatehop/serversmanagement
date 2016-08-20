from app import appcreator
from app import extensions as ext
from tools import core


app = appcreator.create_app()


@app.cli.command()
def run_app():
    # run daemon in background
    daemon = core.Scheduler()
    daemon.start()

    # run web app
    ext.socketio.run(app, host='0.0.0.0', port=5000)


if __name__ == '__main__':
    run_app()
