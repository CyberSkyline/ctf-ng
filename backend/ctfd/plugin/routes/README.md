# Plugin API Routes

All API routes are prefixed with `/plugin/api`.

## Admin Routes (`/plugin/api/admin`)

1.  `GET /plugin/api/admin/stats` - Retrieves system statistics including per-world breakdowns and empty teams. (Admin only)
2.  `GET /plugin/api/admin/stats/counts` - Retrieves basic data counts for worlds, teams, users, and memberships. (Admin only)
3.  `POST /plugin/api/admin/reset` - Resets ALL plugin data. Requires confirmation. (Admin only)
4.  `POST /plugin/api/admin/worlds/<world_id>/reset` - Resets all data for a specific world. Requires confirmation. (Admin only)
5.  `POST /plugin/api/admin/cleanup` - Cleans up orphaned data, such as user records with no team memberships. (Admin only)
6.  `GET /plugin/api/admin/health` - Checks system health and data integrity, returning a report with warnings if any. (Admin only)

## Team Routes (`/plugin/api/teams`)

1.  `GET /plugin/api/teams?world_id=<world_id>` - Retrieves a list of all teams within a specified world, including member counts and limits.
2.  `POST /plugin/api/teams` - Creates a new team in a specified world. The current authenticated user becomes the captain.
3.  `GET /plugin/api/teams/<team_id>` - Retrieves detailed information about a specific team, including its members.
4.  `PATCH /plugin/api/teams/<team_id>` - Updates the details (e.g., name) of a specific team. (Captain/Admin only)
5.  `DELETE /plugin/api/teams/<team_id>` - Disbands (deletes) a specific team and all its memberships. (Captain/Admin only)
6.  `POST /plugin/api/teams/<team_id>/join` - Allows the current authenticated user to join a specific team in a given world.
7.  `POST /plugin/api/teams/leave` - Allows the current authenticated user to leave their current team in a specified world.
8.  `POST /plugin/api/teams/join-by-code` - Allows the current authenticated user to join a team using its invite code.
9.  `GET /plugin/api/teams/<team_id>/captain` - Retrieves information about the current captain of a specific team.
10. `POST /plugin/api/teams/<team_id>/captain` - Transfers team captaincy to another member of the team. (Captain/Admin only)
11. `DELETE /plugin/api/teams/<team_id>/captain` - Removes the current captain, demoting them to a regular member.
12. `DELETE /plugin/api/teams/<team_id>/members/<user_id>` - Removes a specific member from a team. (Captain/Admin only)

## User Routes (`/plugin/api/users`)

1.  `GET /plugin/api/users/me/teams` - Retrieves all team memberships for the current authenticated user across all worlds.
2.  `GET /plugin/api/users/me/worlds/<world_id>/teams` - Retrieves the current authenticated user's team membership details within a specific world.
3.  `GET /plugin/api/users/me/worlds/<world_id>/eligibility` - Checks if the current authenticated user is eligible to join a team in the specified world.
4.  `GET /plugin/api/users/me/stats` - Retrieves participation statistics for the current authenticated user across all worlds.
5.  `GET /plugin/api/users/<user_id>/teams` - Retrieves all team memberships for a specified user across all worlds. (Admin only)
6.  `GET /plugin/api/users/<user_id>/stats` - Retrieves participation statistics for a specified user across all worlds. (Admin only)

## World Routes (`/plugin/api/worlds`)

1.  `GET /plugin/api/worlds` - Retrieves a list of all training worlds, including team and member statistics for each.
2.  `POST /plugin/api/worlds` - Creates a new training world. (Admin only)
3.  `GET /plugin/api/worlds/<world_id>` - Retrieves detailed information about a specific world, including a list of its teams.
4.  `PATCH /plugin/api/worlds/<world_id>` - Updates the information (e.g., name, description) of a specific world. (Admin only)
5.  `GET /plugin/api/worlds/<world_id>/teams` - Retrieves a list of all teams within a specific world.

---
