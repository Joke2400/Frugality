# Frugality

A webapp to help you find the cheapest groceries near you.
This is a long-term project that I like to work on in my free time.

**NOTE:** *Currently being rewritten with FastAPI / Postgres / Vue.js, may be a bit funky at times. Work has thus far focused on rewriting the backend code.*

## What is this?
### Problem:
- Groceries price comparison tools exist in Finland, but most are built by the grocery store chains themselves.
- The incentives for transparency do not necessarily always align with corporate profit incentives.
- Not that simple to access, some require even you to be a part of a loyalty-programme.

### Project vision:
- A simple-to-use, unbiased groceries price comparison app, built for use within Finland.
- Current project scope is limited to grocery stores in Finland.
    - S-Ryhmä/Kesko-stores will be implemented first.
- Free-to-use, will be made available through a website and (maybe) a mobile app.

### Planned features
- Compare several stores & products simultaneously.
- Location-based searching (ex. 'compare stores near you') using gmaps API.
- Factor in other costs (ex. delivery or transit costs).
- Price history statistics:
    - Results get cached server-side to maintain a historical record.
    - Keeps track of price development (ex. inflation/greedflation, drops in price/sales).
    - Keeps track of product sizes (ex. to monitor shrinkflation).
    - Will periodically update records of popular products/stores.

## Setup for local development
**NOTE:** *Project is a WIP - it's recommended to only host it locally.*

### Prerequisites:
- Guide assumes the use of VSCode:
    - Python extension & Devcontainers extension
- Python (3.12.1).
- Docker

### Steps:
1. **Create a '.env' file with the following fields:**
    - POSTGRES_USER - The username for the postgres user
    - POSTGRES_PASSWORD - The password for the postgres user.
    - POSTGRES_DB - The name for the database to be used.
    - POSTGRES_PORT - The port to host the database on (This might not need to be specified later on.)

2. **Build & run the container images using the Devcontainers extension:**
    - Press ctrl+shift+p inside of VSCode and select the *'Devcontainers: Rebuild and reopen in container'* option.
    - Devcontainers will then build & run the docker services defined in the docker compose file.
        - These services can then be started/shutdown via the Docker Desktop app or a CLI.
    - You're done! The containers should now be running in Docker!

3. **If you want to run the backend service outside of a container:**
    - Ensure you have `virtualenv` installed. (Install with: `pip install virtualenv`).
    - Open the terminal & ensure you're in the project root directory.
    - Create a Python virtual environment by running the command below:
        - `virtualenv name_for_your_env --python='path_to_your_python_3.12.exe'`
    - Next up, activate the virtual environment by running the following:
        - Windows - `./name_for_your_env/Scripts/activate`
        - Linux - `source /name_for_your_env/Scripts/activate`
    - Then install the required dependencies with pip:
        - `pip install -r requirements.txt`
    - Ensure the Postgres database image is running in docker.
    - Debug the backend with the 'Python: FastAPI' launch configuration defined in the launch.json file.
    - You're done! Now you can debug backend code outside of a container!