from handlers.interface import IHandler

class ApiController:
    def __init__(self):
        self.handlers = []
        self.set_base_path("")
    def set_base_path(self, base_path: str):
        self.base_path = base_path
    def add_handler(self, handler: IHandler):
        self.handlers.append(handler)
    def set_input(self,params: dict):
        self.validate_params(params)
        self.params = params
    def set_path(self, path: str):
        self.path = path[len(self.base_path):]
    def validate_params(self,params: dict):
        handler = self.get_handler()
        assert handler.validate_params(params), f"Invalid params for: {self.path}"
    def get_handler(self):
        for handler in self.handlers:
            if handler.is_current_path(self.path):
                return handler
        raise ValueError(f"No endpoint defined for: {self.path}")
    def process(self,):
        handler = self.get_handler()
        print("handler", handler)
        print("params", self.params)
        return handler.call_handler(self.params.get("payload"))

