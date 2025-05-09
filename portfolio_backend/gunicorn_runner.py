"""Custom Gunicorn application and Uvicorn worker configuration.

This module defines a custom Gunicorn application that utilizes Uvicorn workers
with specific configurations. It includes a specialized worker class to set up
Uvicorn with optimal parameters for asynchronous handling.

Dependencies:
    - Any: Typing hint for flexible argument types.
    - BaseApplication: Base class for Gunicorn applications.
    - import_app: Utility function to import an application.
    - BaseUvicornWorker: Base class for Uvicorn workers.

Classes:
    UvicornWorker: Custom worker class that extends UvicornWorker to define
                   specific configurations.
    GunicornApplication: Custom application class to start Gunicorn with
                         Uvicorn workers.
"""

from typing import Any

from gunicorn.app.base import BaseApplication
from gunicorn.util import import_app
from uvicorn.workers import UvicornWorker as BaseUvicornWorker

try:
    import uvloop  # noqa: WPS433 (Found nested import)
except ImportError:
    uvloop = None  # type: ignore  # noqa: WPS440 (variables overlap)


class UvicornWorker(BaseUvicornWorker):
    """Configuration for uvicorn workers.

    This class is subclassing UvicornWorker and defines
    some parameters class-wide, because it's impossible,
    to pass these parameters through gunicorn.
    """

    CONFIG_KWARGS = {  # noqa: WPS115 (upper-case constant in a class)
        "loop": "uvloop" if uvloop is not None else "asyncio",
        "http": "httptools",
        "lifespan": "on",
        "factory": True,
        "proxy_headers": False,
    }


class GunicornApplication(BaseApplication):
    """Custom gunicorn application.

    This class is used to start guncicorn
    with custom uvicorn workers.
    """

    def __init__(  # noqa: WPS211 (Too many args)
        self,
        app: str,
        host: str,
        port: int,
        workers: int,
        **kwargs: Any,
    ):
        """Initialize the Gunicorn application with custom Uvicorn workers.

        This constructor sets up the Gunicorn application with the specified
        configuration options, including the binding address, number of workers,
        and the worker class to be used.

        Args:
            app (str): The Python path to the application factory.
            host (str): The host address to bind the application.
            port (int): The port number to bind the application.
            workers (int): The number of worker processes to spawn.
            **kwargs (Any): Additional keyword arguments to configure Gunicorn.
        """
        self.options = {
            "bind": f"{host}:{port}",
            "workers": workers,
            "worker_class": "portfolio_backend.gunicorn_runner.UvicornWorker",
            **kwargs,
        }
        self.app = app
        super().__init__()

    def load_config(self) -> None:
        """Load config for web server.

        This function is used to set parameters to gunicorn
        main process. It only sets parameters that
        gunicorn can handle. If you pass unknown
        parameter to it, it crashes with error.
        """
        for key, value in self.options.items():
            if key in self.cfg.settings and value is not None:
                self.cfg.set(key.lower(), value)

    def load(self) -> str:
        """Load actual application.

        Gunicorn loads application based on this
        function's returns. We return python's path to
        the app's factory.

        Returns:
            str: python path to app factory.
        """
        return import_app(self.app)
