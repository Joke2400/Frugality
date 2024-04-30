#!/bin/bash

# Check for Python 3.12 installation
if ! command -v python3.12 >/dev/null 2>&1; then
    echo "Python 3.12 is not installed. Python 3.12 is a prerequisite for this project."
    exit 1
fi
echo "Verified Python 3.12 installation."
# Check for pip3 installation
if ! command -v pip3 >/dev/null 2>&1; then
    echo "pip3 is not installed. pip3 is a prerequisite for this script."
    exit 1
fi
echo "Verified pip3 installation."
# Check for virtualenv package installation
if ! command -v virtualenv >/dev/null 2>&1; then
    read -r -n 1 -p "The Python package 'virtualenv' is not installed. Do you want to install it (y/n)?"
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "User indicated that package install should not occur."
        echo "Terminating script ..."
        exit 1
    fi
    command pip3 install virtualenv
    # Verify success of installation
    if ! command -v virtualenv >/dev/null 2>&1; then
        echo "Package 'virtualenv' install was not successful."
        echo "Terminating script ..."
        exit 1
    fi
fi
echo "Script prerequisites verified as installed on current system."
echo "---------------------------------------"

ENV_NAME="frugality-env"
PYTHON_PATH="/usr/bin/python3.12"
read -r -p "Please enter a name for the PostgreSQL user: " postgres_user
read -s -r -p "Please enter a password for the PostgreSQL user: " postgres_pass
echo
echo "---------------------------------------"
echo "Creating .env files at: '$PWD/env' ..."
if ! [ -d "./env" ]; then
    echo "Could not find directory 'env' in $PWD. Creating directory..."
    sudo mkdir env
    sudo chown $USER:$USER env
fi


# Create prod.env
echo "POSTGRES_USER=$postgres_user" > ./env/prod.env
echo "POSTGRES_PASSWORD=$postgres_pass" >> ./env/prod.env
echo "POSTGRES_PORT=5432">> ./env/prod.env
echo "POSTGRES_DB=frugality_database" >> ./env/prod.env
echo "DEBUG=False" >> ./env/prod.env

# Create dev.env
echo "POSTGRES_USER=$postgres_user" > ./env/dev.env
echo "POSTGRES_PASSWORD=$postgres_pass" >> ./env/dev.env
echo "POSTGRES_PORT=5433" >> ./env/dev.env
echo "POSTGRES_DB=test_database" >> ./env/dev.env
echo "DEBUG=True" >> ./env/dev.env


if ! [ -e "./backend/$ENV_NAME/bin/activate" ]; then
    echo "Unable to locate virtualenv activation script at: '$PWD/backend/$ENV_NAME/bin/activate'"
    echo "Creating virtualenv at: $PWD/backend/$ENV_NAME/bin/activate"
    command virtualenv ./backend/$ENV_NAME --python=$PYTHON_PATH
fi
if ! [ -e "./backend/$ENV_NAME/bin/activate" ]; then
    echo "Unable to locate virtualenv activation script at: '$PWD/backend/$ENV_NAME/bin/activate'"
    echo "Terminating script ..."
    exit 1
fi
echo "Activating the virtualenv at: '$PWD/backend/$ENV_NAME/bin/activate' ..."
command source ./backend/$ENV_NAME/bin/activate
echo "---------------------------------------"
echo "Installing items specified in 'requirements.txt' ..."
command pip install -r ./backend/requirements.txt
echo "---------------------------------------"
echo "Project setup complete."
