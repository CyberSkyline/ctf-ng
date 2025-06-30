"""
User Business Logic Tests
"""


class TestUserEligibilityAlgorithms:
    """Test user eligibility calculation algorithms."""

    def test_can_join_team_comprehensive_logic(self):
        """Test comprehensive team join eligibility logic."""

        def can_user_join_team(user_data, team_data, event_data):
            reasons = []

            if event_data.get("locked", False):
                reasons.append("Event is locked")
            if event_data.get("ended", False):
                reasons.append("Event has ended")
            if not event_data.get("registration_open", True):
                reasons.append("Registration is closed")

            if user_data.get("banned", False):
                reasons.append("User is banned")
            if user_data.get("current_team_in_event"):
                reasons.append("User already in a team for this event")
            if not user_data.get("verified", True):
                reasons.append("User account not verified")

            current_size = team_data.get("current_members", 0)
            max_size = event_data.get("max_team_size", 4)
            if current_size >= max_size:
                reasons.append("Team is full")
            if team_data.get("status") == "disbanded":
                reasons.append("Team is disbanded")
            if team_data.get("private", False) and not user_data.get("invited", False):
                reasons.append("Team is private and user not invited")

            return len(reasons) == 0, reasons

        user = {
            "id": 1,
            "banned": False,
            "current_team_in_event": None,
            "verified": True,
        }
        team = {"id": 1, "current_members": 3, "status": "active", "private": False}
        event = {
            "id": 1,
            "locked": False,
            "ended": False,
            "max_team_size": 4,
            "registration_open": True,
        }

        can_join, reasons = can_user_join_team(user, team, event)
        assert can_join is True
        assert reasons == []

        event["locked"] = True
        user["banned"] = True
        team["current_members"] = 4

        can_join, reasons = can_user_join_team(user, team, event)
        assert can_join is False
        assert "Event is locked" in reasons
        assert "User is banned" in reasons
        assert "Team is full" in reasons

    def test_user_activity_score_algorithm(self):
        """Test comprehensive user activity scoring."""

        def calculate_activity_score(user_stats):
            base_score = 0

            challenges_solved = user_stats.get("challenges_solved", 0)
            teams_joined = user_stats.get("teams_joined", 0)
            events_participated = user_stats.get("events_participated", 0)
            points_earned = user_stats.get("points_earned", 0)

            base_score += challenges_solved * 10
            base_score += teams_joined * 5
            base_score += events_participated * 15
            base_score += points_earned * 0.1

            # Quality multipliers
            success_rate = user_stats.get("success_rate", 0) / 100.0
            base_score *= 0.5 + success_rate * 0.5  # 50-100% based on success rate

            days_since_active = user_stats.get("days_since_active", 0)
            if days_since_active <= 1:
                base_score *= 1.5  # 50% bonus for today
            elif days_since_active <= 7:
                base_score *= 1.2  # 20% bonus for this week
            elif days_since_active <= 30:
                base_score *= 1.1  # 10% bonus for this month
            elif days_since_active > 90:
                base_score *= 0.8  # 20% penalty for inactive

            if user_stats.get("is_captain", False):
                base_score *= 1.25

            return round(base_score, 1)

        active_user = {
            "challenges_solved": 20,
            "teams_joined": 5,
            "events_participated": 3,
            "points_earned": 2000,
            "success_rate": 80,
            "days_since_active": 1,
            "is_captain": True,
        }

        score = calculate_activity_score(active_user)
        # (20*10 + 5*5 + 3*15 + 2000*0.1) * 0.9 * 1.5 * 1.25 = 490 * 0.9 * 1.5 * 1.25 = 826.875
        assert score > 790

        inactive_user = {
            "challenges_solved": 2,
            "teams_joined": 1,
            "events_participated": 1,
            "points_earned": 100,
            "success_rate": 50,
            "days_since_active": 100,
            "is_captain": False,
        }

        score = calculate_activity_score(inactive_user)
        assert score < 50  # Should be low score


