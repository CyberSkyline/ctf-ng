
# Meta classes that add information to the entire pipeline
class Field:
    def __init__(self, name: str) -> None:
        self.name = name

class FriendlyName:
    def __init__(self, friendly_name: str) -> None:
        self.friendly_name = friendly_name

class Untyped:
    pass