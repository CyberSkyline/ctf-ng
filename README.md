# CTF-NG

## Installation
Run `./install.sh` from the project root folder

Make sure to complete the initial setup for CTFd on the webportal

## Development

### Submodules

To initialize the submodules, run this command after cloning the repo: `git submodule update --init --recursive`
To ensure that your submodules do not get out of sync, please set run `git config --local submodule.recurse true`.

Both of these steps are done for you when you run `install.sh`.

### Running the server
`npm start`

Use `CTRL + C` to stop the server. 

### Backend Development
After making any changes to the backend, you need to run `npm reload` to restart CTFd with your changes.

For linting locally you can install ruff with the following `curl -LsSf https://astral.sh/ruff/install.sh | sh`
Then run `ruff check .`

### Frontend Development
Vite provides hot module reloading. Most changes will be reflected on the page in real-time. If not, you can refresh the page. 

You do not need to run any commands after making frontend changes. 

This is a single-page app. To reach the vite entrypoint, go to `/hello`. 
