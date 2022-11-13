# this file maintains what generations and formats the auto running replay puller is using to feed itself

GENERATIONS = ["gen6"]
FORMATS = [
    "ou",
    "doublesou",
    "randombattle",
    "ubers",
    "randomdoublesbattle",
    "bdspou",
    "bdspdoublesou",
]

ERROR_RETURN_DIC = {
    "Pokemon_Enter": "Something went wrong",
    "Source_Name": "Something went wrong",
    "Healing": 0,
    "Damage": 0,
    "Receiver": "Something went wrong",
    "Type": "Something went wrong",
    "Dealer": "Something went wrong",
    "Player_Number": 121212121212,
    "Action": "Something went wrong",
}
