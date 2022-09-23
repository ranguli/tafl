#!/usr/bin/env bash

cd ../tafl/
poetry export -f requirements.txt -o requirements.txt
datasette publish fly tafl.db --app="tafl-search" -m metadata.json --install=datasette-cluster-map --extra-options="--setting sql_time_limit_ms 10000 --setting facet_time_limit_ms 10000 --setting allow_download off --setting allow_csv_stream off"
