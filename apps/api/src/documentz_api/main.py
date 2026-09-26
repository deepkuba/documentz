"""Executable ASGI application."""

from documentz_api.app import create_app
from documentz_api.settings import load_api_settings

app = create_app(settings=load_api_settings())