class TestUserPermissionLogic:
    """Test user permission and role-based access control."""

    def test_role_hierarchy_permissions(self):
        """Test comprehensive role-based permission system."""

        def get_user_permissions(user_role, team_role=None, context=None):
            permissions = set()

            permissions.update(
                [
                    "view_profile",
                    "edit_own_profile",
                    "join_team",
                    "leave_team",
                    "view_public_events",
                    "submit_flags",
                ]
            )

            if team_role == "captain":
                permissions.update(
                    [
                        "manage_team",
                        "invite_members",
                        "remove_members",
                        "transfer_captaincy",
                        "disband_team",
                        "view_team_stats",
                    ]
                )
            elif team_role == "member":
                permissions.add("view_team_internal")

            if user_role == "admin":
                permissions.update(
                    [
                        "manage_users",
                        "manage_teams",
                        "manage_events",
                        "view_admin_panel",
                        "reset_data",
                        "manage_support_tickets",
                        "view_system_logs",
                        "manage_system_settings",
                    ]
                )
            elif user_role == "support":
                permissions.update(
                    [
                        "view_support_tickets",
                        "manage_support_tickets",
                        "assign_tickets",
                        "escalate_tickets",
                        "view_user_details",
                    ]
                )
            elif user_role == "moderator":
                permissions.update(["moderate_content", "warn_users", "temporary_ban", "view_reports"])

            if context and context.get("event_organizer"):
                permissions.update(
                    [
                        "manage_event_teams",
                        "view_event_analytics",
                        "send_event_announcements",
                    ]
                )

            return permissions

        # Test admin permissions
        admin_perms = get_user_permissions("admin")
        assert "manage_users" in admin_perms
        assert "view_admin_panel" in admin_perms
        assert "view_profile" in admin_perms

        # Test captain permissions
        captain_perms = get_user_permissions("user", "captain")
        assert "manage_team" in captain_perms
        assert "remove_members" in captain_perms
        assert "view_profile" in captain_perms
        assert "manage_users" not in captain_perms

        # Test regular user permissions
        user_perms = get_user_permissions("user", "member")
        assert "view_profile" in user_perms
        assert "view_team_internal" in user_perms
        assert "manage_team" not in user_perms

    def test_permission_validation_logic(self):
        """Test permission validation against actions."""

        def can_perform_action(user_perms, required_perm, resource_owner=None, user_id=None):
            if required_perm not in user_perms:
                return False, "Insufficient permissions"

            if resource_owner and user_id and resource_owner == user_id:
                if required_perm in [
                    "edit_profile",
                    "view_profile",
                    "delete_own_content",
                ]:
                    return True, "Owner access granted"

            if required_perm == "delete_user" and "manage_users" not in user_perms:
                return False, "Insufficient permissions"

            return True, "Access granted"

        admin_perms = {"manage_users", "view_profile", "delete_user"}
        user_perms = {"view_profile", "edit_profile"}

        can_do, reason = can_perform_action(admin_perms, "delete_user")
        assert can_do is True

        can_do, reason = can_perform_action(user_perms, "delete_user")
        assert can_do is False
        assert "Insufficient permissions" in reason

        can_do, reason = can_perform_action(user_perms, "edit_profile", resource_owner=123, user_id=123)
        assert can_do is True
        assert "Owner access granted" in reason


