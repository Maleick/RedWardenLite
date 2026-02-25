from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class DecisionResult:
    allow: bool
    action: str
    reason: str
    message: str
    ipgeo: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
