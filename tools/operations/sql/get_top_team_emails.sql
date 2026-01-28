-- Round 1, Defense
SELECT ng_teams.name AS team_name, ng_scores.points, users.name, users.email, users.id
FROM ng_scores
JOIN ng_teams ON ng_scores.team_id = ng_teams.id
JOIN ng_team_members ON (ng_teams.id = ng_team_members.team_id)
JOIN users ON (ng_team_members.user_id = users.id)
WHERE ng_teams.ranked = true and ng_teams.event_id = 1 and ng_scores.points >= 6850
ORDER BY ng_scores.points DESC;

-- Round 1, Offense
SELECT ng_teams.name AS team_name, ng_scores.points, users.name, users.email, users.id
FROM ng_scores
JOIN ng_teams ON ng_scores.team_id = ng_teams.id
JOIN ng_team_members ON (ng_teams.id = ng_team_members.team_id)
JOIN users ON (ng_team_members.user_id = users.id)
WHERE ng_teams.ranked = true and ng_teams.event_id = 2 and ng_scores.points >= 4902
ORDER BY ng_scores.points DESC;

-- Round 1, Teams
SELECT ng_teams.name AS team_name, ng_scores.points, users.name, users.email, users.id
FROM ng_scores
JOIN ng_teams ON ng_scores.team_id = ng_teams.id
JOIN ng_team_members ON (ng_teams.id = ng_team_members.team_id)
JOIN users ON (ng_team_members.user_id = users.id)
WHERE ng_teams.ranked = true and ng_teams.event_id = 3 and ng_scores.points >= 14102
ORDER BY ng_scores.points DESC;