#!/bin/bash

# Check if the imdb-crawler Docker container is running
if [ $(docker ps -q -f name=imdb-crawler) ]; then
    echo "imdb-crawler Docker container is already running."
else
    # Start the imdb-crawler container if it is not running
    # Create shared_data folder if it doesn't exist
    mkdir -p $HOME/docker/shared_data
    cd $HOME/docker/imdb-crawler
    docker build -t imdb-crawler-python-app .
    # docker run -it --rm --network="host" --name imdb-crawler -v $HOME/docker/shared_data:/shared imdb-crawler-python-app
    docker run -d --rm --network="host" --name imdb-crawler -v $HOME/docker/shared_data:/shared imdb-crawler-python-app
    echo "imdb-crawler Docker container started."
fi
