from handlers import IHandler

class SimpleHandler(IHandler):
    def is_current_path(self, path: str) -> bool:
        return path == "/test"
    def validate_params(self, params: dict):
        return True
    def call_handler(self, params: dict):
        return {"message": "Hello, World!"}


