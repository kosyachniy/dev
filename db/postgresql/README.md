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

## Requests
* ` SELECT * FROM information_schema.tables; `
