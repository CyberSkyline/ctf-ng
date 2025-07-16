from CTFd.models import db

from ....core import NotFoundError, ValidationError
from ....team.models.Team import Team
from ....event.models.Demographic import Demographic
from ...models.Event import Event
from ....user.models.User import User

def join_event_controller(event: Event, user : User, invite_code : str = "", team_name : str = "") -> Team:
    """Main controller for the event joining process.
    """
    if (not invite_code) and (not team_name):
        raise ValidationError("Either invite_code or team_name must be provided")

    Event.check_eligibility(event, user)
    
    try:
        Demographic.create_demographic(user_id=user.id, event_id=event.id, commit=False)
        if invite_code:
            team = Team.find_by_invite_code(invite_code)
            if not team:
                raise NotFoundError(f"Team with invite code {invite_code} not found")
            
            team.add_member(user.id, commit=False)
        else:
            team = Team.create_team_with_captain(
                name=team_name,
                event_id=event.id,
                captain_id=user.id,
                ranked=True,
                commit=False,
            )
        db.session.commit()
        return team
    except Exception as e:
        print(e)
        db.session.rollback()
        raise e
