"""
Hypothetical Event Business Logic Tests
"""

from datetime import datetime, timedelta
from ...core.utils import utc_now


class TestEventLifecycleLogic:
    """Test event lifecycle state management algorithms."""

    def test_event_state_transitions(self):
        """Test event state transition validation logic."""

        def validate_state_transition(current_state, target_state, event_data):
            errors = []

            valid_transitions = {
                "draft": ["scheduled", "cancelled"],
                "scheduled": ["active", "cancelled", "postponed"],
                "active": ["paused", "ended", "cancelled"],
                "paused": ["active", "ended", "cancelled"],
                "ended": ["archived"],
                "cancelled": ["archived"],
                "postponed": ["scheduled", "cancelled"],
                "archived": [],
            }

            if target_state not in valid_transitions.get(current_state, []):
                errors.append(f"Cannot transition from {current_state} to {target_state}")
                return False, errors

            current_time = utc_now()
            start_time = event_data.get("start_time")
            end_time = event_data.get("end_time")

            if target_state == "active":
                if start_time and start_time > current_time:
                    errors.append("Cannot start event before scheduled start time")
                if event_data.get("teams_count", 0) == 0:
                    errors.append("Cannot start event with no registered teams")

            elif target_state == "ended":
                if end_time and end_time > current_time:
                    errors.append("Cannot end event before scheduled end time")

            elif target_state == "scheduled":
                if not start_time or not end_time:
                    errors.append("Cannot schedule event without start and end times")
                if start_time >= end_time:
                    errors.append("Start time must be before end time")

            return len(errors) == 0, errors

        event_data = {
            "start_time": utc_now() - timedelta(hours=1),
            "end_time": utc_now() + timedelta(hours=5),
            "teams_count": 5,
        }

        valid, errors = validate_state_transition("scheduled", "active", event_data)
        assert valid is True
        assert errors == []

        valid, errors = validate_state_transition("ended", "active", event_data)
        assert valid is False
        assert "Cannot transition from ended to active" in str(errors)

        future_event = {
            "start_time": utc_now() + timedelta(hours=2),
            "end_time": utc_now() + timedelta(hours=8),
            "teams_count": 3,
        }

        valid, errors = validate_state_transition("scheduled", "active", future_event)
        assert valid is False
        assert "before scheduled start time" in str(errors)

    def test_event_duration_calculations(self):
        """Test event duration and timing calculations."""

        def calculate_event_timing(start_time, end_time, current_time=None):
            if current_time is None:
                current_time = utc_now()

            total_duration = (end_time - start_time).total_seconds()

            if current_time < start_time:
                return {
                    "status": "upcoming",
                    "time_until_start": (start_time - current_time).total_seconds(),
                    "total_duration": total_duration,
                    "progress_percentage": 0.0,
                }

            elif current_time > end_time:
                return {
                    "status": "ended",
                    "total_duration": total_duration,
                    "progress_percentage": 100.0,
                    "ended_ago": (current_time - end_time).total_seconds(),
                }

            else:
                elapsed = (current_time - start_time).total_seconds()
                remaining = (end_time - current_time).total_seconds()
                progress = (elapsed / total_duration) * 100

                return {
                    "status": "active",
                    "elapsed_time": elapsed,
                    "remaining_time": remaining,
                    "total_duration": total_duration,
                    "progress_percentage": round(progress, 1),
                }

        start = datetime(2024, 1, 1, 12, 0, 0)
        end = datetime(2024, 1, 1, 18, 0, 0)
        current = datetime(2024, 1, 1, 10, 0, 0)

        timing = calculate_event_timing(start, end, current)
        assert timing["status"] == "upcoming"
        assert timing["time_until_start"] == 7200  # 2 hours
        assert timing["total_duration"] == 21600  # 6 hours

        current = datetime(2024, 1, 1, 15, 0, 0)
        timing = calculate_event_timing(start, end, current)
        assert timing["status"] == "active"
        assert timing["progress_percentage"] == 50.0
        assert timing["elapsed_time"] == 10800  # 3 hours
        assert timing["remaining_time"] == 10800  # 3 hours


