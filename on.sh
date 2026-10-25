#!/bin/bash
# Switch imdb-crawler.sh back on: removes the flag file CRON_OFF that off.sh wrote.
cd "$(dirname "$(readlink -f "$0")")" || exit 1
# A launcher renamed by the old off.sh (<name>-off.sh, before 2026-10-25) is put back,
# or dropped when git has already restored the tracked one.
[ -f imdb-crawler-off.sh ] && { [ -f imdb-crawler.sh ] && rm -f imdb-crawler-off.sh || mv imdb-crawler-off.sh imdb-crawler.sh; }
rm -f CRON_OFF && echo "imdb-crawler: on (CRON_OFF removed)"
