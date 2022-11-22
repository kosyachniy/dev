# PostgreSQL
## Start
```
docker pull postgres
docker run --name mypsql -e POSTGRES_PASSWORD=password -e POSTGRES_DB=main -d -p 5432:5432 postgres
```

## Commands
```
docker exec -it mypsql psql -h localhost -p 5432 -U postgres
\c main
```

```
SET client_encoding = 'UTF8';
\timing
```

```
SET enable_seqscan = OFF;
```

* ` \? ` - Help
* ` \h <command> ` - Help with SQL command
* ` \l ` - List of databases
* ` \timing `
* ` \x auto `
* ` \dn `
* ` \dt ` - List of tables
* ` \d <table> ` - Scheme of table
* ` \c {[DBNAME|- USER|- HOST|- PORT|-]|conninfo} ` - Connect to
* ` \conninfo ` - Connection info
* ` \q ` - Quit

## Export / Import
```
pg_dump -h localhost -p 5432 -U postgres main > backup.db
psql -h localhost -p 5432 -U postgres main < backup.db
```

## Requests
* ` SELECT * FROM information_schema.tables; `


postgres//{user}:{password}@{host}:{port}/{db_name}?sslmode=require