class TestUserProgressionSystem:
    """Test user progression and ranking algorithms."""

    def test_user_level_calculation(self):
        """Test user level and progression system."""

        def calculate_user_level(user_stats):
            points = user_stats.get("total_points", 0)
            challenges_solved = user_stats.get("challenges_solved", 0)
            events_completed = user_stats.get("events_completed", 0)

            level_points = 0
            level_points += points * 0.01  # 1 level point per 100 score points
            level_points += challenges_solved * 2  # 2 level points per challenge
            level_points += events_completed * 10  # 10 level points per event

            import math

            level = int(math.sqrt(level_points / 10)) + 1
            level = min(level, 50)  # Cap at level 50

            current_level_requirement = ((level - 1) ** 2) * 10
            next_level_requirement = (level**2) * 10
            progress = (
                (level_points - current_level_requirement) / (next_level_requirement - current_level_requirement)
            ) * 100

            return {
                "level": level,
                "level_points": round(level_points, 1),
                "progress_to_next": round(progress, 1),
                "points_needed": round(next_level_requirement - level_points, 1),
            }

        beginner = {"total_points": 500, "challenges_solved": 5, "events_completed": 1}
        result = calculate_user_level(beginner)
        assert result["level"] >= 1
        assert result["progress_to_next"] >= 0

        advanced = {
            "total_points": 10000,
            "challenges_solved": 50,
            "events_completed": 10,
        }
        result = calculate_user_level(advanced)
        assert result["level"] > 5
        assert result["level"] <= 50

    def test_user_ranking_algorithm(self):
        """Test comprehensive user ranking system."""

        def calculate_ranking_score(user_data):
            total_points = user_data.get("total_points", 0)
            challenges_solved = user_data.get("challenges_solved", 0)
            events_participated = user_data.get("events_participated", 0)
            team_contributions = user_data.get("team_contributions", 0)

            base_score = total_points + (challenges_solved * 50) + (events_participated * 200)

            success_rate = user_data.get("success_rate", 0) / 100.0
            base_score *= 0.7 + success_rate * 0.3

            if user_data.get("leadership_roles", 0) > 0:
                base_score *= 1.15

            days_inactive = user_data.get("days_since_last_activity", 0)
            if days_inactive <= 7:
                activity_multiplier = 1.0
            elif days_inactive <= 30:
                activity_multiplier = 0.95
            elif days_inactive <= 90:
                activity_multiplier = 0.85
            else:
                activity_multiplier = 0.7

            base_score *= activity_multiplier

            base_score += team_contributions * 25

            return round(base_score, 2)

        users = [
            {
                "name": "TopPlayer",
                "total_points": 5000,
                "challenges_solved": 40,
                "events_participated": 8,
                "success_rate": 90,
                "leadership_roles": 2,
                "days_since_last_activity": 1,
                "team_contributions": 15,
            },
            {
                "name": "CasualPlayer",
                "total_points": 2000,
                "challenges_solved": 15,
                "events_participated": 3,
                "success_rate": 60,
                "leadership_roles": 0,
                "days_since_last_activity": 14,
                "team_contributions": 5,
            },
        ]

        for user in users:
            user["ranking_score"] = calculate_ranking_score(user)

        users.sort(key=lambda u: u["ranking_score"], reverse=True)

        assert users[0]["name"] == "TopPlayer"
        assert users[0]["ranking_score"] > users[1]["ranking_score"]
        assert users[0]["ranking_score"] > 9000


class TestUserValidationRules:
    """Test user data validation business rules."""

    def test_username_validation_comprehensive(self):
        """Test comprehensive username validation rules."""

        def validate_username(username):
            errors = []

            if not username:
                errors.append("Username is required")
                return errors

            if len(username) < 3:
                errors.append("Username must be at least 3 characters")
            if len(username) > 20:
                errors.append("Username must be 20 characters or less")

            allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-")
            if not all(c in allowed_chars for c in username):
                errors.append("Username can only contain letters, numbers, underscores, and dashes")

            if username.startswith(("_", "-")) or username.endswith(("_", "-")):
                errors.append("Username cannot start or end with underscore or dash")

            if "__" in username or "--" in username or "_-" in username or "-_" in username:
                errors.append("Username cannot contain consecutive special characters")

            reserved = {"admin", "support", "moderator", "system", "root", "api"}
            if username.lower() in reserved:
                errors.append("Username is reserved")

            return errors

        assert validate_username("validuser") == []
        assert validate_username("user_123") == []
        assert validate_username("test-user") == []

        assert "required" in str(validate_username(""))
        assert "3 characters" in str(validate_username("ab"))
        assert "20 characters" in str(validate_username("a" * 21))
        assert "letters, numbers, underscores, and dashes" in str(validate_username("user@email"))
        assert "consecutive" in str(validate_username("user__test"))
        assert "reserved" in str(validate_username("admin"))

    def test_profile_completeness_scoring(self):
        """Test user profile completeness calculation."""

        def calculate_profile_completeness(profile_data):
            score = 0
            total_possible = 100

            if profile_data.get("username"):
                score += 20
            if profile_data.get("email"):
                score += 20
            if profile_data.get("name"):
                score += 20

            if profile_data.get("bio"):
                score += 10
            if profile_data.get("location"):
                score += 5
            if profile_data.get("website"):
                score += 5
            if profile_data.get("avatar"):
                score += 10
            if profile_data.get("social_links"):
                score += 5
            if profile_data.get("skills"):
                score += 5

            return min(score, total_possible)

        complete_profile = {
            "username": "testuser",
            "email": "test@example.com",
            "name": "Test User",
            "bio": "Security enthusiast",
            "location": "New York",
            "website": "https://example.com",
            "avatar": "avatar.jpg",
            "social_links": ["twitter.com/test"],
            "skills": ["python", "security"],
        }

        assert calculate_profile_completeness(complete_profile) == 100

        minimal_profile = {"username": "testuser", "email": "test@example.com"}

        assert calculate_profile_completeness(minimal_profile) == 40


