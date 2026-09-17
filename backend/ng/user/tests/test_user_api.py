"""
Tests for user admin routes & user related user routes
"""


def test_get_user_profile(logged_in_client, user):
    """
    Test getting the current user's profile
    """
    response = logged_in_client.get("/ng/users/me")

    assert response.status_code == 200
    data = response.get_json()

    assert data["success"] is True
    user_data = data["data"]
    assert user_data["id"] == user.id
    assert user_data["name"] == user.name
    assert user_data["email"] == user.email
    assert "registered_at" in user_data
    assert "roles" not in user_data


def test_get_user_events(logged_in_client, user, event_factory, team_factory):
    """
    Test getting the current user's events
    """
    event1 = event_factory(name = "User Event 1")
    event2 = event_factory(name = "User Event 2")
    team_factory(event = event1, members = [user])
    team_factory(event = event2, members = [user])

    response = logged_in_client.get("/ng/users/me/events")

    assert response.status_code == 200
    data = response.get_json()

    assert data["success"] is True
    events = data["data"]
    assert len(events) == 2
    event_names = {event["name"] for event in events}
    assert "User Event 1" in event_names
    assert "User Event 2" in event_names

    event_ids = {event["id"] for event in events}
    assert event1.id in event_ids
    assert event2.id in event_ids


def test_get_user_teams(logged_in_client, user, event_factory, team_factory):
    """
    Test getting the current user's teams
    """
    event1 = event_factory(name = "Team Event 1")
    event2 = event_factory(name = "Team Event 2")
    team_factory(event = event1, name = "Team N", members = [user])
    team_factory(event = event2, name = "Team NG", members = [user])

    response = logged_in_client.get("/ng/users/me/teams")

    assert response.status_code == 200
    data = response.get_json()

    assert data["success"] is True
    teams = data["data"]
    assert len(teams) == 2
    team_names = {team["name"] for team in teams}
    assert "Team N" in team_names
    assert "Team NG" in team_names

    for team in teams:
        assert "id" in team
        assert "name" in team
        assert "event_id" in team
        assert team["member_count"] >= 1


def test_admin_get_users(admin_client, admin):
    """
    Test getting all users as an admin
    """
    response = admin_client.get("/ng/admin/users")

    assert response.status_code == 200
    data = response.get_json()

    assert data["success"] is True
    assert data["data"]["lastRow"] >= 1
    assert admin.id in {row["id"] for row in data["data"]["rows"]}


def test_non_admin_endpoints(logged_in_client, user):
    """
    Test that non-admins cannot access the admin users endpoint
    """
    response = logged_in_client.get("/ng/admin/users")
    assert response.status_code == 403
    response = logged_in_client.get(f"/ng/admin/users/{user.id}")
    assert response.status_code == 403
    response = logged_in_client.put(f"/ng/admin/users/{user.id}", json = {})
    assert response.status_code == 403
    response = logged_in_client.delete(
        "/ng/admin/users/delete",
        json = {"user": user.id}
    )
    assert response.status_code == 403
    response = logged_in_client.get(f"/ng/admin/users/{user.id}/events")
    assert response.status_code == 403
    response = logged_in_client.get(f"/ng/admin/users/{user.id}/teams")
    assert response.status_code == 403


def test_admin_get_user_events(admin_client, user_factory, event_factory, team_factory):
    """
    Test admin getting user events with actual data
    """
    user = user_factory(name = "testuser", email = "test@example.com")
    event = event_factory(name = "Test Event")
    team_factory(event = event, members = [user])

    response = admin_client.get(f"/ng/admin/users/{user.id}/events")

    assert response.status_code == 200
    data = response.get_json()

    assert data["success"] is True
    events = data["data"]
    assert len(events) == 1
    assert events[0]["name"] == "Test Event"
    assert events[0]["id"] == event.id


def test_admin_get_user_teams(admin_client, user_factory, event_factory, team_factory):
    """
    Test admin getting user teams with actual data
    """
    user = user_factory(name = "testuser", email = "test@example.com")
    event = event_factory(name = "Test Event")
    team = team_factory(event = event, name = "Test Team", members = [user])

    response = admin_client.get(f"/ng/admin/users/{user.id}/teams")
    assert response.status_code == 200
    data = response.get_json()

    assert data["success"] is True
    teams = data["data"]
    assert len(teams) == 1
    assert teams[0]["name"] == "Test Team"
    assert teams[0]["id"] == team.id
    assert teams[0]["event_id"] == event.id


