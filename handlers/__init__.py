MSG_NOT_IMPLEMENTED = "Subclasses must implement this method"
class IHandler:
    def validate_params(self, params):
        raise NotImplementedError(MSG_NOT_IMPLEMENTED)
    def is_current_path(self, path) -> bool:
        raise NotImplementedError(MSG_NOT_IMPLEMENTED)
    def get_caller(self, params: dict):
        raise NotImplementedError(MSG_NOT_IMPLEMENTED)
    def generate_help(self):
        raise NotImplementedError(MSG_NOT_IMPLEMENTED)

class HandlerWrapper(IHandler):
    def __init__(self):
        self.handlers = []
        self.path = None
        self.current_handler = None
    def is_current_path(self, path: str) -> bool:
        self.path = path
        for handler in self.handlers:
            if handler.is_current_path(path):
                self.current_handler = handler
                return True
        return False
    def validate_params(self, params: dict):
        return self.current_handler.validate_params(params)
    def call_handler(self, params: dict):
        return self.current_handler.call_handler(params)
    def add_handler(self, handler: IHandler):
        self.handlers.append(handler)
    def generate_help(self):
        return self.current_handler.generate_help()
