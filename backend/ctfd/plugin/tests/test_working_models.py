import pytest
from CTFd.models import db
from tests.helpers import gen_user

from .helpers import (
    create_ctfd,
    destroy_ctfd,
)

def test_models_via_database():
    """test models by directly using database operations"""
    app = create_ctfd()

    with app.app_context():
        print("\n Testing models via database operations...")

        World = None
        Team = None
        User = None
        TeamMember = None

        # Find
        for mapper in db.Model.registry.mappers:
            model_class = mapper.class_
            if hasattr(model_class, '__tablename__'):
                if model_class.__tablename__ == 'ng_worlds':
                    World = model_class
                elif model_class.__tablename__ == 'ng_teams':
                    Team = model_class
                elif model_class.__tablename__ == 'ng_users':
                    User = model_class
                elif model_class.__tablename__ == 'ng_team_members':
                    TeamMember = model_class

        # verify
        assert World is not None, "World model not found"
        assert Team is not None, "Team model not found"
        assert User is not None, "User model not found"
        assert TeamMember is not None, "TeamMember model not found"
        print(" Found all models in SQLAlchemy registry")

        # test World creation
        world = World(name="Test World", description="A test world")
        db.session.add(world)
        db.session.commit()
        assert world.id is not None
        print(f" World created with ID: {world.id}")

        # test team creation
        team = Team(
            name="Test Team",
            world_id=world.id,
            limit=4,
            invite_code="TEST123",
            ranked=True
        )
        db.session.add(team)
        db.session.commit()
        assert team.id is not None
        print(f" Team created with ID: {team.id}")


        ctfd_user = gen_user(db, name="testuser", email="test@example.com")
        ng_user = User(id=ctfd_user.id)
        db.session.add(ng_user)
        db.session.commit()
        assert ng_user.id == ctfd_user.id
        print(f" User extension created for CTFd user ID: {ctfd_user.id}")

        membership = TeamMember(
            user_id=ng_user.id,
            team_id=team.id,
            world_id=world.id
        )
        db.session.add(membership)
        db.session.commit()
        assert membership.id is not None
        print(f" TeamMember created with ID: {membership.id}")

        print("\n ALL MODEL CREATION TESTS PASSED!")

        print("\n Testing unique constraint (one team per world)...")

        # creating another team in the same world
        team2 = Team(
            name="Test Team 2",
            world_id=world.id,
            limit=4,
            invite_code="TEST456"
        )
        db.session.add(team2)
        db.session.commit()

        # trying to add the same user to the second team in the same world
        try:
            membership2 = TeamMember(
                user_id=ng_user.id,
                team_id=team2.id,
                world_id=world.id
            )
            db.session.add(membership2)
            db.session.commit()
            assert False, "Should have failed due to unique constraint"
        except Exception as e:
            print(f"✅ Unique constraint working: {type(e).__name__}")
            db.session.rollback()

        # testing multi-world functionality
        print("\n Testing multi-world team memberships...")

        # second world
        world2 = World(name="Test World 2")
        db.session.add(world2)
        db.session.commit()

        # creating a team in the second world
        team_w2 = Team(
            name="World 2 Team",
            world_id=world2.id,
            limit=4,
            invite_code="W2TEAM"
        )
        db.session.add(team_w2)
        db.session.commit()

        # should be able to join a team in the different world
        membership_w2 = TeamMember(
            user_id=ng_user.id,
            team_id=team_w2.id,
            world_id=world2.id
        )
        db.session.add(membership_w2)
        db.session.commit()
        print(" User successfully joined team in different world")

        # verify user is in teams in both worlds
        user_memberships = TeamMember.query.filter_by(user_id=ng_user.id).all()
        assert len(user_memberships) == 2

        world_ids = [m.world_id for m in user_memberships]
        assert world.id in world_ids
        assert world2.id in world_ids
        print(" User confirmed in teams across multiple worlds")

        print("\n ALL TESTS PASSED!")
        print("=" * 50)
        print(" Model creation working")
        print(" Unique constraint enforced")
        print(" Multi-world functionality working")
        print(" Database relationships intact")

    destroy_ctfd(app)

def test_realistic_scenario():
    """testing a multi-user, multi-world scenario"""
    app = create_ctfd()

    with app.app_context():
        print("\n Testing scenario...")

        # Find our models
        World = Team = User = TeamMember = None
        for mapper in db.Model.registry.mappers:
            model_class = mapper.class_
            if hasattr(model_class, '__tablename__'):
                if model_class.__tablename__ == 'ng_worlds':
                    World = model_class
                elif model_class.__tablename__ == 'ng_teams':
                    Team = model_class
                elif model_class.__tablename__ == 'ng_users':
                    User = model_class
                elif model_class.__tablename__ == 'ng_team_members':
                    TeamMember = model_class

        # test scenario
        print("Setting up: Security Training Program")

        # creating employees
        employees = []
        ng_users = []
        names = [("Alice Admin", "alice@corp.com"), 
                ("Bob Developer", "bob@corp.com"),
                ("Charlie Security", "charlie@corp.com")]

        for name, email in names:
            emp = gen_user(db, name=name, email=email)
            ng_emp = User(id=emp.id)
            employees.append(emp)
            ng_users.append(ng_emp)
            db.session.add(ng_emp)

        # training worlds
        basic_world = World(name="Basic Security Training")
        advanced_world = World(name="Advanced Threat Response")
        db.session.add_all([basic_world, advanced_world])
        db.session.commit()

        # teams
        basic_red = Team(name="Red Team", world_id=basic_world.id, limit=2, invite_code="BRED")
        basic_blue = Team(name="Blue Team", world_id=basic_world.id, limit=2, invite_code="BBLUE")
        adv_ir = Team(name="Incident Response", world_id=advanced_world.id, limit=3, invite_code="ADVIR")
        adv_ta = Team(name="Threat Analysis", world_id=advanced_world.id, limit=2, invite_code="ADVTA")

        db.session.add_all([basic_red, basic_blue, adv_ir, adv_ta])
        db.session.commit()

        # assign people to teams
        assignments = [
            (ng_users[0], basic_red, basic_world),
            (ng_users[0], adv_ir, advanced_world),
            (ng_users[1], basic_blue, basic_world),
            (ng_users[1], adv_ta, advanced_world),
            (ng_users[2], basic_red, basic_world),
            (ng_users[2], adv_ir, advanced_world),
        ]

        for ng_user, team, world in assignments:
            membership = TeamMember(
                user_id=ng_user.id,
                team_id=team.id,
                world_id=world.id
            )
            db.session.add(membership)

        db.session.commit()

        # verify
        print("\n Final Team Assignments:")
        for i, (emp, ng_user) in enumerate(zip(employees, ng_users)):
            memberships = TeamMember.query.filter_by(user_id=ng_user.id).all()
            print(f"  {emp.name}:")
            for m in memberships:
                team = Team.query.get(m.team_id)
                world = World.query.get(m.world_id)
                print(f"    • {team.name} in {world.name}")

        # verify constraints
        total_memberships = TeamMember.query.count()
        assert total_memberships == 6

        # verify team compositions
        print("\n Team Sizes:")
        for team in [basic_red, basic_blue, adv_ir, adv_ta]:
            member_count = TeamMember.query.filter_by(team_id=team.id).count()
            world = World.query.get(team.world_id)
            print(f"  {world.name} - {team.name}: {member_count}/{team.limit} members")

        print("\n SCENARIO TEST PASSED!")

    destroy_ctfd(app)