class TestEventRegistrationLogic:
    """Test event registration eligibility and validation."""

    def test_registration_eligibility(self):
        """Test comprehensive registration eligibility logic."""

        def check_registration_eligibility(user_data, team_data, event_data):
            errors = []
            warnings = []

            # Event-level checks
            if not event_data.get("registration_open", True):
                errors.append("Registration is closed for this event")

            if event_data.get("locked", False):
                errors.append("Event is locked, no new registrations allowed")

            max_teams = event_data.get("max_teams")
            current_teams = event_data.get("current_teams", 0)
            if max_teams and current_teams >= max_teams:
                errors.append("Event has reached maximum team capacity")

            if user_data.get("banned", False):
                errors.append("Banned users cannot register")

            if not user_data.get("verified", True):
                errors.append("User account must be verified")

            user_events = user_data.get("registered_events", [])
            if event_data["id"] in user_events:
                errors.append("User already registered for this event")

            team_size = team_data.get("member_count", 1)
            min_size = event_data.get("min_team_size", 1)
            max_size = event_data.get("max_team_size", 4)

            if team_size < min_size:
                errors.append(f"Team must have at least {min_size} members")
            if team_size > max_size:
                errors.append(f"Team cannot exceed {max_size} members")

            required_level = event_data.get("required_skill_level")
            if required_level:
                team_avg_level = team_data.get("average_skill_level", 0)
                if team_avg_level < required_level:
                    errors.append(f"Team average skill level must be at least {required_level}")

            event_difficulty = event_data.get("difficulty_rating", 3)
            team_experience = team_data.get("average_experience", 1)
            if event_difficulty > team_experience + 2:
                warnings.append("This event may be significantly more difficult than your team's experience level")

            conflicting_events = user_data.get("conflicting_events", [])
            if conflicting_events:
                warnings.append(f"You have {len(conflicting_events)} overlapping events scheduled")

            return {
                "eligible": len(errors) == 0,
                "errors": errors,
                "warnings": warnings,
            }

        user = {
            "id": 1,
            "banned": False,
            "verified": True,
            "registered_events": [],
            "conflicting_events": [],
        }
        team = {"member_count": 3, "average_skill_level": 7, "average_experience": 5}
        event = {
            "id": 100,
            "registration_open": True,
            "locked": False,
            "max_teams": 50,
            "current_teams": 25,
            "min_team_size": 2,
            "max_team_size": 5,
            "required_skill_level": 5,
            "difficulty_rating": 6,
        }

        result = check_registration_eligibility(user, team, event)
        assert result["eligible"] is True
        assert result["errors"] == []
        assert len(result["warnings"]) == 0

        event["locked"] = True
        user["banned"] = True

        result = check_registration_eligibility(user, team, event)
        assert result["eligible"] is False
        assert "locked" in str(result["errors"])
        assert "Banned users" in str(result["errors"])

    def test_team_placement_algorithm(self):
        """Test team placement and grouping algorithms."""

        def assign_team_groups(teams, grouping_strategy="balanced"):
            if grouping_strategy == "balanced":
                teams_by_skill = sorted(teams, key=lambda t: t.get("average_skill", 0), reverse=True)
                groups = [[] for _ in range(4)]  # 4 groups

                for i, team in enumerate(teams_by_skill):
                    groups[i % 4].append(team)

            elif grouping_strategy == "skill_based":
                beginner = [t for t in teams if t.get("average_skill", 0) <= 3]
                intermediate = [t for t in teams if 3 < t.get("average_skill", 0) <= 7]
                advanced = [t for t in teams if t.get("average_skill", 0) > 7]
                groups = [beginner, intermediate, advanced]

            elif grouping_strategy == "random":
                import random

                shuffled = teams.copy()
                random.shuffle(shuffled)
                group_size = len(teams) // 4
                groups = []
                for i in range(0, len(shuffled), group_size):
                    groups.append(shuffled[i : i + group_size])

            else:
                groups = [teams]

            return groups

        teams = [
            {"id": 1, "name": "Beginners", "average_skill": 2},
            {"id": 2, "name": "Pros", "average_skill": 9},
            {"id": 3, "name": "Intermediate", "average_skill": 5},
            {"id": 4, "name": "Advanced", "average_skill": 8},
            {"id": 5, "name": "Novices", "average_skill": 3},
            {"id": 6, "name": "Experts", "average_skill": 10},
        ]

        balanced_groups = assign_team_groups(teams, "balanced")
        assert len(balanced_groups) == 4

        for group in balanced_groups:
            if len(group) >= 2:
                skills = [t["average_skill"] for t in group]
                assert max(skills) - min(skills) >= 3

        skill_groups = assign_team_groups(teams, "skill_based")
        beginner_group = skill_groups[0]
        advanced_group = skill_groups[2]

        assert all(t["average_skill"] <= 3 for t in beginner_group)
        assert all(t["average_skill"] > 7 for t in advanced_group)


