from ..models.IndvidualContainer import IndvidualContainer

def get_current_connected_challenge(current_user) -> int | None:
    user_container = IndvidualContainer.get_user_indvidual_container(current_user)
    if not user_container:
        return None

    current_challenge_id = user_container.get_current_challenge()

    return current_challenge_id
