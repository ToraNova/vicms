from flask import abort

class BaseContent:
    def __init__(self, content_name, routes_disabled = []):
        for route in routes_disabled:
            setattr(self, route, lambda *arg : abort(404))
        self.content_name = content_name
