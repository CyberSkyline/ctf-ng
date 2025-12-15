# CTF-NG

## Installation
Run `./install.sh` from the project root folder

Make sure to complete the initial setup for CTFd on the webportal

## Default Container Credentials

### Individual User Containers (noVNC)
When users spawn individual containers for challenges, the system uses the `consol/debian-xfce-vnc` Docker image by default (configurable via `NOVNC_CONTAINER` in `backend/ng/config.py`).

**Default Credentials:**
- **VNC Password:** `vncpassword`
- **Root Password:** `vncpassword`
- **Default User:** Containers run as `root` by default

These credentials allow users to:
- Access the VNC desktop environment
- Use `sudo` or switch to root user within the container
- Execute privileged commands for challenge tasks

**Note:** For production environments, consider using a custom noVNC image with modified credentials or setting the `VNC_PW` environment variable when spawning containers.

## Development

### Submodules

To initialize the submodules, run this command after cloning the repo: `git submodule update --init --recursive`
To ensure that your submodules do not get out of sync, please set run `git config --local submodule.recurse true`.

Both of these steps are done for you when you run `install.sh`.

### Running the server
`pnpm start`

Use `CTRL + C` to stop the server. 

### Backend Development
After making any changes to the backend that cannot be hot-reloaded, you need to run `pnpm reload` to restart CTFd with your changes.

For linting locally you can install ruff with the following `curl -LsSf https://astral.sh/ruff/install.sh | sh`
Then run `ruff check .`

### Frontend Development
Vite provides hot module reloading. Most changes will be reflected on the page in real-time. If not, you can refresh the page. 

You do not need to run any commands after making frontend changes. 

This is a single-page app. To reach the vite entrypoint, go to `/`. 

### Docker tls install
All of the certs and config for the daemon are handled in the install script.
You might run into an issue that systemd no longer wants to start the docker daemon.
Modifying the service definition for the docker systemd service to run as root:root (User and group)
should fix this.

You will also need to change ng/config.py to make `DOCKER_HOST` point to your docker host.

### Docker Service Overrides

If you are having issues with your docker service not starting and see an error in the logs saying something about how you have
flags and configuration conflicting, you can add this file to your systemd folders to override the base docker service.

Youc can put it in an override configuration file using the following commands:

```bash
sudo mkdir /etc/systemd/system/docker.service.d/
sudo nano /etc/systemd/system/docker.service.d/override.conf
```

And then you can copy the following into the override file

```
[Service]
ExecStart=
ExecStart=/usr/bin/dockerd
User=root
Group=root
```