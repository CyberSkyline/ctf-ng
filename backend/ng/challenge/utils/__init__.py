def generate_seed(event_id: int, challenge_id: int, question_id: int | None, team_seed: str) -> str:
    if question_id is not None:
        return f"{event_id}:{challenge_id}:{question_id}:{team_seed}"
    return f"{event_id}:{challenge_id}:{team_seed}"
