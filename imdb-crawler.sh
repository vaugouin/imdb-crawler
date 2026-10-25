#!/bin/bash

# Switched off by off.sh, back on with on.sh: the flag file CRON_OFF next to this script makes
# every cron tick exit here. The script keeps its name, so the git clone stays clean.
if [ -f "$(dirname "$(readlink -f "$0")")/CRON_OFF" ]; then
    echo "CRON_OFF present: imdb-crawler switched off (bash on.sh to switch it back on)."
    exit 0
fi

# Check if the imdb-crawler Docker container is running
if [ $(docker ps -q -f name=imdb-crawler) ]; then
    echo "imdb-crawler Docker container is already running."
else
    # Start the imdb-crawler container if it is not running
    # Create shared_data folder if it doesn't exist
    mkdir -p $HOME/docker/shared_data/imdb-crawler
    cd $HOME/docker/imdb-crawler
    docker build -t imdb-crawler-python-app .
    # docker run -it --rm --network="host" --name imdb-crawler --env-file /home/debian/docker/imdb-crawler/.env -v $HOME/docker/shared_data/imdb-crawler:/shared imdb-crawler-python-app
    docker run -d --rm --network="host" --name imdb-crawler --env-file /home/debian/docker/imdb-crawler/.env -v $HOME/docker/shared_data/imdb-crawler:/shared imdb-crawler-python-app
    echo "imdb-crawler Docker container started."
fi
