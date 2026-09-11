from collections import defaultdict
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.repositories.entity_repo import EntityRepository
from app.repositories.relationship_repo import RelationshipRepository
from app.schemas.graph import GraphNode, GraphEdge, GraphResponse

class GraphService:
    def __init__(self, db: Session):
        self.db = db
        self.entity_repo = EntityRepository(db)
        self.relationship_repo = RelationshipRepository(db)

    def get_world_graph(self, world_id: str) -> GraphResponse:
        entities = self.entity_repo.list_by_world(world_id)
        relationships = self.relationship_repo.list_by_world(world_id)

        node_degrees = defaultdict(int)
        edges: List[GraphEdge] = []

        for rel in relationships:
            active_ver = self.relationship_repo.get_active_version(rel.id)
            rel_type = active_ver.relationship_type if active_ver else "RELATED_TO"
            conf = active_ver.confidence if active_ver else 1.0
            status = active_ver.status if active_ver else "ACTIVE"
            ch_id = active_ver.chapter_id if active_ver else None

            node_degrees[rel.source_entity_id] += 1
            node_degrees[rel.target_entity_id] += 1

            edges.append(GraphEdge(
                id=rel.id,
                source=rel.source_entity_id,
                target=rel.target_entity_id,
                type=rel_type,
                confidence=conf,
                status=status,
                chapter_id=ch_id
            ))

        nodes: List[GraphNode] = []
        for ent in entities:
            # Gather active facts for properties
            properties = {}
            for fact in ent.facts:
                latest_ver = fact.versions[0] if fact.versions else None
                if latest_ver and latest_ver.status == "ACTIVE":
                    properties[fact.property_name] = latest_ver.value

            nodes.append(GraphNode(
                id=ent.id,
                label=ent.canonical_name,
                type=ent.entity_type,
                properties=properties,
                degree=node_degrees[ent.id]
            ))

        return GraphResponse(nodes=nodes, edges=edges)
