# API Endpoints

Defines the resources for our REST API

### `admin.py` (`/admin`)

-   `GET /stats`: Get detailed system statistics, including per-world counts.
-   `GET /stats/counts`: Get simple counts of all major database tables.
-   `POST /reset`: Resets all plugin data across all worlds.
-   `POST /worlds/<id>/reset`: Resets all teams and members for a specific world.
-   `POST /cleanup`: Removes orphaned user records from the plugin tables.
-   `GET /health`: Runs a quick health check on the system.

### `teams.py` (`/teams`)

-   `GET /`: List all teams within a specific `world_id`.
-   `POST /`: Create a new team in a specific world.
-   `GET /<id>`: Get detailed information about a single team.
-   `PATCH /<id>`: Update a team's details (e.g., name).
-   `DELETE /<id>`: Disband and delete a team entirely.
-   `POST /<id>/join`: Join a specific team.
-   `POST /<id>/captain`: Assign a new captain for a team.
-   `DELETE /<id>/captain`: Demote the current captain, leaving the team without one (if needed).
-   `DELETE /<id>/members/<user_id>`: Remove a specific member from a team (if needed).
-   `POST /leave`: Leave the team you are currently on in a specific world.
-   `POST /join-by-code`: Join a team using its invite code.

### `users.py` (`/users`)

-   `GET /me/teams`: Get a list of all teams the current user is on across all worlds.
-   `GET /me/worlds/<id>/teams`: Get the current user's team for a specific world.
-   `GET /me/worlds/<id>/eligibility`: Check if the current user is eligible to join a team in a specific world.
-   `GET /me/stats`: Get participation stats for the current user.
-   `GET /<id>/teams`: (Admin) Get all teams for a specific user.
-   `GET /<id>/stats`: (Admin) Get participation stats for a specific user.

### `worlds.py` (`/worlds`)

-   `GET /`: Get a list of all available worlds with basic stats.
-   `POST /`: (Admin) Create a new world.
-   `GET /<id>`: Get detailed information for a single world, including its teams.
-   `PATCH /<id>`: (Admin) Update a world's details.
-   `GET /<id>/teams`: Get a list of all teams within a specific world.
