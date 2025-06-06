#!/usr/bin/env python3

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--port", help="Port for debug server to listen on", default=8000)
parser.add_argument(
    "--profile", help="Enable flask_profiler profiling", action="store_true"
)
parser.add_argument(
    "--disable-gevent",
    help="Disable importing gevent and monkey patching",
    action="store_false",
)
args = parser.parse_args()
if args.disable_gevent:
    print(" * Importing gevent and monkey patching. Use --disable-gevent to disable.")
    from gevent import monkey

    monkey.patch_all()

# Import not at top of file to allow gevent to monkey patch uninterrupted
from CTFd import create_app # noqa

app = create_app()

if args.profile:
    from flask_debugtoolbar import DebugToolbarExtension # noqa
    import flask_profiler # noqa

    app.config["flask_profiler"] = {
        "enabled": app.config["DEBUG"],
        "storage": {"engine": "sqlite"},
        "basicAuth": {"enabled": False},
        "ignore": ["^/themes/.*", "^/events"],
    }
    flask_profiler.init_app(app)
    app.config["DEBUG_TB_PROFILER_ENABLED"] = True
    app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False

    toolbar = DebugToolbarExtension()
    toolbar.init_app(app)
    print(f" * Flask profiling running at http://0.0.0.0:${args.port}/flask-profiler/")

app.run(debug=True, threaded=True, host="0.0.0.0", port=args.port)