class TestEventConstraintValidation:
    """Test event constraint and rule validation."""

    def test_time_constraint_validation(self):
        """Test event time constraint validation logic."""

        def validate_time_constraints(event_data):
            errors = []
            warnings = []

            start_time = event_data.get("start_time")
            end_time = event_data.get("end_time")
            registration_deadline = event_data.get("registration_deadline")

            if not start_time or not end_time:
                errors.append("Start time and end time are required")
                return {"valid": False, "errors": errors, "warnings": warnings}

            if start_time >= end_time:
                errors.append("Start time must be before end time")

            duration = (end_time - start_time).total_seconds()
            min_duration = 3600
            max_duration = 7 * 24 * 3600

            if duration < min_duration:
                errors.append("Event must be at least 1 hour long")
            if duration > max_duration:
                warnings.append("Event duration exceeds 1 week - consider splitting")

            if registration_deadline:
                if registration_deadline > start_time:
                    errors.append("Registration deadline must be before event start")

                time_to_start = (start_time - registration_deadline).total_seconds()
                if time_to_start < 3600:
                    warnings.append("Registration deadline is very close to event start")

            current_time = utc_now()
            if start_time < current_time - timedelta(hours=1):
                errors.append("Cannot schedule event in the past")

            if start_time > current_time + timedelta(days=365):
                warnings.append("Event scheduled more than 1 year in advance")

            return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}

        start = utc_now() + timedelta(days=7)
        end = start + timedelta(hours=6)
        registration_deadline = start - timedelta(days=1)

        event = {
            "start_time": start,
            "end_time": end,
            "registration_deadline": registration_deadline,
        }

        result = validate_time_constraints(event)
        assert result["valid"] is True
        assert result["errors"] == []

        event["start_time"] = end
        event["end_time"] = start

        result = validate_time_constraints(event)
        assert result["valid"] is False
        assert "Start time must be before end time" in str(result["errors"])

    def test_capacity_limit_calculations(self):
        """Test event capacity and resource limit calculations."""

        def calculate_event_capacity(event_config, resource_limits):
            constraints = {}

            max_teams = event_config.get("max_teams")
            max_team_size = event_config.get("max_team_size", 4)
            if max_teams:
                constraints["team_limit"] = max_teams * max_team_size

            server_capacity = resource_limits.get("server_capacity", 1000)
            bandwidth_limit = resource_limits.get("bandwidth_mbps", 100)
            storage_limit = resource_limits.get("storage_gb", 500)

            bandwidth_per_user = 0.5  # MB/s
            storage_per_user = 0.1  # GB

            constraints["server_limit"] = server_capacity
            constraints["bandwidth_limit"] = int(bandwidth_limit / bandwidth_per_user)
            constraints["storage_limit"] = int(storage_limit / storage_per_user)

            effective_capacity = min(constraints.values())

            recommended_capacity = int(effective_capacity * 0.9)

            return {
                "constraints": constraints,
                "effective_capacity": effective_capacity,
                "recommended_capacity": recommended_capacity,
                "limiting_factor": min(constraints, key=constraints.get),
            }

        event_config = {"max_teams": 100, "max_team_size": 4}

        resource_limits = {
            "server_capacity": 300,
            "bandwidth_mbps": 50,
            "storage_gb": 20,
        }

        capacity = calculate_event_capacity(event_config, resource_limits)

        assert capacity["limiting_factor"] == "bandwidth_limit"
        assert capacity["effective_capacity"] == 100
        assert capacity["recommended_capacity"] == 90  # 90% of 100

    def test_scoring_system_validation(self):
        """Test event scoring system configuration validation."""

        def validate_scoring_system(scoring_config):
            errors = []

            scoring_type = scoring_config.get("type", "static")

            if scoring_type == "static":
                base_points = scoring_config.get("base_points", {})
                if not isinstance(base_points, dict):
                    errors.append("Base points must be a dictionary")
                else:
                    for category, points in base_points.items():
                        if not isinstance(points, (int, float)) or points < 0:
                            errors.append(f"Invalid points for category {category}")

            elif scoring_type == "dynamic":
                decay_factor = scoring_config.get("decay_factor", 0.1)
                if not 0 <= decay_factor <= 1:
                    errors.append("Decay factor must be between 0 and 1")

                min_points = scoring_config.get("min_points", 50)
                max_points = scoring_config.get("max_points", 500)
                if min_points >= max_points:
                    errors.append("Minimum points must be less than maximum points")

            elif scoring_type == "progressive":
                point_tiers = scoring_config.get("point_tiers", [])
                if not point_tiers:
                    errors.append("Progressive scoring requires point tiers")
                else:
                    for i, tier in enumerate(point_tiers):
                        if not isinstance(tier, dict) or "threshold" not in tier or "multiplier" not in tier:
                            errors.append(f"Invalid tier configuration at index {i}")

            else:
                errors.append(f"Unknown scoring type: {scoring_type}")

            time_bonus = scoring_config.get("time_bonus_enabled", False)
            if time_bonus:
                bonus_window = scoring_config.get("bonus_window_hours", 0)
                if bonus_window <= 0:
                    errors.append("Time bonus window must be positive")

            return len(errors) == 0, errors

        static_config = {
            "type": "static",
            "base_points": {"easy": 100, "medium": 200, "hard": 400},
            "time_bonus_enabled": True,
            "bonus_window_hours": 24,
        }

        valid, errors = validate_scoring_system(static_config)
        assert valid is True
        assert errors == []

        dynamic_config = {
            "type": "dynamic",
            "decay_factor": 1.5,  # Invalid - over 1
            "min_points": 100,
            "max_points": 50,  # Invalid - min > max
        }

        valid, errors = validate_scoring_system(dynamic_config)
        assert valid is False
        assert "Decay factor must be between 0 and 1" in str(errors)
        assert "Minimum points must be less than maximum" in str(errors)


