
-- Get users and all sponsors
SELECT users.name, users.email, ng_teams.name as team_name, ng_sponsors.name as sponsor, ng_scores.points as points
FROM ng_users
JOIN users on (users.id = ng_users.id)
JOIN ng_team_members ON (ng_team_members.user_id = ng_users.id)
JOIN ng_teams on (ng_team_members.team_id = ng_teams.id)
JOIN ng_scores ON (ng_scores.team_id = ng_team_members.team_id)
JOIN ng_sponsors ON (ng_users.sponsor_id = ng_sponsors.id)
WHERE ng_teams.event_id = 2 and ng_teams.ranked = true and ng_teams.start_timestamp IS NOT NULL
;

-- Get participants per sponsor per event
SELECT ng_events.name as event_name, ng_sponsors.name as sponsor, COUNT(ng_sponsors.id) as participants
FROM ng_users
JOIN users on (users.id = ng_users.id)
JOIN ng_team_members ON (ng_team_members.user_id = ng_users.id)
JOIN ng_teams on (ng_team_members.team_id = ng_teams.id)
JOIN ng_scores ON (ng_scores.team_id = ng_team_members.team_id)
JOIN ng_sponsors ON (ng_users.sponsor_id = ng_sponsors.id)
JOIN ng_events ON (ng_teams.event_id = ng_events.id)
WHERE (ng_teams.event_id = 2) and ng_teams.ranked = true and ng_teams.start_timestamp IS NOT NULL
GROUP BY ng_sponsors.id, ng_events.id
;
