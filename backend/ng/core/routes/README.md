# Plugin API Routes

All API routes are prefixed with `/ng`.

## Admin Routes (`/ng/admin`)

1.  `GET /ng/admin/stats` - Retrieves system statistics including per-event breakdowns and empty teams. (Admin only)
2.  `GET /ng/admin/stats/counts` - Retrieves basic data counts for events, teams, users, and memberships. (Admin only)
3.  `POST /ng/admin/reset` - Resets ALL plugin data. Requires confirmation. (Admin only)
4.  `POST /ng/admin/events/<event_id>/reset` - Resets all data for a specific event. Requires confirmation. (Admin only)
5.  `POST /ng/admin/cleanup` - Cleans up orphaned data, such as user records with no team memberships. (Admin only)
6.  `GET /ng/admin/health` - Checks system health and data integrity, returning a report with warnings if any. (Admin only)

## Team Routes (`/ng/teams`)

1.  `GET /ng/teams?event_id=<event_id>` - Retrieves a list of all teams within a specified event, including member counts and limits.
2.  `POST /ng/teams` - Creates a new team in a specified event. The current authenticated user becomes the captain.
3.  `GET /ng/teams/<team_id>` - Retrieves detailed information about a specific team, including its members.
4.  `PATCH /ng/teams/<team_id>` - Updates the details (e.g., name) of a specific team. (Captain/Admin only)
5.  `DELETE /ng/teams/<team_id>` - Disbands (deletes) a specific team and all its memberships. (Captain/Admin only)
6.  `POST /ng/teams/join` - Allows the current authenticated user to join a team using its invite code. This is the only way to join a team.
7.  `POST /ng/teams/leave` - Allows the current authenticated user to leave their current team in a specified event. Note: Captains cannot leave their teams and must transfer captaincy first.
8.  `GET /ng/teams/<team_id>/captain` - Retrieves information about the current captain of a specific team.
9.  `POST /ng/teams/<team_id>/captain` - Transfers team captaincy to another member of the team. (Captain/Admin only)
10. `DELETE /ng/teams/<team_id>/members/<user_id>` - Removes a specific member from a team. The team's invite code is automatically regenerated for security. (Captain/Admin only)

## User Routes (`/ng/users`)

1.  `GET /ng/users/me/teams` - Retrieves all team memberships for the current authenticated user across all events.
2.  `GET /ng/users/me/events/<event_id>/teams` - Retrieves the current authenticated user's team membership details within a specific event.
3.  `GET /ng/users/me/events/<event_id>/eligibility` - Checks if the current authenticated user is eligible to join a team in the specified event.
4.  `GET /ng/users/me/stats` - Retrieves participation statistics for the current authenticated user across all events.
5.  `GET /ng/users/<user_id>/teams` - Retrieves all team memberships for a specified user across all events. (Admin only)
6.  `GET /ng/users/<user_id>/stats` - Retrieves participation statistics for a specified user across all events. (Admin only)

## Event Routes (`/ng/events`)

1.  `GET /ng/events` - Retrieves a list of all training events, including team and member statistics for each.
2.  `POST /ng/events` - Creates a new training event with optional scheduling (start_time, end_time) and locking capabilities. (Admin only)
3.  `GET /ng/events/<event_id>` - Retrieves detailed information about a specific event, including a list of its teams.
4.  `PATCH /ng/events/<event_id>` - Updates the information (e.g., name, description, start_time, end_time, locked status) of a specific event. (Admin only)
5.  `GET /ng/events/<event_id>/teams` - Retrieves a list of all teams within a specific event.

