# Controllers

### Key Principles

-   **Separation of Concerns:** Controller functions know nothing about web requests (HTTP, JSON). They take simple Python data types as arguments and return dictionaries.
-   **Logic Lives Here:** All rules, like checking if a team is full, generating invite codes, or verifying a user can be removed, are handled in these files.

### Files

-   `team_controller.py`: Logic for creating, joining, leaving, and managing teams.
-   `world_controller.py`: Logic for creating and managing worlds.
-   `user_controller.py`: Logic for getting users pecific data
-   `database_controller.py`: Contains admin level utilities for database health checks and data resets.
