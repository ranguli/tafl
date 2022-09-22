# TAFL Search
A web app for searching and exploring Canada's radio spectrum. Provides a frontend to the TAFL produced by Innovation, Science and Economic Development Canada.


## Deployment

```
datasette publish fly tafl.db --app="tafl-search" -m metadata.json --install=datasette-cluster-map --extra-options="--setting sql_time_limit_ms 10000 --setting facet_time_limit_ms 10000"
```
