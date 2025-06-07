# Models

This directory contains the SQLAlchemy models for our plugin. These define the structure of our custom `ng_` (ng_ prevents name conflicts with CTFd) database tables.

### Core Models

-   `World.py`: Container for an event or competition.
-   `Team.py`: A team that exists *within* a `World`. Has a `world_id`.
-   `User.py`: Extension of CTFd's core `users` table, linking a CTFd user to our plugin's features.
-   `TeamMember.py`: The critical junction table that connects a `User` to a `Team` in a specific `World`.
