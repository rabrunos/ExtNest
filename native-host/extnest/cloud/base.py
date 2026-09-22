class CloudProvider:
    name = "base"

    def put_text(self, logical_path: str, text: str):
        raise NotImplementedError

    def get_text(self, logical_path: str):
        raise NotImplementedError

    def exists(self, logical_path: str):
        return self.get_text(logical_path) is not None
