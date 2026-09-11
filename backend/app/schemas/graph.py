from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class GraphNode(BaseModel):
    id: str
    label: str
    type: str
    properties: Dict[str, Any] = {}
    degree: int = 0

class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    type: str
    confidence: float = 1.0
    status: str = "ACTIVE"
    chapter_id: Optional[str] = None

class GraphResponse(BaseModel):
    nodes: List[GraphNode] = []
    edges: List[GraphEdge] = []
