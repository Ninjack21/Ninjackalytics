CREATE TABLE IF NOT EXISTS battle_info
(
    "Battle_ID" text COLLATE pg_catalog."default" NOT NULL,
    "Date_Submitted" date NOT NULL,
    "Format" text COLLATE pg_catalog."default" NOT NULL,
    "Player" text COLLATE pg_catalog."default" NOT NULL,
    "Rank" integer,
    "Private" boolean NOT NULL,
    "Winner" text COLLATE pg_catalog."default" NOT NULL
);

CREATE TABLE IF NOT EXISTS actions
(
    "Battle_ID" text COLLATE pg_catalog."default" NOT NULL,
    "Turn" integer NOT NULL,
    "Player" text COLLATE pg_catalog."default" NOT NULL,
    "Action" text COLLATE pg_catalog."default" NOT NULL
);

CREATE TABLE IF NOT EXISTS damage
(
    "Battle_ID" text COLLATE pg_catalog."default" NOT NULL,
    "Turn" integer NOT NULL,
    "Dealer" text COLLATE pg_catalog."default" NOT NULL,
    "Name" text COLLATE pg_catalog."default" NOT NULL,
    "Receiver" text COLLATE pg_catalog."default" NOT NULL,
    "Damage" numeric(5,2) NOT NULL,
    "Type" text COLLATE pg_catalog."default" NOT NULL
);

CREATE TABLE IF NOT EXISTS healing
(
    "Battle_ID" text COLLATE pg_catalog."default" NOT NULL,
    "Turn" integer NOT NULL,
    "Name" text COLLATE pg_catalog."default" NOT NULL,
    "Receiver" text COLLATE pg_catalog."default" NOT NULL,
    "Recovery" numeric(5,2) NOT NULL,
    "Type" text COLLATE pg_catalog."default"
);

CREATE TABLE IF NOT EXISTS switch
(
    "Battle_ID" text COLLATE pg_catalog."default" NOT NULL,
    "Turn" integer NOT NULL,
    "Player" text COLLATE pg_catalog."default" NOT NULL,
    "Pokemon_Enter" text COLLATE pg_catalog."default" NOT NULL,
    "Source" text COLLATE pg_catalog."default" NOT NULL
);

CREATE TABLE IF NOT EXISTS team
(
    "Battle_ID" text COLLATE pg_catalog."default" NOT NULL,
    "Player" text COLLATE pg_catalog."default" NOT NULL,
    "Pokemon" text COLLATE pg_catalog."default" NOT NULL
);

CREATE TABLE IF NOT EXISTS unique_battle_ids
(
    "Battle_ID" text COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT "Unique_Battle_IDs_pkey" PRIMARY KEY ("Battle_ID")
);

CREATE TABLE IF NOT EXISTS errors
(
    "Battle_ID" text COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT "errors_pkey" PRIMARY KEY ("Battle_ID"),
    "Date" date NOT NULL,
    "Func_Name" text COLLATE pg_catalog."default" NOT NULL,
    "Current_Step" text COLLATE pg_catalog."default" NOT NULL,
    "Parameters" text COLLATE pg_catalog."default",
    "Error_Message" text COLLATE pg_catalog."default"
);