CREATE OR REPLACE VIEW "dmg_heal_turns_union" as 
SELECT "Turn", "Battle_ID" 
FROM damage
UNION
SELECT "Turn", "Battle_ID"
FROM healing
ORDER BY "Turn";

CREATE OR REPLACE VIEW "org_dmg" as
SELECT u."Turn", u."Battle_ID", d."Dealer", d."Name", d."Receiver", d."Damage", d."Type"
FROM dmg_heal_turns_union u
FULL OUTER JOIN damage d
ON u."Battle_ID" = d."Battle_ID" and u."Turn" = d."Turn"
ORDER BY "Turn";

CREATE OR REPLACE VIEW "battle_stats_compiled" as 
SELECT o."Turn", o."Battle_ID", o."Dealer" as Dmg_Dealer, o."Name" as Dmg_Source_Name, o."Receiver" as Dmg_Receiver,
o."Damage", o."Type" as Dmg_Type, h."Recovery", h."Receiver" as Heal_Receiver, h."Type" as Heal_Type, h."Name" as Heal_Source_Name
FROM org_dmg o
FULL OUTER JOIN healing h
ON o."Battle_ID" = h."Battle_ID" AND o."Turn" = h."Turn"
ORDER BY "Turn", "Battle_ID"
;

select * 
FROM battle_stats_compiled;