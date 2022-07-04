CREATE TABLE IF NOT EXISTS Battle_Info
(
    "Battle_ID" text COLLATE pg_catalog."default" NOT NULL,
    "Date_Submitted" date NOT NULL,
    "Format" text COLLATE pg_catalog."default" NOT NULL,
    "Player" text COLLATE pg_catalog."default" NOT NULL,
    "Rank" integer,
    "Private" boolean NOT NULL,
    "Winner" text COLLATE pg_catalog."default" NOT NULL
);

CREATE TABLE IF NOT EXISTS Actions
(
    "Battle_ID" text COLLATE pg_catalog."default" NOT NULL,
    "Turn" integer NOT NULL,
    "Player" text COLLATE pg_catalog."default" NOT NULL,
    "Action" text COLLATE pg_catalog."default" NOT NULL
);

CREATE TABLE IF NOT EXISTS Damage
(
    "Battle_ID" text COLLATE pg_catalog."default" NOT NULL,
    "Turn" integer NOT NULL,
    "Dealer" text COLLATE pg_catalog."default" NOT NULL,
    "Name" text COLLATE pg_catalog."default" NOT NULL,
    "Receiver" text COLLATE pg_catalog."default" NOT NULL,
    "Damage" numeric(5,2) NOT NULL,
    "Type" text COLLATE pg_catalog."default" NOT NULL
);

CREATE TABLE IF NOT EXISTS Healing
(
    "Battle_ID" text COLLATE pg_catalog."default" NOT NULL,
    "Turn" integer NOT NULL,
    "Name" text COLLATE pg_catalog."default" NOT NULL,
    "Receiver" text COLLATE pg_catalog."default" NOT NULL,
    "Recovery" numeric(5,2) NOT NULL,
    "Type" text COLLATE pg_catalog."default"
);

CREATE TABLE IF NOT EXISTS Switch
(
    "Battle_ID" text COLLATE pg_catalog."default" NOT NULL,
    "Turn" integer NOT NULL,
    "Player" text COLLATE pg_catalog."default" NOT NULL,
    "Pokemon_Enter" text COLLATE pg_catalog."default" NOT NULL,
    "Source" text COLLATE pg_catalog."default" NOT NULL
);

CREATE TABLE IF NOT EXISTS Team
(
    "Battle_ID" text COLLATE pg_catalog."default" NOT NULL,
    "Player" text COLLATE pg_catalog."default" NOT NULL,
    "Pokemon" text COLLATE pg_catalog."default" NOT NULL
);

CREATE TABLE IF NOT EXISTS Unique_Battle_IDs
(
    "Battle_ID" text COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT "Unique_Battle_IDs_pkey" PRIMARY KEY ("Battle_ID")
);
