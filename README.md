# Frugality

A webapp to help you find the cheapest groceries near you.
This is a long-term project that I like to work on in my free time.

**NOTE:** _Currently being rewritten with FastAPI / Postgres / Vue.js, may be a bit funky at times. Work has thus far focused on rewriting the backend code._

## What is this?

### The problem:

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

## Set up for development

**NOTE:** _The project is a WIP - it's recommended to only host it locally at the moment._

### Prerequisites:

- The project requires Python 3.12 due to the use of newer syntax.
- This project assumes the use of VSCode:
  - Extensions: Python & Devcontainers
- Docker for containerization:
  - Installing only the Docker Engine is recommended on Linux, as Docker Desktop seems to cause file-permission to be set to 'root' inside the container which leads to permission errors on runtime after building the backend image. A workaround is to of course manually change the permissions after building.

## Steps:

1. **Run the setup.sh install script (Linux only)**

   - setup.sh creates a `.env` file with default environment variables for the apps, remember change the password environment variable.
   - **NOTE:** _Environment variables are inherently unsafe for credentials, hence the disclaimer above about hosting over the internet. This method is temporary & will be remedied at a later point._
   - setup.sh will also install the `virtualenv` package if it's not already installed & create a new Python virtual environment at the project root.
   - This allows the backend to be run from outside a container _(for debugging purposes)_.

2. **Or if you want to do this manually (Or you're running Windows)**

   - _Note that you need to create the `.env` files manually if you didn't run setup.sh. The required variables can be read from the setup.sh script, there will be a batch file created later_
   - Ensure you have `virtualenv` installed. (Install with: `pip install virtualenv`).
   - Open the terminal & ensure you're in the project root directory.
   - Create a Python virtual environment by running the command below:
     - `virtualenv name_for_your_env --python='path_to_your_python_3.12.exe'`
   - Next up, activate the virtual environment by running the following:
     - Windows - `./name_for_your_env/Scripts/activate`
     - Linux - `source /name_for_your_env/bin/activate`
   - Then install the required dependencies with pip:
     - `pip install -r ./backend/requirements.txt`

3. **Run the application**

   Simply run `docker compose up` and docker will build & run the services. NOTE: You need `sudo` if your user is not in the docker user-group.

   For debugging you can choose to only start the `test_database` service. Then you can run the existing debug profiles from _outside_ of a container. The profiles are defined in the `.vscode/launch.json`.
   NOTE: The project is configured in a way where the database name and port are different for debug mode.
