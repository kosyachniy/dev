# PostgreSQL
## Start
```
docker pull postgres
docker run --name mypsql -e POSTGRES_PASSWORD=password -d -p 5432:5432 postgres
docker exec -it mypsql bash
psql -h localhost -p 5432 -U postgres
```

## Commands
* ` help `
* ` \? `
* ` \l ` - List of databases
* ` \h <command> `
* ` \timing `
* ` \x auto `
* ` \dn `
* ` \dt `
* ` \d `
* ` \c {[DBNAME|- USER|- HOST|- PORT|-]|conninfo} `
* ` \conninfo `

## Requests
* ` SELECT * FROM information_schema.tables; `