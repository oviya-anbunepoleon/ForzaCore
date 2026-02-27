def calculate_score(difficulty: str):
    score_map = {
        "Easy": 10,
        "Medium": 20,
        "Hard": 30
    }
    return score_map.get(difficulty, 0)