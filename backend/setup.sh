#!/bin/bash

# Local setup script for Debian/Ubuntu based distros
# Before running, ensure that Python 3.12 & pip3 are installed

env_name="frugality_env"
python_path="/usr/bin/python3.12"
postgres_user="frugality_user"
postgres_password="pleasechangethispassword"
postgres_db="test_database"
postgres_port=5432

# Create a .env file with default environment variables
echo "Setting up dev environment..."
echo "POSTGRES_USER=$postgres_user" > .env
echo "POSTGRES_PASSWORD=$postgres_password" >> .env
echo "POSTGRES_DB=$postgres_db" >> .env
echo "POSTGRES_PORT=$postgres_port" >> .env
echo "Created .env file with default values. Please remember to edit it with the appropriate values."


# Install [virtualenv] if not already present
if ! [ "$(pip3 list | grep -F virtualenv)" ]; then
    echo "Installing 'virtualenv' package..."
    command pip3 install virtualenv
else
    echo "Package 'virtualenv' is already installed. Skipping package install step..."
fi

if ! [ -d frugality_env ]; then
    echo "Directory '$env_name' does not exist. Creating virtualenv with name: '$env_name'..."
    command virtualenv $env_name --python=$python_path
else
    echo "Directory '$env_name' already exists. Skipping creation of new virtual environment..."
fi

if ! [ -e "./$env_name/bin/activate" ]; then
    echo "Unable to locate env activation script inside '$env_name'. Aborting setup..."
    exit
fi

echo "Activating Python virtual environment..."
command source ./$env_name/bin/activate
echo "Installing project requirements..."
command pip install -r requirements.txt
echo "Project setup complete."