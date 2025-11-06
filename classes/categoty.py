from dataclasses import dataclass, asdict

@dataclass
class Category:
    id: str
    name: str
    description: str = ""

    def to_dict(self):
        return asdict(self)