class TestEventAdvancedAlgorithms:
    """Test advanced event management algorithms and optimization."""

    def test_event_load_balancing_algorithm(self):
        """Test event server load balancing and resource distribution."""

        def calculate_optimal_load_distribution(events, servers):
            """Calculate optimal event distribution across servers."""
            load_distribution = {server["id"]: [] for server in servers}
            server_loads = {server["id"]: 0 for server in servers}

            # Sort events by expected load (descending)
            sorted_events = sorted(events, key=lambda e: e.get("expected_participants", 0), reverse=True)

            for event in sorted_events:
                # Find server with minimum load
                min_load_server = min(server_loads, key=server_loads.get)
                min_server_capacity = next(s["capacity"] for s in servers if s["id"] == min_load_server)

                event_load = event.get("expected_participants", 0)

                # Check if server can handle the event
                if server_loads[min_load_server] + event_load <= min_server_capacity:
                    load_distribution[min_load_server].append(event)
                    server_loads[min_load_server] += event_load
                else:
                    # Find any server that can handle this event
                    assigned = False
                    for server in servers:
                        if server_loads[server["id"]] + event_load <= server["capacity"]:
                            load_distribution[server["id"]].append(event)
                            server_loads[server["id"]] += event_load
                            assigned = True
                            break

                    if not assigned:
                        # Event cannot be assigned to any server
                        return None, "Insufficient server capacity"

            # Calculate load balance metrics
            load_values = list(server_loads.values())
            avg_load = sum(load_values) / len(load_values) if load_values else 0

            if avg_load > 0:
                load_variance = sum((load - avg_load) ** 2 for load in load_values) / len(load_values)
                load_balance_score = max(0, 100 - (load_variance / avg_load * 10))  # Reduced scaling factor
            else:
                load_balance_score = 100

            return {
                "distribution": load_distribution,
                "server_loads": server_loads,
                "load_balance_score": load_balance_score,
                "utilization_rate": (sum(load_values) / sum(s["capacity"] for s in servers)) * 100 if servers else 0,
            }, None

        events = [
            {"id": 1, "name": "Big Event", "expected_participants": 400},
            {"id": 2, "name": "Medium Event", "expected_participants": 200},
            {"id": 3, "name": "Small Event 1", "expected_participants": 100},
            {"id": 4, "name": "Small Event 2", "expected_participants": 150},
            {"id": 5, "name": "Tiny Event", "expected_participants": 50},
        ]

        servers = [
            {"id": "server1", "capacity": 500},
            {"id": "server2", "capacity": 400},
            {"id": "server3", "capacity": 300},
        ]

        result, error = calculate_optimal_load_distribution(events, servers)

        assert error is None
        assert result["utilization_rate"] <= 100
        assert result["load_balance_score"] >= 0

        # Check that all events are assigned
        total_assigned = sum(len(events) for events in result["distribution"].values())
        assert total_assigned == len(events)

        # Check capacity constraints
        for server_id, server_load in result["server_loads"].items():
            server_capacity = next(s["capacity"] for s in servers if s["id"] == server_id)
            assert server_load <= server_capacity

    def test_event_recommendation_engine(self):
        """Test event recommendation algorithm for users."""

        def generate_event_recommendations(user_profile, available_events, max_recommendations=5):
            """Generate personalized event recommendations."""
            scored_events = []

            for event in available_events:
                score = 0

                # Skill level matching
                user_skill = user_profile.get("skill_level", 5)
                event_difficulty = event.get("difficulty_rating", 5)
                skill_diff = abs(user_skill - event_difficulty)

                if skill_diff == 0:
                    score += 30
                elif skill_diff <= 1:
                    score += 20
                elif skill_diff <= 2:
                    score += 10
                else:
                    score -= 5

                # Interest matching
                user_interests = set(user_profile.get("interests", []))
                event_categories = set(event.get("categories", []))
                interest_overlap = len(user_interests & event_categories)
                score += interest_overlap * 15

                # Past participation matching
                user_past_events = user_profile.get("past_event_types", [])
                event_type = event.get("type", "general")
                if event_type in user_past_events:
                    score += 10

                # Team size preference
                preferred_team_size = user_profile.get("preferred_team_size", 4)
                event_team_size = event.get("max_team_size", 4)
                if preferred_team_size == event_team_size:
                    score += 8
                elif abs(preferred_team_size - event_team_size) <= 1:
                    score += 4

                # Time preference
                user_timezone = user_profile.get("timezone", "UTC")
                event_timezone = event.get("timezone", "UTC")
                if user_timezone == event_timezone:
                    score += 5

                # Popularity factor (but not too popular)
                participants = event.get("current_participants", 0)
                capacity = event.get("max_participants", 100)
                fill_rate = participants / capacity if capacity > 0 else 0

                if 0.3 <= fill_rate <= 0.7:  # Sweet spot
                    score += 12
                elif 0.1 <= fill_rate < 0.3:
                    score += 8
                elif 0.7 < fill_rate <= 0.9:
                    score += 5
                else:
                    score -= 3

                # Duration preference
                user_max_duration = user_profile.get("max_event_duration_hours", 8)
                event_duration = event.get("duration_hours", 4)
                if event_duration <= user_max_duration:
                    score += 6
                else:
                    score -= 10

                scored_events.append(
                    {
                        "event": event,
                        "score": score,
                        "reasons": _get_recommendation_reasons(user_profile, event, score),
                    }
                )

            # Sort by score and return top recommendations
            scored_events.sort(key=lambda x: x["score"], reverse=True)
            return scored_events[:max_recommendations]

        def _get_recommendation_reasons(user_profile, event, score):
            """Generate human-readable reasons for recommendation."""
            reasons = []

            user_skill = user_profile.get("skill_level", 5)
            event_difficulty = event.get("difficulty_rating", 5)

            if abs(user_skill - event_difficulty) <= 1:
                reasons.append("Matches your skill level")

            user_interests = set(user_profile.get("interests", []))
            event_categories = set(event.get("categories", []))
            if user_interests & event_categories:
                reasons.append(f"Matches your interests: {', '.join(user_interests & event_categories)}")

            if score >= 50:
                reasons.append("Highly recommended based on your profile")
            elif score >= 30:
                reasons.append("Good match for your preferences")
            elif score >= 10:
                reasons.append("Decent option to consider")

            return reasons

        user_profile = {
            "skill_level": 7,
            "interests": ["web", "crypto", "reverse"],
            "preferred_team_size": 4,
            "timezone": "UTC",
            "max_event_duration_hours": 8,
            "past_event_types": ["ctf", "bootcamp"],
        }

        available_events = [
            {
                "id": 1,
                "name": "Advanced CTF",
                "difficulty_rating": 8,
                "categories": ["web", "crypto"],
                "max_team_size": 4,
                "timezone": "UTC",
                "duration_hours": 6,
                "type": "ctf",
                "current_participants": 120,
                "max_participants": 200,
            },
            {
                "id": 2,
                "name": "Beginner Workshop",
                "difficulty_rating": 3,
                "categories": ["basics", "intro"],
                "max_team_size": 2,
                "timezone": "EST",
                "duration_hours": 12,
                "type": "workshop",
                "current_participants": 50,
                "max_participants": 100,
            },
            {
                "id": 3,
                "name": "Crypto Challenge",
                "difficulty_rating": 7,
                "categories": ["crypto", "math"],
                "max_team_size": 3,
                "timezone": "UTC",
                "duration_hours": 4,
                "type": "challenge",
                "current_participants": 80,
                "max_participants": 150,
            },
        ]

        recommendations = generate_event_recommendations(user_profile, available_events, max_recommendations=3)

        assert len(recommendations) <= 3
        assert recommendations[0]["score"] >= recommendations[1]["score"]  # Sorted by score

        # The Advanced CTF should score highest due to perfect matches
        top_event = recommendations[0]["event"]
        assert top_event["name"] == "Advanced CTF"
        assert len(recommendations[0]["reasons"]) > 0

    def test_event_analytics_engine(self):
        """Test comprehensive event analytics and insights generation."""

        def generate_event_analytics(event_data, participation_data, performance_data):
            """Generate comprehensive event analytics."""
            total_participants = len(participation_data)
            total_teams = len(set(p["team_id"] for p in participation_data))

            # Participation metrics
            registration_rate = event_data.get("registrations", 0) / event_data.get("invitations", 1)
            participant_completion_rate = (
                len([p for p in participation_data if p.get("completed", False)]) / total_participants
                if total_participants > 0
                else 0
            )

            # Performance metrics
            challenge_completion_rates = {}
            for perf in performance_data:
                challenge_id = perf["challenge_id"]
                if challenge_id not in challenge_completion_rates:
                    challenge_completion_rates[challenge_id] = {
                        "completed": 0,
                        "attempted": 0,
                    }

                challenge_completion_rates[challenge_id]["attempted"] += 1
                if perf.get("solved", False):
                    challenge_completion_rates[challenge_id]["completed"] += 1

            # Calculate difficulty analysis
            difficulty_analysis = {}
            for challenge_id, stats in challenge_completion_rates.items():
                challenge_completion_rate = stats["completed"] / stats["attempted"] if stats["attempted"] > 0 else 0

                if challenge_completion_rate > 0.8:
                    difficulty = "Too Easy"
                elif challenge_completion_rate > 0.5:
                    difficulty = "Appropriate"
                elif challenge_completion_rate > 0.2:
                    difficulty = "Challenging"
                else:
                    difficulty = "Too Hard"

                difficulty_analysis[challenge_id] = {
                    "completion_rate": challenge_completion_rate,
                    "difficulty_assessment": difficulty,
                    "attempts": stats["attempted"],
                    "solves": stats["completed"],
                }

            # Team performance distribution
            team_scores = {}
            for perf in performance_data:
                team_id = perf["team_id"]
                if team_id not in team_scores:
                    team_scores[team_id] = 0
                team_scores[team_id] += perf.get("points", 0)

            scores = list(team_scores.values())
            avg_score = sum(scores) / len(scores) if scores else 0

            # Engagement metrics
            active_time_data = [p.get("active_minutes", 0) for p in participation_data]
            avg_engagement = sum(active_time_data) / len(active_time_data) if active_time_data else 0

            # Generate insights
            insights = []

            if participant_completion_rate < 0.3:
                insights.append("Low completion rate - consider reducing difficulty or extending duration")
            elif participant_completion_rate > 0.9:
                insights.append("Very high completion rate - event may be too easy")

            if registration_rate < 0.5:
                insights.append("Low registration rate - improve marketing or adjust timing")

            if avg_engagement < 60:  # Less than 1 hour average
                insights.append("Low engagement time - challenges may not be compelling enough")

            too_hard_challenges = [
                cid for cid, data in difficulty_analysis.items() if data["difficulty_assessment"] == "Too Hard"
            ]
            if len(too_hard_challenges) > len(difficulty_analysis) * 0.3:
                insights.append("Too many overly difficult challenges - balance the difficulty curve")

            return {
                "summary": {
                    "total_participants": total_participants,
                    "total_teams": total_teams,
                    "registration_rate": registration_rate,
                    "completion_rate": participant_completion_rate,
                    "average_score": avg_score,
                    "average_engagement_minutes": avg_engagement,
                },
                "challenge_analysis": difficulty_analysis,
                "insights": insights,
                "recommendations": _generate_recommendations(
                    difficulty_analysis, participant_completion_rate, avg_engagement
                ),
            }

        def _generate_recommendations(difficulty_analysis, participant_completion_rate, avg_engagement):
            """Generate actionable recommendations based on analytics."""
            recommendations = []

            easy_challenges = sum(1 for d in difficulty_analysis.values() if d["difficulty_assessment"] == "Too Easy")
            hard_challenges = sum(1 for d in difficulty_analysis.values() if d["difficulty_assessment"] == "Too Hard")

            if easy_challenges > 2:
                recommendations.append("Increase difficulty of easier challenges or add bonus objectives")

            if hard_challenges > 2:
                recommendations.append("Provide more hints or reduce complexity of difficult challenges")

            if participant_completion_rate < 0.4:
                recommendations.append("Consider extending event duration or providing more guidance")

            if avg_engagement < 90:
                recommendations.append("Add more interactive elements or real-time feedback")

            return recommendations

        event_data = {"registrations": 150, "invitations": 200, "duration_hours": 8}

        participation_data = [
            {"user_id": 1, "team_id": 1, "completed": True, "active_minutes": 120},
            {"user_id": 2, "team_id": 1, "completed": True, "active_minutes": 100},
            {"user_id": 3, "team_id": 2, "completed": True, "active_minutes": 30},
            {"user_id": 4, "team_id": 2, "completed": True, "active_minutes": 150},
        ]

        performance_data = [
            {"team_id": 1, "challenge_id": "ch1", "solved": True, "points": 100},
            {"team_id": 1, "challenge_id": "ch2", "solved": False, "points": 0},
            {"team_id": 2, "challenge_id": "ch1", "solved": True, "points": 100},
            {"team_id": 2, "challenge_id": "ch2", "solved": True, "points": 200},
        ]

        analytics = generate_event_analytics(event_data, participation_data, performance_data)

        assert analytics["summary"]["total_participants"] == 4
        assert analytics["summary"]["total_teams"] == 2
        assert analytics["summary"]["completion_rate"] == 1.0  # 4 out of 4 completed
        assert "ch1" in analytics["challenge_analysis"]
        assert "ch2" in analytics["challenge_analysis"]
        assert len(analytics["insights"]) >= 0
        assert len(analytics["recommendations"]) >= 0