def test_admin_get_nonexistent_user(admin_client):
    """
    Test admin trying to get a user that doesn't exist
    """
    response = admin_client.get("/ng/admin/users/99999")

    assert response.status_code == 404
    data = response.get_json()

    assert data["success"] is False


def test_admin_update_nonexistent_user(admin_client):
    """
    Test admin trying to update a user that doesn't exist
    """
    response = admin_client.put("/ng/admin/users/99999", json = {"name": "Test"})

    assert response.status_code == 404
    data = response.get_json()

    assert data["success"] is False


def test_get_user(admin_client, user):
    """
    Test getting a specific user as an admin
    """
    response = admin_client.get(f"/ng/admin/users/{user.id}")

    assert response.status_code == 200
    data = response.get_json()

    assert data["success"] is True
    user_data = data["data"]
    assert user_data["id"] == user.id
    assert user_data["name"] == user.name
    assert user_data["email"] == user.email
    assert "registered_at" in user_data
    assert "roles" in user_data or "role" in user_data


def test_user_put(admin_client, user, db_session):
    """
    Test updating a user as an admin
    """
    updated_data = {"name": "Updated User", "email": "updated@example.com"}
    response = admin_client.put(f"/ng/admin/users/{user.id}", json = updated_data)

    assert response.status_code == 200
    data = response.get_json()

    assert data["success"] is True
    assert data["data"]["name"] == updated_data["name"]
    assert data["data"]["email"] == updated_data["email"]

    db_session.refresh(user)
    assert user.name == "Updated User"
    assert user.email == "updated@example.com"

    verify_response = admin_client.get(f"/ng/admin/users/{user.id}")
    verify_data = verify_response.get_json()
    assert verify_data["data"]["name"] == "Updated User"
    assert verify_data["data"]["email"] == "updated@example.com"

def test_user_put_input_validation(admin_client, user):
    """
    Test updating a user with invalid data as an admin
    """
    invalid_data = {"notvalid": "data", "name": "test", "email": "test@test.com"}
    response = admin_client.put(f"/ng/admin/users/{user.id}", json = invalid_data)

    assert response.status_code == 200
    data = response.get_json()

    assert data["success"] is True
    assert data["data"]["name"] == "test"
    assert data["data"]["email"] == "test@test.com"
    assert "notvalid" not in data["data"]

def test_delete_user(admin_client, user):
    """
    Test deleting a user as an admin
    """
    user_id = user.id
    response = admin_client.delete(
        "/ng/admin/users/delete",
        json = {"user_id": user_id}
    )

    assert response.status_code == 200
    data = response.get_json()

    assert data["success"] is True

    response = admin_client.get(f"/ng/admin/users/{user_id}")
    assert response.status_code == 404

def test_user_login(logged_in_client, user):
    """
    Test user login endpoint
    """
    preset_username = "testuser"
    preset_password = "password"


    response = logged_in_client.post(
        "/ng/users/login",
        json={"username": preset_username, "password": preset_password}
    )
    assert response.status_code == 200
    data = response.get_json()

    assert data["success"] is True
    assert "session" in logged_in_client.cookie_jar._cookies['localhost.local']['/']

def test_user_logout(logged_in_client):
    """
    Test user logout endpoint
    """
    response = logged_in_client.post("/ng/users/logout",json={})

    assert response.status_code == 200
    data = response.get_json()

    assert data["success"] is True
    assert "session" not in logged_in_client.cookie_jar._cookies['localhost.local']['/']

