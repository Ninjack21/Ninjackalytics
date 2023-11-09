import re


class Pokemon:
    def __init__(
        self, real_name: str, nickname: str, player_num: str, hp=100, hp_change=None
    ):
        self.real_name = self._handle_real_name(real_name)
        self.nickname = nickname
        self.player_num = int(player_num)
        self.hp = hp
        self.hp_change = hp_change

    def _handle_real_name(self, real_name: str) -> str:
        """
        Returns a str with the real name of the pokemon before the first
        comma

        Parameters
        ----------
        real_name : str
            The real name of the pokemon

        Returns
        -------
        str
            The real name of the pokemon before the first comma

        """
        return real_name.split(",")[0]

    def __hash__(self):
        return hash((self.real_name, self.player_num))

    def __eq__(self, other: object):
        """
        Defines how a Pokemon object is considered equal to another Pokemon object

        When the real_name and player_num of the two Pokemon objects are the same then the
        objects are considered equal
        """
        return (
            self.__class__ == other.__class__
            and self.real_name == other.real_name
            and self.player_num == other.player_num
        )

    def update_hp(self, new_hp: float) -> None:
        """
        Updates the hp_change and hp stat of the object

        Parameters
        ----------
        new_hp : float
            A float that represents the new hp of the Pokemon
        """
        self.hp_change = new_hp - self.hp
        self.hp = new_hp

    @property
    def get_hp(self):
        return self.hp

    @property
    def get_hp_change(self) -> float:
        return self.hp_change

    def check_if_name_is_self(self, name: str) -> bool:
        """
        Checks a provided raw_name and returns True if it refers to self and False if it does not.

        Paramters
        ---------
        name : str
            The raw name found in the log

        Returns
        -------
        bool
            True if the provided raw_name refers to self and False if it does not.

        Example:
        name = p1a: Espeon
        prefix = the p1[a-d] part (== "p1a" here)
        player_num = prefix[1], i.e. the second character of the prefix, here 1
        """
        prefix = re.findall("[p][1-2][a-z]*: ", name)[0]
        player_num = int(prefix[1])
        name = name.split(prefix)[1]

        if player_num == self.player_num and name == self.nickname:
            return True
        else:
            return False
