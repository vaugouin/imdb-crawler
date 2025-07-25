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

- **Database**: MySQL database with pre-created import tables
- **File System**: Write access to `/shared/` directory for temporary files
- **Network**: Internet access to download from `datasets.imdbws.com`
- **Custom Module**: `citizenphil` module for database connections and server variables

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
