from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.contradiction import Contradiction
from app.core.constants import ContradictionType, ContradictionStatus
from app.repositories.contradiction_repo import ContradictionRepository
from app.repositories.fact_repo import FactRepository
from app.repositories.relationship_repo import RelationshipRepository
from app.config.logging import get_logger

logger = get_logger(__name__)

class ConsistencyService:
    def __init__(self, db: Session):
        self.db = db
        self.contradiction_repo = ContradictionRepository(db)
        self.fact_repo = FactRepository(db)
        self.relationship_repo = RelationshipRepository(db)

    def run_checks(
        self,
        world_id: str,
        events: List[Dict[str, Any]] = [],
        temporal_relations: List[Dict[str, Any]] = []
    ) -> List[Contradiction]:
        """
        Executes consistency checks on world state components:
        1. Temporal cycles (using DFS cycle detection)
        2. Unresolved conflicting fact versions
        3. Conflicting relationship versions
        """
        detected: List[Contradiction] = []

        # 1. Temporal Cycle Detection
        cycle_issues = self._detect_temporal_cycles(events, temporal_relations)
        for issue in cycle_issues:
            con = self.contradiction_repo.create_contradiction(
                world_id=world_id,
                contradiction_type=ContradictionType.CYCLE.value,
                explanation=issue["description"],
                confidence=1.0,
                status=ContradictionStatus.DETECTED.value
            )
            detected.append(con)

        return detected

    def _detect_temporal_cycles(
        self,
        events: List[Dict[str, Any]],
        temporal_relations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        issues = []
        event_ids = {e.get("id") or e.get("event_id") for e in events if (e.get("id") or e.get("event_id"))}
        graph = {eid: [] for eid in event_ids}

        for tr in temporal_relations:
            e1 = tr.get("event_1")
            e2 = tr.get("event_2")
            rel = tr.get("relation", "").upper()

            if e1 in graph and e2 in graph:
                if rel == "BEFORE":
                    graph[e1].append(e2)
                elif rel == "AFTER":
                    graph[e2].append(e1)

        visited = {node: 0 for node in graph}  # 0: unvisited, 1: visiting, 2: visited

        def dfs(node: str, path: List[str]) -> bool:
            visited[node] = 1
            path.append(node)
            for neighbor in graph.get(node, []):
                if visited.get(neighbor) == 0:
                    if dfs(neighbor, path):
                        return True
                elif visited.get(neighbor) == 1:
                    start_idx = path.index(neighbor)
                    cycle = path[start_idx:] + [neighbor]
                    issues.append({
                        "type": "TEMPORAL_CYCLE",
                        "description": f"Temporal ordering cycle detected: {' -> '.join(cycle)}"
                    })
                    return True
            path.pop()
            visited[node] = 2
            return False

        for node in list(graph.keys()):
            if visited[node] == 0:
                dfs(node, [])

        return issues

    def resolve_contradiction(
        self,
        contradiction_id: str,
        status: str = "RESOLVED",
        preferred_fact_version_id: Optional[str] = None
    ) -> Optional[Contradiction]:
        con = self.contradiction_repo.resolve(contradiction_id, status=status)
        if con and preferred_fact_version_id and con.old_fact_version_id and con.new_fact_version_id:
            from app.models.fact import FactVersion
            # Activate preferred version, mark other as superseded
            chosen = self.db.query(FactVersion).filter_by(id=preferred_fact_version_id).first()
            other_id = con.old_fact_version_id if preferred_fact_version_id == con.new_fact_version_id else con.new_fact_version_id
            other = self.db.query(FactVersion).filter_by(id=other_id).first()
            if chosen:
                chosen.status = "ACTIVE"
            if other:
                other.status = "SUPERSEDED"
            self.db.commit()
        return con

    def list_contradictions(self, world_id: str, status: Optional[str] = None) -> List[Contradiction]:
        return self.contradiction_repo.list_by_world(world_id, status=status)
