CREATE TABLE "users" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "status" TEXT NOT NULL DEFAULT 'active',
    "image" TEXT,
    "login" TEXT COLLATE "en_US" CHECK("login" ~ '\S+') UNIQUE,
    "name" TEXT COLLATE "en_US" CHECK("name" ~ '\S+'),
    "surname" TEXT COLLATE "en_US" CHECK("surname" ~ '\S+'),
    "mail" TEXT COLLATE "en_US" CHECK("mail" ~ '\S+') UNIQUE,
    "password" TEXT,
    "phone" INTEGER UNIQUE,
    "lang" TEXT CHECK("lang" ~ '\S+'),
    "birthday" TIMESTAMP,
    "tags" TEXT[] NOT NULL DEFAULT ARRAY[]::TEXT[],
    "extra" JSONB NOT NULL DEFAULT '{}'::JSONB,
    "created" TIMESTAMP NOT NULL DEFAULT NOW(),
    "updated" TIMESTAMP NOT NULL DEFAULT NOW()
);
