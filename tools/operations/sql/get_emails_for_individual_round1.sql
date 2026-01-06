SELECT user_id, users.email
FROM ng_demographics
JOIN users ON ng_demographics.user_id = users.id
WHERE ng_demographics.event_id = 1 
  OR ng_demographics.event_id = 2
  GROUP BY users.email, user_id