def test_multiple_incorrect_attempts(logged_in_client, user):
    """
    Test multiple incorrect login attempts
    """
    preset_username = "testuser"
    incorrect_password = "wrongpassword"
    correct_password = "password"

    for _ in range(5):
        response = logged_in_client.post(
            "/ng/users/login",
            json={"username": preset_username, "password": incorrect_password}
        )
        assert response.status_code == 401
        data = response.get_json()
        assert data["success"] is False
        assert "authentication" in data["errors"]

    response = logged_in_client.post(
        "/ng/users/login",
        json={"username": preset_username, "password": correct_password}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert "session" in logged_in_client.cookie_jar._cookies['localhost.local']['/']

def test_login_with_email(logged_in_client, user):
    """
    Test user login using email instead of username
    """
    preset_email = "test@example.com"
    preset_password = "password"
    response = logged_in_client.post(
        "/ng/users/login",
        json={"username": preset_email, "password": preset_password}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert "session" in logged_in_client.cookie_jar._cookies['localhost.local']['/']


def test_user_get_sponsor(client_factory, user_factory, sponsor_factory):
    """
    Test getting the current user's sponsor affiliation
    """
    sponsor = sponsor_factory(name="Test Sponsor", logo="https://www.ndow.org/wp-content/uploads/2021/10/branta_canadensis-scaled.jpeg")
    user = user_factory(name="sponsoruser", email="sponsoruser@example.com", sponsor=sponsor)
    client = client_factory(user=user)

    response = client.get("/ng/users/me/sponsor")
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["data"]["name"] == "Test Sponsor"

def test_user_get_no_sponsor(client_factory, user_factory):
    """
    Test getting the current user's sponsor affiliation when none exists
    """
    user = user_factory(name="nosponsoruser", email="nosponsoruser@example.com")
    client = client_factory(user=user)

    response = client.get("/ng/users/me/sponsor")
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["data"] is None

def test_update_user_sponsor(client_factory,user_factory, sponsor_factory):
    """
    Test updating a user's sponsor affiliation as an admin
    """
    sponsor = sponsor_factory(name="Test Sponsor", logo="https://www.ndow.org/wp-content/uploads/2021/10/branta_canadensis-scaled.jpeg")
    user = user_factory(name="updatesponsoruser", email="updatesponsoruser@example.com", sponsor=sponsor)
    sponsor = sponsor_factory(name="New Sponsor", logo="https://www.ndow.org/wp-content/uploads/2021/10/branta_canadensis-scaled.jpeg")
    client = client_factory(user=user)

    response = client.put("/ng/users/me/sponsor", json={"sponsor_id": sponsor.id})
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["data"]["name"] == "New Sponsor"

def test_update_user_sponsor_not_found(client_factory,user_factory):
    """
    Test updating a user's sponsor affiliation when the sponsor is not found
    """
    user = user_factory(name="updatesponsoruser", email="updatesponsoruser@example.com")
    client = client_factory(user=user)

    response = client.put("/ng/users/me/sponsor", json={"sponsor_id": 9999})
    assert response.status_code == 404
    data = response.get_json()
    assert data["success"] is False
    assert "sponsor" in data["errors"]

def test_update_user_sponsor_no_data(client_factory,user_factory):
    """
    Test updating a user's sponsor affiliation with no data provided
    """
    user = user_factory(name="updatesponsoruser", email="updatesponsoruser@example.com")
    client = client_factory(user=user)

    response = client.put("/ng/users/me/sponsor", json={})
    assert response.status_code == 400
    data = response.get_json()
    assert data["success"] is False
    assert "sponsor" in data["errors"]



def test_admin_create_user(admin_client):
    """
    Test creating a new user as an admin
    """
    from CTFd.models import Users
    from CTFd.utils.crypto import verify_password

    password = "  hunter2  "

    response = admin_client.post(
        "/ng/admin/users",
        json={
            "name": "createduser",
            "email": "createduser@example.com",
            "password": password,
        },
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["data"]["name"] == "createduser"
    assert data["data"]["email"] == "createduser@example.com"

    # the created user should be retrievable
    user_id = data["data"]["id"]
    verify = admin_client.get(f"/ng/admin/users/{user_id}")
    assert verify.status_code == 200

    assert verify_password(password, Users.query.filter_by(id=user_id).first().password)


def test_admin_create_user_missing_password(admin_client):
    """
    Test that creating a user without a password fails validation
    """
    response = admin_client.post(
        "/ng/admin/users",
        json={
            "name": "nopassword",
            "email": "nopassword@example.com",
        },
    )

    assert response.status_code == 400
    data = response.get_json()
    assert data["success"] is False
    assert "password" in data["errors"]


def test_admin_create_user_duplicate(admin_client, user_factory):
    """
    Test that creating a user with an existing email conflicts
    """
    user_factory(name="existing", email="existing@example.com")

    response = admin_client.post(
        "/ng/admin/users",
        json={
            "name": "existing",
            "email": "existing@example.com",
            "password": "hunter2",
        },
    )

    assert response.status_code == 409
    data = response.get_json()
    assert data["success"] is False


def test_non_admin_create_user(logged_in_client):
    """
    Test that non-admins cannot create users
    """
    response = logged_in_client.post(
        "/ng/admin/users",
        json={
            "name": "shouldfail",
            "email": "shouldfail@example.com",
            "password": "hunter2",
        },
    )

    assert response.status_code == 403


def test_user_put_password(admin_client, user, db_session):
    """
    Test that an admin can change an expo user's password
    """
    from CTFd.utils.crypto import verify_password

    response = admin_client.put(f"/ng/admin/users/{user.id}", json={"password": "newpassword123"})

    assert response.status_code == 200
    assert response.get_json()["success"] is True

    db_session.refresh(user)
    assert verify_password("newpassword123", user.password)


def test_user_put_password_sso_rejected(admin_client, user_factory, db_session):
    """
    Test that an admin cannot set a password for an SSO user
    """
    from CTFd.models import Users
    from CTFd.utils.crypto import verify_password

    ng_user = user_factory(name="ssouser", email="sso@example.com", password="password")
    ng_user.oauth_id = "okta|123"
    db_session.commit()
    user_id = ng_user.id

    response = admin_client.put(f"/ng/admin/users/{user_id}", json={"password": "newpassword123"})

    assert response.status_code == 400
    data = response.get_json()
    assert data["success"] is False
    assert "password" in data["errors"]

    # the password must be left untouched
    assert verify_password("password", Users.query.filter_by(id=user_id).first().password)


def test_get_user_stats(logged_in_client, user, event_factory, team_factory, challenge_factory, attempt_factory):
    """
    Test getting the current user's platform-wide statistics
    """
    from datetime import datetime

    live_event = event_factory(name="Live Event")
    practice_event = event_factory(name="Practice Event", practice=True)

    live_team = team_factory(event=live_event, members=[user])
    live_team.set_start_timestamp(datetime.utcnow())
    practice_team = team_factory(event=practice_event, members=[user])
    practice_team.set_start_timestamp(datetime.utcnow())

    # fully solved practice challenge, should count toward practice_challenges_completed
    completed_challenge = challenge_factory(event=practice_event)
    q1, q2 = completed_challenge.questions
    attempt_factory(user_id=user.id, team_id=practice_team.id, event_id=practice_event.id,
                     challenge_id=completed_challenge.id, question_id=q1.id, is_correct=True)
    attempt_factory(user_id=user.id, team_id=practice_team.id, event_id=practice_event.id,
                     challenge_id=completed_challenge.id, question_id=q2.id, is_correct=True)

    # partially solved practice challenge, should not count as completed
    partial_challenge = challenge_factory(event=practice_event)
    pq1, pq2 = partial_challenge.questions
    attempt_factory(user_id=user.id, team_id=practice_team.id, event_id=practice_event.id,
                     challenge_id=partial_challenge.id, question_id=pq1.id, is_correct=True)
    attempt_factory(user_id=user.id, team_id=practice_team.id, event_id=practice_event.id,
                     challenge_id=partial_challenge.id, question_id=pq2.id, is_correct=False)

    # correct submission on the live event, counts toward total_correct_submissions only
    live_challenge = challenge_factory(event=live_event)
    lq1 = live_challenge.questions[0]
    attempt_factory(user_id=user.id, team_id=live_team.id, event_id=live_event.id,
                     challenge_id=live_challenge.id, question_id=lq1.id, is_correct=True)

    response = logged_in_client.get("/ng/users/me/stats")

    assert response.status_code == 200
    data = response.get_json()["data"]
    assert data["total_correct_submissions"] == 4
    assert data["events_participated"] == 1
    assert data["practice_challenges_completed"] == 1


def test_user_serialize_is_sso(admin_client, user_factory, db_session):
    """
    Test that the admin serializer reports SSO status
    """
    expo = user_factory(name="expouser", email="expo@example.com")
    sso = user_factory(name="ssouser2", email="sso2@example.com")
    sso.oauth_id = "okta|456"
    db_session.commit()

    expo_res = admin_client.get(f"/ng/admin/users/{expo.id}")
    assert expo_res.get_json()["data"]["is_sso"] is False

    sso_res = admin_client.get(f"/ng/admin/users/{sso.id}")
    assert sso_res.get_json()["data"]["is_sso"] is True
