def rank_candidates(candidates):
    return sorted(
        candidates,
        key=lambda x: x.get("match_score", 0),
        reverse=True
    )