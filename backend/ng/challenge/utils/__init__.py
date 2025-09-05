def generate_seed(event_id: int, challenge_id: int, question_id: int, team_seed: str) -> str:
    return f"{event_id}:{challenge_id}:{question_id}:{team_seed}"