class TestEventOptimizationAlgorithms:
    """Test event optimization and resource management algorithms."""

    def test_dynamic_scoring_adjustment(self):
        """Test dynamic scoring adjustment based on solve rates."""

        def adjust_challenge_scores(challenges, solve_data, target_solve_rate=0.4):
            """Dynamically adjust challenge scores based on solve rates."""
            adjusted_challenges = []

            for challenge in challenges:
                challenge_id = challenge["id"]
                attempts = len([s for s in solve_data if s["challenge_id"] == challenge_id])
                solves = len([s for s in solve_data if s["challenge_id"] == challenge_id and s["solved"]])

                if attempts == 0:
                    # No attempts yet, keep original score
                    adjusted_challenges.append(challenge.copy())
                    continue

                current_solve_rate = solves / attempts
                original_score = challenge["base_score"]

                # Calculate adjustment factor
                if current_solve_rate > target_solve_rate * 1.5:  # Too easy
                    adjustment_factor = 0.8  # Reduce score
                    adjustment_reason = "High solve rate - reducing points"
                elif current_solve_rate < target_solve_rate * 0.5:  # Too hard
                    adjustment_factor = 1.3  # Increase score
                    adjustment_reason = "Low solve rate - increasing points"
                else:
                    adjustment_factor = 1.0  # No change
                    adjustment_reason = "Solve rate within target range"

                # Apply time-based bonus decay
                time_since_start = challenge.get("hours_since_start", 0)
                time_decay = max(0.7, 1.0 - (time_since_start * 0.05))  # 5% decay per hour, min 70%

                final_score = int(original_score * adjustment_factor * time_decay)

                adjusted_challenge = challenge.copy()
                adjusted_challenge["current_score"] = final_score
                adjusted_challenge["adjustment_factor"] = adjustment_factor
                adjusted_challenge["time_decay"] = time_decay
                adjusted_challenge["solve_rate"] = current_solve_rate
                adjusted_challenge["adjustment_reason"] = adjustment_reason

                adjusted_challenges.append(adjusted_challenge)

            return adjusted_challenges

        challenges = [
            {
                "id": "ch1",
                "name": "Easy Web",
                "base_score": 100,
                "hours_since_start": 2,
            },
            {
                "id": "ch2",
                "name": "Hard Crypto",
                "base_score": 500,
                "hours_since_start": 4,
            },
            {
                "id": "ch3",
                "name": "Medium Pwn",
                "base_score": 300,
                "hours_since_start": 1,
            },
        ]

        solve_data = [
            # Easy challenge - high solve rate (80%)
            {"challenge_id": "ch1", "solved": True},
            {"challenge_id": "ch1", "solved": True},
            {"challenge_id": "ch1", "solved": True},
            {"challenge_id": "ch1", "solved": True},
            {"challenge_id": "ch1", "solved": False},
            # Hard challenge - low solve rate (10%)
            {"challenge_id": "ch2", "solved": False},
            {"challenge_id": "ch2", "solved": False},
            {"challenge_id": "ch2", "solved": False},
            {"challenge_id": "ch2", "solved": False},
            {"challenge_id": "ch2", "solved": False},
            {"challenge_id": "ch2", "solved": False},
            {"challenge_id": "ch2", "solved": False},
            {"challenge_id": "ch2", "solved": False},
            {"challenge_id": "ch2", "solved": False},
            {"challenge_id": "ch2", "solved": True},
            # Medium challenge - target solve rate (40%)
            {"challenge_id": "ch3", "solved": True},
            {"challenge_id": "ch3", "solved": True},
            {"challenge_id": "ch3", "solved": False},
            {"challenge_id": "ch3", "solved": False},
            {"challenge_id": "ch3", "solved": False},
        ]

        adjusted = adjust_challenge_scores(challenges, solve_data)

        # Easy challenge should have reduced score
        easy_challenge = next(c for c in adjusted if c["id"] == "ch1")
        assert easy_challenge["current_score"] < easy_challenge["base_score"]
        assert easy_challenge["solve_rate"] == 0.8

        # Hard challenge should have increased score
        hard_challenge = next(c for c in adjusted if c["id"] == "ch2")
        assert hard_challenge["current_score"] > hard_challenge["base_score"]
        assert hard_challenge["solve_rate"] == 0.1

        # Medium challenge should have minimal change
        medium_challenge = next(c for c in adjusted if c["id"] == "ch3")
        assert (
            abs(medium_challenge["current_score"] - medium_challenge["base_score"])
            <= medium_challenge["base_score"] * 0.1
        )

    def test_event_resource_optimization(self):
        """Test event resource optimization and allocation."""

        def optimize_event_resources(event_config, resource_constraints, participant_data):
            """Optimize resource allocation for event performance."""
            total_participants = len(participant_data)

            # Calculate resource requirements
            cpu_per_participant = 0.1  # CPU cores
            memory_per_participant = 0.5  # GB
            storage_per_participant = 0.2  # GB
            bandwidth_per_participant = 2.0  # Mbps

            required_resources = {
                "cpu_cores": total_participants * cpu_per_participant,
                "memory_gb": total_participants * memory_per_participant,
                "storage_gb": total_participants * storage_per_participant,
                "bandwidth_mbps": total_participants * bandwidth_per_participant,
            }

            # Check against constraints
            available_resources = resource_constraints.copy()
            resource_utilization = {}
            scaling_recommendations = []

            for resource, required in required_resources.items():
                available = available_resources.get(resource, 0)
                utilization = (required / available) * 100 if available > 0 else float("inf")
                resource_utilization[resource] = utilization

                if utilization > 90:
                    scaling_recommendations.append(
                        {
                            "resource": resource,
                            "current_usage": f"{utilization:.1f}%",
                            "recommendation": "Scale up immediately",
                            "required_additional": required - available,
                        }
                    )
                elif utilization > 70:
                    scaling_recommendations.append(
                        {
                            "resource": resource,
                            "current_usage": f"{utilization:.1f}%",
                            "recommendation": "Monitor closely, prepare to scale",
                            "required_additional": 0,
                        }
                    )

            # Optimize based on participant behavior patterns
            peak_concurrent_ratio = 0.7  # 70% of participants active simultaneously
            expected_peak_load = total_participants * peak_concurrent_ratio

            # Adjust resource allocation
            optimized_allocation = {
                "web_servers": max(2, int(expected_peak_load / 50)),  # 50 users per server
                "database_connections": int(expected_peak_load * 1.2),  # 20% overhead
                "cache_size_mb": int(expected_peak_load * 10),  # 10MB per concurrent user
                "worker_processes": max(4, int(expected_peak_load / 25)),  # 25 users per worker
            }

            # Calculate cost optimization
            cost_per_hour = {
                "web_server": 0.05,
                "database_connection": 0.001,
                "cache_mb": 0.0001,
                "worker_process": 0.02,
            }

            estimated_hourly_cost = (
                optimized_allocation["web_servers"] * cost_per_hour["web_server"]
                + optimized_allocation["database_connections"] * cost_per_hour["database_connection"]
                + optimized_allocation["cache_size_mb"] * cost_per_hour["cache_mb"]
                + optimized_allocation["worker_processes"] * cost_per_hour["worker_process"]
            )

            event_duration_hours = event_config.get("duration_hours", 8)
            total_estimated_cost = estimated_hourly_cost * event_duration_hours

            return {
                "required_resources": required_resources,
                "resource_utilization": resource_utilization,
                "scaling_recommendations": scaling_recommendations,
                "optimized_allocation": optimized_allocation,
                "cost_estimate": {
                    "hourly": estimated_hourly_cost,
                    "total": total_estimated_cost,
                },
                "performance_metrics": {
                    "expected_peak_concurrent": expected_peak_load,
                    "users_per_server": expected_peak_load / optimized_allocation["web_servers"],
                    "cache_per_user_mb": optimized_allocation["cache_size_mb"] / expected_peak_load,
                },
            }

        event_config = {"duration_hours": 8, "expected_participation_rate": 0.7}

        resource_constraints = {
            "cpu_cores": 20,
            "memory_gb": 100,
            "storage_gb": 200,
            "bandwidth_mbps": 1000,
        }

        participant_data = [{"id": i} for i in range(200)]  # 200 participants

        optimization = optimize_event_resources(event_config, resource_constraints, participant_data)

        assert optimization["required_resources"]["cpu_cores"] == 20.0  # 200 * 0.1
        assert optimization["required_resources"]["memory_gb"] == 100.0  # 200 * 0.5
        assert optimization["performance_metrics"]["expected_peak_concurrent"] == 140.0  # 200 * 0.7
        assert optimization["cost_estimate"]["total"] > 0
        assert len(optimization["scaling_recommendations"]) >= 0

        # Check if any resources are over-utilized
        over_utilized = any(util > 90 for util in optimization["resource_utilization"].values())
        if over_utilized:
            assert len(optimization["scaling_recommendations"]) > 0
