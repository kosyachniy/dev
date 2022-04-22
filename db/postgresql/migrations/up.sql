CREATE TABLE "users" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "status" SMALLINT NOT NULL DEFAULT 3,
    "image" TEXT,
    "login" TEXT COLLATE "en_US" CHECK("login" ~ '\S+') UNIQUE,
    "name" TEXT COLLATE "en_US" CHECK("name" ~ '\S+'),
    "surname" TEXT COLLATE "en_US" CHECK("surname" ~ '\S+'),
    "mail" TEXT COLLATE "en_US" CHECK("mail" ~ '\S+') UNIQUE,
    "password" TEXT,
    "phone" INTEGER UNIQUE,
    "lang" TEXT NOT NULL DEFAULT 'ru' CHECK("lang" ~ '\S+'),
    "created" TIMESTAMP NOT NULL DEFAULT NOW(),
    "updated" TIMESTAMP NOT NULL DEFAULT NOW(),
    "extra" JSONB NOT NULL DEFAULT '{}'::JSONB
);
