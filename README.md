# IMDb Crawler

A Python script that automatically downloads and imports IMDb dataset files into a MySQL database for data analysis and processing.

## Overview

The `imdb-crawler.py` script is designed to:
- Download the latest IMDb dataset files from the official IMDb datasets website
- Extract and process the compressed TSV files
- Import the data into corresponding MySQL database tables
- Track processing status and maintain import history

## Features

### Automated Daily Processing
- Checks if new data is available (compares against yesterday's date)
- Only processes data if it's newer than the last successful import
- Maintains execution logs and status tracking

### Data Sources
The script downloads and processes 7 different IMDb dataset files:

1. **title.ratings** - Movie/TV show ratings data
2. **title.basics** - Basic title information (title, year, genre, etc.)
3. **title.akas** - Alternative titles and localized names
4. **title.principals** - Principal cast and crew information
5. **name.basics** - Person information (actors, directors, etc.)
6. **title.episode** - TV series episode information
7. **title.crew** - Crew information for titles

### Database Integration
Each dataset is imported into corresponding MySQL tables:
- `T_WC_IMDB_MOVIE_RATING_IMPORT` - Ratings data
- `T_WC_IMDB_MOVIE_BASIC_IMPORT` - Basic title information
- `T_WC_IMDB_MOVIE_AKA_IMPORT` - Alternative titles
- `T_WC_IMDB_MOVIE_PRINCIPAL_IMPORT` - Principal cast/crew
- `T_WC_IMDB_PERSON_BASIC_IMPORT` - Person information
- `T_WC_IMDB_SERIE_EPISODE_IMPORT` - Episode data
- `T_WC_IMDB_PERSON_MOVIE_IMPORT` - Crew information

## Processing Workflow

### 1. Initialization
- Sets up timezone (Paris timezone)
- Calculates yesterday's date for file availability
- Retrieves previous execution status from server variables
- Initializes tracking variables

### 2. Date Validation
- Compares current date with last successful import date
- Only proceeds if new data is available

### 3. File Processing Loop
For each IMDb dataset file:
1. **Download**: Retrieves compressed TSV file from `https://datasets.imdbws.com/`
2. **Extract**: Decompresses the .gz file to .tsv format
3. **Import**: Loads data into MySQL using optimized bulk import
4. **Cleanup**: Removes temporary files

### 4. Database Import Optimization
The script uses several MySQL optimizations for faster imports:
- Disables autocommit, unique checks, and foreign key checks
- Disables table keys during import
- Uses `LOAD DATA INFILE` for bulk insertion
- Re-enables all checks and commits after import

### 5. Status Tracking
- Records start/end timestamps
- Tracks current processing step
- Maintains list of successfully processed files
- Stores last successful import date

## Setup Instructions

### 1. Database Setup
Before running the crawler, you must create the required MySQL/MariaDB tables using the provided SQL script:

```bash
mysql -u your_username -p your_database < IMDb-tables.sql
```

This script creates all the necessary import tables:
- `T_WC_IMDB_MOVIE_RATING_IMPORT`
- `T_WC_IMDB_MOVIE_BASIC_IMPORT`
- `T_WC_IMDB_MOVIE_AKA_IMPORT`
- `T_WC_IMDB_MOVIE_PRINCIPAL_IMPORT`
- `T_WC_IMDB_PERSON_BASIC_IMPORT`
- `T_WC_IMDB_SERIE_EPISODE_IMPORT`
- `T_WC_IMDB_PERSON_MOVIE_IMPORT`

### 2. Configuration File Setup
Copy the example environment file and update it with your actual credentials:

```bash
cp .env.example .env
```

Then edit `.env` and replace the placeholder values with your actual:
- **MariaDB/MySQL credentials**: host, port, username, password, database name
- **Timezone**: Update if different from Europe/Paris

> **Security note:** `.env` is listed in both `.gitignore` and `.dockerignore`, so it is excluded from the git repository and from the Docker build context. Never commit `.env` and never `COPY` it into the image — see the [Docker usage](#docker-usage) section below for how secrets are injected at runtime.

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## Docker Usage

The image must be built **without** secrets baked in. The `Dockerfile` only ships the application code and non-sensitive defaults; the `.env` file is excluded from the build context by `.dockerignore`. At runtime, secrets are supplied with Docker's `--env-file` option, pointing at a host-managed env file that lives **outside** the application source tree.

### Build

```bash
docker build -t imdb-crawler-python-app .
```

### Run

```bash
docker run -d --rm \
    --network="host" \
    --name imdb-crawler \
    --env-file /home/debian/docker/imdb-crawler/.env \
    -v $HOME/docker/shared_data:/shared \
    imdb-crawler-python-app
```

Key points:
- `--env-file /home/debian/docker/imdb-crawler/.env` injects the database credentials and other environment variables at container start time. Adjust the path to wherever the env file lives on your host.
- The env file is **not** copied into the image, is not part of any image layer or build cache, and is not pushed to any registry.
- The Dockerfile does not `COPY .env` and does not declare secrets in `ENV` lines. Only non-sensitive defaults belong in the image.
- The provided helper script [`imdb-crawler.sh`](imdb-crawler.sh) already uses `--env-file` and can be used to build and start the container in one step.

## Dependencies

```python
import time
import requests
import pymysql.cursors
import json
import citizenphil as cp  # Custom module for database connections and utilities
from datetime import datetime, timedelta
import gzip
import shutil
import csv
import os
```

## Configuration Requirements

- **Database**: MySQL/MariaDB database with pre-created import tables (use `IMDb-tables.sql`)
- **File System**: Write access to `/shared/` directory for temporary files
- **Network**: Internet access to download from `datasets.imdbws.com`
- **Custom Module**: `citizenphil` module for database connections and server variables
- **API Access**: TMDb API key and token for additional movie data

## Error Handling

- MySQL connection errors are caught and logged
- Failed downloads prevent the import date from being updated
- Rollback functionality for database transactions
- Process status tracking for monitoring and debugging

## File Management

- Downloads files to `/shared/` directory
- Automatically removes compressed files after extraction
- Automatically removes TSV files after database import
- Maintains clean temporary file space

## Monitoring

The script provides several monitoring capabilities:
- Current process status tracking
- Execution history
- Import timestamps for each dataset
- Success/failure status for each run

## Usage

The script is designed to run automatically (e.g., via cron job) and will:
1. Check if new data is available
2. Download and process only if needed
3. Update tracking variables upon completion
4. Log all activities for monitoring

## Data Freshness

IMDb datasets are typically updated daily, and the script ensures you always have the most recent data available by checking against yesterday's date before processing.
