-- Round 1, Defense (Teams)
SELECT
  ng_teams.name AS name,
  1 as ranked,
  LOWER(HEX(RANDOM_BYTES(16))) as invite_code,
  LOWER(HEX(RANDOM_BYTES(8))) as seed,
  5 as event_id,
  users.id as user_id
FROM ng_scores
JOIN ng_teams ON ng_scores.team_id = ng_teams.id
JOIN ng_team_members ON (ng_teams.id = ng_team_members.team_id)
JOIN users ON (ng_team_members.user_id = users.id)
WHERE ng_teams.ranked = true and ng_teams.event_id = 1 and ng_scores.points >= 6850
ORDER BY ng_scores.points DESC;

-- Round 1, Defense (Demographics)
SELECT  
  users.id as user_id,
  5 as event_id,
  NOW() as reg_timestamp
FROM ng_scores
JOIN ng_teams ON ng_scores.team_id = ng_teams.id
JOIN ng_team_members ON (ng_teams.id = ng_team_members.team_id)
JOIN users ON (ng_team_members.user_id = users.id)
WHERE ng_teams.ranked = true and ng_teams.event_id = 1 and ng_scores.points >= 6850
ORDER BY ng_scores.points DESC;

-- Round 1, Defense (TeamMembers)
SELECT  
  users.id as user_id,
  5 as event_id,
  t2.id as team_id,
  NOW() as joined_at,
  ng_team_members.role as role
FROM ng_scores
JOIN ng_teams ON ng_scores.team_id = ng_teams.id
JOIN ng_team_members ON (ng_teams.id = ng_team_members.team_id)
JOIN users ON (ng_team_members.user_id = users.id)
JOIN ng_teams t2 ON (t2.name = ng_teams.name AND t2.event_id = 5)
WHERE ng_teams.ranked = true and ng_teams.event_id = 1 and ng_scores.points >= 6850
ORDER BY ng_scores.points DESC;

--


-- Round 1, Offense (Teams)
SELECT
  ng_teams.name AS name,
  2 as ranked,
  LOWER(HEX(RANDOM_BYTES(16))) as invite_code,
  LOWER(HEX(RANDOM_BYTES(8))) as seed,
  6 as event_id,
  users.id as user_id
FROM ng_scores
JOIN ng_teams ON ng_scores.team_id = ng_teams.id
JOIN ng_team_members ON (ng_teams.id = ng_team_members.team_id)
JOIN users ON (ng_team_members.user_id = users.id)
WHERE ng_teams.ranked = true and ng_teams.event_id = 2 and ng_scores.points >= 4902
ORDER BY ng_scores.points DESC;

-- Round 1, Offense (Demographics)
SELECT  
  users.id as user_id,
  6 as event_id,
  NOW() as reg_timestamp
FROM ng_scores
JOIN ng_teams ON ng_scores.team_id = ng_teams.id
JOIN ng_team_members ON (ng_teams.id = ng_team_members.team_id)
JOIN users ON (ng_team_members.user_id = users.id)
WHERE ng_teams.ranked = true and ng_teams.event_id = 2 and ng_scores.points >= 4902
ORDER BY ng_scores.points DESC;

-- Round 1, Offense (TeamMembers)
SELECT  
  users.id as user_id,
  6 as event_id,
  t2.id as team_id,
  NOW() as joined_at,
  ng_team_members.role as role
FROM ng_scores
JOIN ng_teams ON ng_scores.team_id = ng_teams.id
JOIN ng_team_members ON (ng_teams.id = ng_team_members.team_id)
JOIN users ON (ng_team_members.user_id = users.id)
JOIN ng_teams t2 ON (t2.name = ng_teams.name AND t2.event_id = 6)
WHERE ng_teams.ranked = true and ng_teams.event_id = 2 and ng_scores.points >= 4902
ORDER BY ng_scores.points DESC;

--

-- Round 1, Teams (Teams)
SELECT
  ng_teams.name AS name,
  3 as ranked,
  LOWER(HEX(RANDOM_BYTES(16))) as invite_code,
  LOWER(HEX(RANDOM_BYTES(8))) as seed,
  8 as event_id
FROM ng_scores
JOIN ng_teams ON ng_scores.team_id = ng_teams.id
WHERE ng_teams.ranked = true and ng_teams.event_id = 3 and ng_scores.points >= 14102
ORDER BY ng_scores.points DESC;

-- Round 1, Teams (Demographics)
SELECT  
  users.id as user_id,
  8 as event_id,
  NOW() as reg_timestamp
FROM ng_scores
JOIN ng_teams ON ng_scores.team_id = ng_teams.id
JOIN ng_team_members ON (ng_teams.id = ng_team_members.team_id)
JOIN users ON (ng_team_members.user_id = users.id)
WHERE ng_teams.ranked = true and ng_teams.event_id = 3 and ng_scores.points >= 14102
ORDER BY ng_scores.points DESC;

-- Round 1, Teams (TeamMembers)
SELECT  
  users.id as user_id,
  8 as event_id,
  t2.id as team_id,
  NOW() as joined_at,
  ng_team_members.role as role
FROM ng_scores
JOIN ng_teams ON ng_scores.team_id = ng_teams.id
JOIN ng_team_members ON (ng_teams.id = ng_team_members.team_id)
JOIN users ON (ng_team_members.user_id = users.id)
JOIN ng_teams t2 ON (t2.name = ng_teams.name AND t2.event_id = 8)
WHERE ng_teams.ranked = true and ng_teams.event_id = 3 and ng_scores.points >= 14102
ORDER BY ng_scores.points DESC;