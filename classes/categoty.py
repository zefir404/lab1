from dataclasses import dataclass, asdict
from typing import Dict, Any
@dataclass
class Category:
    id: str
    name: str
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