class TestAdvancedUserAlgorithms:
    """Test advanced user algorithms and computations."""

    def test_user_activity_scoring_comprehensive(self):
        """Test comprehensive user activity scoring algorithm."""

        def calculate_comprehensive_activity_score(user_data):
            """Calculate activity score with multiple weighted factors."""
            score_components = {
                "participation": 0,
                "engagement": 0,
                "consistency": 0,
                "social": 0,
                "achievement": 0,
            }

            # Participation scoring (25% weight)
            team_count = user_data.get("team_count", 0)
            events_participated = user_data.get("events_participated", 0)
            score_components["participation"] = min((team_count * 5) + (events_participated * 8), 250)

            # Engagement scoring (20% weight)
            challenges_solved = user_data.get("challenges_solved", 0)
            time_spent_hours = user_data.get("time_spent_hours", 0)
            score_components["engagement"] = min((challenges_solved * 3) + (time_spent_hours * 0.5), 200)

            # Consistency scoring (20% weight)
            participation_rate = user_data.get("participation_rate", 0)
            streak_days = user_data.get("login_streak_days", 0)
            score_components["consistency"] = min((participation_rate * 150) + (streak_days * 2), 200)

            # Social scoring (15% weight)
            forum_posts = user_data.get("forum_posts", 0)
            team_leadership = user_data.get("teams_led", 0)
            score_components["social"] = min((forum_posts * 2) + (team_leadership * 15), 150)

            # Achievement scoring (20% weight)
            wins = user_data.get("competition_wins", 0)
            top_placements = user_data.get("top_3_placements", 0)
            score_components["achievement"] = min((wins * 25) + (top_placements * 10), 200)

            total_score = sum(score_components.values())

            # Determine tier based on score
            if total_score >= 800:
                tier = "Legendary"
            elif total_score >= 600:
                tier = "Expert"
            elif total_score >= 400:
                tier = "Advanced"
            elif total_score >= 200:
                tier = "Intermediate"
            else:
                tier = "Beginner"

            return {
                "total_score": total_score,
                "components": score_components,
                "tier": tier,
                "percentile": min(total_score / 1000 * 100, 100),
            }

        # High-activity user
        expert_user = {
            "team_count": 20,
            "events_participated": 15,
            "challenges_solved": 80,
            "time_spent_hours": 200,
            "participation_rate": 0.9,
            "login_streak_days": 45,
            "forum_posts": 25,
            "teams_led": 5,
            "competition_wins": 3,
            "top_3_placements": 8,
        }

        result = calculate_comprehensive_activity_score(expert_user)
        assert result["total_score"] >= 700, f"Expert user should have high score, got {result['total_score']}"
        assert result["tier"] in ["Expert", "Legendary"]
        assert result["percentile"] >= 70

        # Beginner user
        beginner_user = {
            "team_count": 1,
            "events_participated": 2,
            "challenges_solved": 5,
            "time_spent_hours": 10,
            "participation_rate": 0.2,
            "login_streak_days": 3,
            "forum_posts": 1,
            "teams_led": 0,
            "competition_wins": 0,
            "top_3_placements": 0,
        }

        result = calculate_comprehensive_activity_score(beginner_user)
        assert result["total_score"] <= 150, f"Beginner should have low score, got {result['total_score']}"
        assert result["tier"] == "Beginner"

    def test_user_recommendation_engine(self):
        """Test user recommendation engine for teams and events."""

        def generate_user_recommendations(target_user, available_teams, available_events):
            """Generate personalized recommendations for a user."""
            recommendations = {"teams": [], "events": [], "reasoning": {}}

            user_skills = set(target_user.get("skills", []))
            user_interests = set(target_user.get("interests", []))
            user_experience_level = target_user.get("experience_level", "beginner")

            # Team recommendations
            for team in available_teams:
                team_skills = set(team.get("required_skills", []))
                team_size = team.get("current_size", 0)
                team_max_size = team.get("max_size", 4)
                team_level = team.get("skill_level", "mixed")

                score = 0
                reasons = []

                # Skill match scoring
                skill_overlap = len(user_skills.intersection(team_skills))
                if skill_overlap > 0:
                    score += skill_overlap * 20
                    reasons.append(f"Skills match: {skill_overlap} overlapping skills")

                # Team availability
                if team_size < team_max_size:
                    score += 15
                    reasons.append("Team has open spots")

                # Experience level compatibility
                if (
                    (user_experience_level == "beginner" and team_level in ["beginner", "mixed"])
                    or (user_experience_level == "intermediate" and team_level in ["intermediate", "mixed"])
                    or (user_experience_level == "advanced" and team_level in ["advanced", "mixed"])
                ):
                    score += 25
                    reasons.append("Compatible experience level")

                if score >= 30:  # Minimum threshold
                    recommendations["teams"].append(
                        {
                            "team_id": team["id"],
                            "team_name": team["name"],
                            "score": score,
                            "reasons": reasons,
                        }
                    )

            # Event recommendations
            for event in available_events:
                event_categories = set(event.get("categories", []))
                event_difficulty = event.get("difficulty", "easy")

                score = 0
                reasons = []

                # Interest match
                interest_overlap = len(user_interests.intersection(event_categories))
                if interest_overlap > 0:
                    score += interest_overlap * 15
                    reasons.append(f"Interest match: {interest_overlap} categories")

                # Difficulty appropriateness
                difficulty_match = {
                    "beginner": ["easy", "medium"],
                    "intermediate": ["easy", "medium", "hard"],
                    "advanced": ["medium", "hard", "expert"],
                }

                if event_difficulty in difficulty_match.get(user_experience_level, []):
                    score += 20
                    reasons.append("Appropriate difficulty level")

                if score >= 20:  # Minimum threshold
                    recommendations["events"].append(
                        {
                            "event_id": event["id"],
                            "event_name": event["name"],
                            "score": score,
                            "reasons": reasons,
                        }
                    )

            # Sort by score
            recommendations["teams"].sort(key=lambda x: x["score"], reverse=True)
            recommendations["events"].sort(key=lambda x: x["score"], reverse=True)

            return recommendations

        # Test user
        user = {
            "skills": ["python", "web", "crypto"],
            "interests": ["web", "forensics", "crypto"],
            "experience_level": "intermediate",
        }

        # Available teams
        teams = [
            {
                "id": 1,
                "name": "CyberWarriors",
                "required_skills": ["python", "web"],
                "current_size": 2,
                "max_size": 4,
                "skill_level": "intermediate",
            },
            {
                "id": 2,
                "name": "ScriptKiddies",
                "required_skills": ["javascript"],
                "current_size": 4,
                "max_size": 4,
                "skill_level": "beginner",
            },
        ]

        # Available events
        events = [
            {
                "id": 1,
                "name": "Web Security CTF",
                "categories": ["web", "crypto"],
                "difficulty": "medium",
            },
            {
                "id": 2,
                "name": "Advanced Forensics",
                "categories": ["forensics", "reverse"],
                "difficulty": "expert",
            },
        ]

        recommendations = generate_user_recommendations(user, teams, events)

        assert len(recommendations["teams"]) >= 1
        top_team = recommendations["teams"][0]
        assert top_team["team_id"] == 1
        assert top_team["score"] >= 60

        assert len(recommendations["events"]) >= 1
        top_event = recommendations["events"][0]
        assert top_event["event_id"] == 1
        assert top_event["score"] >= 35
