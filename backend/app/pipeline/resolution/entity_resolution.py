import re
from typing import List, Dict, Any, Optional

def normalize_name(name: str) -> str:
    """Standardizes a name for comparison (lowercased, punctuation stripped)."""
    if not name:
        return ""
    name = re.sub(r'^(the|a|an)\s+', '', name.strip(), flags=re.IGNORECASE)
    name = re.sub(r'[^a-zA-Z0-9\s]', '', name)
    return " ".join(name.lower().split())


def token_similarity(name1: str, name2: str) -> float:
    """Calculates Jaccard similarity over word tokens."""
    tokens1 = set(normalize_name(name1).split())
    tokens2 = set(normalize_name(name2).split())
    if not tokens1 or not tokens2:
        return 0.0
    intersection = tokens1.intersection(tokens2)
    union = tokens1.union(tokens2)
    return len(intersection) / len(union)


def string_containment(name1: str, name2: str) -> float:
    """Checks if one name is a complete substring or prefix/suffix of the other."""
    n1 = normalize_name(name1)
    n2 = normalize_name(name2)
    if not n1 or not n2:
        return 0.0
    if n1 == n2:
        return 1.0
    if n1 in n2 or n2 in n1:
        shorter = min(len(n1), len(n2))
        longer = max(len(n1), len(n2))
        return shorter / longer
    return 0.0


def calculate_match_confidence(mention: str, candidate_canonical: str, candidate_aliases: List[str] = []) -> float:
    """Computes overall confidence score between a mention and a candidate entity."""
    norm_mention = normalize_name(mention)
    norm_canonical = normalize_name(candidate_canonical)

    if norm_mention == norm_canonical:
        return 1.0

    # Check aliases
    for alias in candidate_aliases:
        norm_alias = normalize_name(alias)
        if norm_mention == norm_alias:
            return 0.98

    # Token overlap & substring check
    tok_score = token_similarity(mention, candidate_canonical)
    sub_score = string_containment(mention, candidate_canonical)
    
    score = max(tok_score, sub_score)
    for alias in candidate_aliases:
        score = max(score, token_similarity(mention, alias), string_containment(mention, alias))

    return round(score, 3)


def resolve_entity(
    mention: str,
    candidates: List[Dict[str, Any]],
    threshold: float = 0.85
) -> Optional[Dict[str, Any]]:
    """
    Finds the best matching entity candidate for a given mention.
    Each candidate should have 'id', 'canonical_name', and optional 'aliases'.
    """
    best_candidate = None
    best_score = 0.0

    for candidate in candidates:
        score = calculate_match_confidence(
            mention=mention,
            candidate_canonical=candidate.get("canonical_name", ""),
            candidate_aliases=candidate.get("aliases", [])
        )
        if score > best_score:
            best_score = score
            best_candidate = candidate

    if best_score >= threshold and best_candidate:
        return {
            "entity_id": best_candidate["id"],
            "canonical_name": best_candidate["canonical_name"],
            "confidence": best_score
        }

    return None


def cluster_mentions(extracted_entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Clusters duplicate entity mentions within a single extraction batch
    and rolls up their attributes and aliases.
    """
    clusters: List[Dict[str, Any]] = []

    for ent in extracted_entities:
        canonical = ent.get("canonical_name", "").strip()
        mention = ent.get("mention", "").strip()
        ent_type = ent.get("type", "character").lower()
        attributes = ent.get("attributes", {})

        matched_cluster = None
        for cluster in clusters:
            if cluster["type"] == ent_type:
                conf = calculate_match_confidence(
                    canonical,
                    cluster["canonical_name"],
                    cluster["aliases"]
                )
                if conf >= 0.85:
                    matched_cluster = cluster
                    break

        if matched_cluster:
            if mention and mention not in matched_cluster["aliases"] and mention != matched_cluster["canonical_name"]:
                matched_cluster["aliases"].append(mention)
            if len(canonical) > len(matched_cluster["canonical_name"]):
                matched_cluster["aliases"].append(matched_cluster["canonical_name"])
                matched_cluster["canonical_name"] = canonical
            # Merge attributes
            for k, v in attributes.items():
                if k not in matched_cluster["attributes"] or not matched_cluster["attributes"][k]:
                    matched_cluster["attributes"][k] = v
        else:
            aliases = [mention] if mention and mention != canonical else []
            clusters.append({
                "canonical_name": canonical,
                "type": ent_type,
                "aliases": aliases,
                "attributes": dict(attributes)
            })

    return clusters
