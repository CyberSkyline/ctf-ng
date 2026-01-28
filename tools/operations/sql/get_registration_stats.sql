
-- Get registration stats for each event, omit admin test event (4)
SELECT ng_events.name AS event_name, COUNT(DISTINCT ng_demographics.user_id) AS user_count, COUNT(DISTINCT ng_teams.id) AS team_count
FROM ng_demographics
JOIN ng_events ON ng_demographics.event_id = ng_events.id
LEFT JOIN ng_teams ON ng_demographics.event_id = ng_teams.event_id
WHERE ng_demographics.event_id <> 4 and ng_teams.ranked = true
GROUP BY ng_events.name;

-- Get total users on system
SELECT COUNT(users.id) as user_count
FROM users;

-- Get participating teams per event
SELECT ng_events.name AS event_name, COUNT(DISTINCT ng_teams.id)
FROM ng_teams
JOIN ng_events ON ng_teams.event_id = ng_events.id
WHERE ng_teams.start_timestamp IS NOT NULL and ng_teams.ranked = true and ng_teams.event_id <> 4
GROUP BY ng_teams.event_id;
