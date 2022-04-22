# PostgreSQL
## Start
```
docker pull postgres
docker run --name mypsql -e POSTGRES_PASSWORD=password -d -p 5432:5432 postgres
docker exec -it mypsql bash
psql -h localhost -p 5432 -U postgres
CREATE DATABASE main;
```

## Commands
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
