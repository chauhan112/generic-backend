class IHandler:
    def validate_params(self, params):
        raise NotImplementedError("Subclasses must implement this method")
    def is_current_path(self, path) -> bool:
        raise NotImplementedError("Subclasses must implement this method")
    def get_caller(self, params: dict):
        raise NotImplementedError("Subclasses must implement this method")