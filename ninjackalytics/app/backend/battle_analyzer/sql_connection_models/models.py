from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


from poke_tool.config.config import db_uri
from poke_tool.backend.battle_analyzer.database_handler.battle_db_models import *
import pandas as pd

engine = create_engine(db_uri)
Session = sessionmaker(engine)


class Query:
    """
    The Query class is a base class for querying data from the database.
    """

    def __init__(self, battle_id: str):
        """
        Initializes the instance with the `battle_id` to be used for querying the data.

        Parameters:
        battle_id (str): The battle id to be used for querying data.
        """
        self.battle_id = battle_id
        self.table_id = self._get_table_id()

    def _get_table_id(self):
        """
        Get the table id from the database.
        """
        entity_cols = [battle_info.id]
        df = self._query_data(battle_info, entity_cols)
        return df.iloc[0]["id"]

    def _query_data(self, model, entity_cols):
        """
        Query the data from the database using the provided `model` and `entity_cols`.

        Parameters:
        model (model): The SQLAlchemy model to be used for querying the data.
        entity_cols (list): The columns to be retrieved from the database.

        Returns:
        df (pandas.DataFrame): The queried data in a pandas dataframe.
        """
        with Session.begin() as session:
            query = (
                session.query(model)
                .with_entities(*entity_cols)
                .filter_by(Battle_ID=self.table_id)
            )
            statement = query.statement
            df = pd.read_sql(statement, session.bind)
        return df

    def _get_player_data(self, df: pd.DataFrame, player_number: int, source_col: str):
        """
        Filter the dataframe to include only data for the specified player.

        Parameters:
        df (pandas.DataFrame): The dataframe to be filtered.
        player_number (int): The player number to be retrieved.
        source_col (str): The source column to be used for filtering.

        Returns:
        df (pandas.DataFrame): The filtered dataframe.
        """
        df = df[df[source_col].str.startswith(f"P{player_number}")]
        return df


class BattleInfo(Query):
    def __init__(self, battle_id: str):
        super().__init__(battle_id)

    def query_data(self):
        entity_cols = [
            battle_info.Battle_ID,
            battle_info.Format,
            battle_info.P1,
            battle_info.P2,
            battle_info.Rank,
            battle_info.Winner,
        ]
        return self._query_data(battle_info, entity_cols)


class Damages(Query):
    """
    Class for handling and processing damage data for a battle.

    This class inherits from the `Query` class and implements methods for
    retrieving raw damage data, renaming columns, and dividing damage data
    into player-specific data frames.
    """

    def __init__(self, battle_id: str):
        """
        Initialize an instance of the `Damages` class.

        Parameters
        ----------
        battle_id : str
            The ID of the battle to retrieve damage data for.
        """
        super().__init__(battle_id)

    def _get_raw_df(self):
        """
        Retrieve the raw damage data for the specified battle.

        Returns
        -------
        pd.DataFrame
            The raw damage data, with columns for damage, dealer, receiver,
            source name, turn, and type.
        """
        entity_cols = [
            damages.Damage,
            damages.Dealer,
            damages.Receiver,
            damages.Source_Name,
            damages.Turn,
            damages.Type,
        ]
        return self._query_data(damages, entity_cols)

    def _rename_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Rename columns in the damage data frame.

        Parameters
        ----------
        df : pd.DataFrame
            The raw damage dataframe to rename columns for.

        Returns
        -------
        pd.DataFrame
            The input dataframe with columns renamed to "Dmg_Source",
            "Dmg_Receiver", and "Dmg_Type".
        """
        df = df.rename(
            columns={
                "Source_Name": "Dmg_Source",
                "Receiver": "Dmg_Receiver",
                "Type": "Dmg_Type",
            }
        )
        return df

    def get_player_damage_taken_dfs(self) -> dict:
        """
        Divide the damage data into player-specific dataframes. We want to define
        the damage_taken_dfs for each player, which means we want all damage data
        related to the Receiver being the player who's df we are building.

        Returns
        -------
        dict
            A dictionary with keys "P1" and "P2", representing the damage dataframes
            for each player. Each dataframe has columns for turn,
            dealer, source, receiver, type, and amount(called "Damage").
        """
        raw_df = self._get_raw_df()
        renamed_df = self._rename_columns(raw_df)
        player_dfs = {
            f"P{x}": self._get_player_data(
                df=renamed_df, player_number=x, source_col="Dmg_Receiver"
            )
            for x in [1, 2]
        }
        return player_dfs

    def get_player_damage_dealt_dfs(self) -> dict:
        """
        Divide the damage data into player-specific dataframes. We want to define
        the damage_dealt_dfs for each player, which means we want all damage data
        related to the Receiver being the opposing player who's df we are building.


        Returns
        -------
        dict
            A dictionary with keys "P1" and "P2", representing the damage dataframes
            for each player. Each dataframe has columns for turn,
            dealer, source, receiver, type, and amount(called "Damage").
        """
        raw_df = self._get_raw_df()
        renamed_df = self._rename_columns(raw_df)
        player_dfs = {
            f"P{x}": self._get_player_data(
                df=renamed_df,
                player_number=[y for y in [1, 2] if y != x][
                    0
                ],  # opposite current player
                source_col="Dmg_Receiver",
            )
            for x in [1, 2]
        }
        return player_dfs


class Healing(Query):
    """
    Class for handling and processing healing data for a battle.

    This class inherits from the `Query` class and implements methods for
    retrieving raw healing data, renaming columns, and dividing healing data
    into player-specific data frames.
    """

    def __init__(self, battle_id: str):
        """
        Initialize an instance of the `Healing` class.

        Parameters
        ----------
        battle_id : str
            The ID of the battle to retrieve damage data for.
        """
        super().__init__(battle_id)

    def _get_raw_df(self):
        """
        Retrieve the raw healing data for the specified battle.

        Returns
        -------
        pd.DataFrame
            The raw healing data, with columns for healing, receiver,
            source name, turn, and type.
        """
        entity_cols = [
            healing.Healing,
            healing.Receiver,
            healing.Source_Name,
            healing.Turn,
            healing.Type,
        ]
        return self._query_data(healing, entity_cols)

    def _rename_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Rename columns in the healing data frame.

        Parameters
        ----------
        df : pd.DataFrame
            The raw healing dataframe to rename columns for.

        Returns
        -------
        pd.DataFrame
            The input dataframe with columns renamed to "Heal_Source",
            "Heal_Receiver", and "Heal_Type".
        """
        df = df.rename(
            columns={
                "Source_Name": "Heal_Source",
                "Receiver": "Heal_Receiver",
                "Type": "Heal_Type",
            }
        )
        return df

    def get_player_dfs(self) -> dict:
        """
        Divide the healing data into player-specific dataframes. The only purpose of
        this method is to handle the defining the correct source_col.

        Returns
        -------
        dict
            A dictionary with keys "P1" and "P2", representing the healing dataframes
            for each player. Each dataframe has columns for turn,
            dealer, source, receiver, type, and amount(called "Healing").
        """
        raw_df = self._get_raw_df()
        renamed_df = self._rename_columns(raw_df)
        player_dfs = {
            f"P{x}": self._get_player_data(
                df=renamed_df, player_number=x, source_col="Heal_Receiver"
            )
            for x in [1, 2]
        }
        return player_dfs


class Pivots(Query):
    """
    Class for handling and processing pivot data for a battle.

    This class inherits from the `Query` class and implements methods for
    retrieving raw pivot data, renaming columns, and dividing pivot data
    into player-specific data frames.
    """

    def __init__(self, battle_id: str):
        """
        Initialize an instance of the `Pivots` class.

        Parameters
        ----------
        battle_id : str
            The ID of the battle to retrieve damage data for.
        """
        super().__init__(battle_id)

    def _get_raw_df(self):
        """
        Retrieve the raw pivot data for the specified battle.

        Returns
        -------
        pd.DataFrame
            The raw pivot data, with columns for pokemon_enter,
            source name, and turn,
        """
        entity_cols = [
            pivots.Pokemon_Enter,
            pivots.Source_Name,
            pivots.Turn,
        ]
        return self._query_data(pivots, entity_cols)

    def _rename_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Rename columns in the pivots data frame.

        Parameters
        ----------
        df : pd.DataFrame
            The raw pivots dataframe to rename columns for.

        Returns
        -------
        pd.DataFrame
            The input dataframe with columns renamed to "Pivot_Source",
            "Heal_Receiver", and "Heal_Type".
        """
        df = df.rename(
            columns={
                "Source_Name": "Pivot_Source",
            }
        )
        return df

    def get_player_dfs(self) -> dict:
        """
        Divide the pivots data into player-specific dataframes. The only purpose of
        this method is to handle the defining the correct source_col.

        Returns
        -------
        dict
            A dictionary with keys "P1" and "P2", representing the pivots dataframes
            for each player. Each dataframe has columns for turn, source_name,
            and pokemon_enter.
        """
        raw_df = self._get_raw_df()
        renamed_df = self._rename_columns(raw_df)
        player_dfs = {
            f"P{x}": self._get_player_data(
                df=renamed_df, player_number=x, source_col="Pokemon_Enter"
            )
            for x in [1, 2]
        }
        return player_dfs


class Actions(Query):
    """
    Class for handling and processing action data for a battle.

    This class inherits from the `Query` class and implements methods for
    retrieving raw action data, renaming columns, and dividing action data
    into player-specific data frames.
    """

    def __init__(self, battle_id: str):
        """
        Initialize an instance of the `Actions` class.

        Parameters
        ----------
        battle_id : str
            The ID of the battle to retrieve damage data for.
        """
        super().__init__(battle_id)

    def _get_raw_df(self):
        """
        Retrieve the raw action data for the specified battle.

        Returns
        -------
        pd.DataFrame
            The raw action data, with columns for player_number,
            action, and turn,
        """
        entity_cols = [
            actions.Action,
            actions.Turn,
            actions.Player_Number,
        ]
        return self._query_data(actions, entity_cols)

    def get_player_dfs(self) -> dict:
        """
        Divide the actions data into player-specific dataframes. The only purpose of
        this method is to handle the defining the correct source_col.

        Returns
        -------
        dict
            A dictionary with keys "P1" and "P2", representing the actions dataframes
            for each player. Each dataframe has columns for turn, player_number,
            and action.
        """
        raw_df = self._get_raw_df()
        player_dfs = {
            f"P{x}": self._get_player_data(
                df=raw_df, player_number=x, source_col="Player_Number"
            )
            for x in [1, 2]
        }
        return player_dfs

    def _get_player_data(self, df: pd.DataFrame, player_number: int, source_col: str):
        """
        Filter the dataframe to include only data for the specified player. The Actions
        columns are organized differently than the other models and thus we need to
        overwrite the parent method for geting a specific player's data.

        Parameters:
        df (pandas.DataFrame): The dataframe to be filtered.
        player_number (int): The player number to be retrieved.
        source_col (str): The source column to be used for filtering.

        Returns:
        df (pandas.DataFrame): The filtered dataframe.
        """
        df = df[df[source_col].str.startswith(f"{player_number}")]
        return df


class BattleData:
    """
    A class for retrieving and processing battle data for a specific battle ID.

    This class creates instances of other classes for each type of data:
    BattleInfo, Damages, Healing, Pivots, and Actions, and then uses the
    get_player_dfs method to retrieve player-specific dataframes.
    """

    def __init__(self, battle_id: str) -> None:
        """
        Initialize an instance of the `BattleData` class.

        Parameters
        ----------
        battle_id : str
            The ID of the battle to retrieve data for.
        """
        self.battle_id = battle_id
        self.battle_info = self._get_battle_info()
        if self.battle_info:
            self.player_damages_dealt = self._get_damages_dealt_player_dfs()
            self.player_damages_taken = self._get_damages_taken_player_dfs()
            self.player_healing = self._get_healing_player_dfs()
            self.player_pivots = self._get_pivots_player_dfs()
            self.player_actions = self._get_actions_player_dfs()
            self.winner = self._determine_winner()
            self._update_player_dfs()
            self.hp_discrepancy_df = self.create_hp_discrepancy_df()

    def _get_battle_info(self) -> pd.DataFrame:
        """
        Retrieve the battle information for the specified battle.

        Returns
        -------
        pd.DataFrame
            A dataframe with information about the battle.
        """
        BattleInfoObj = BattleInfo(self.battle_id)
        return BattleInfoObj.query_data()

    def _get_damages_dealt_player_dfs(self) -> dict:
        """
        Retrieve player-specific damage data for the specified battle.

        Returns
        -------
        dict
            A dictionary with keys "P1" and "P2", representing the damage dealt
            dataframes for each player.
        """
        DamagesObj = Damages(self.battle_id)
        return DamagesObj.get_player_damage_dealt_dfs()

    def _get_damages_taken_player_dfs(self) -> dict:
        """
        Retrieve player-specific damage data for the specified battle.

        Returns
        -------
        dict
            A dictionary with keys "P1" and "P2", representing the damage taken
            dataframes for each player.
        """
        DamagesObj = Damages(self.battle_id)
        return DamagesObj.get_player_damage_taken_dfs()

    def _get_healing_player_dfs(self) -> dict:
        """
        Retrieve player-specific healing data for the specified battle.

        Returns
        -------
        dict
            A dictionary with keys "P1" and "P2", representing the healing dataframes
            for each player.
        """
        HealingObj = Healing(self.battle_id)
        return HealingObj.get_player_dfs()

    def _get_actions_player_dfs(self) -> dict:
        """
        Retrieve player-specific action data for the specified battle.

        Returns
        -------
        dict
            A dictionary with keys "P1" and "P2", representing the actions dataframes
            for each player.
        """
        ActionsObj = Actions(self.battle_id)
        return ActionsObj.get_player_dfs()

    def _get_pivots_player_dfs(self):
        """
        Retrieve player-specific pivot data for the specified battle.

        Returns
        -------
        dict
            A dictionary with keys "P1" and "P2", representing the pivot dataframes
            for each player.
        """
        PivotsObj = Pivots(self.battle_id)
        return PivotsObj.get_player_dfs()

    def _determine_winner(self):
        """
        This method determines the winner of the battle by comparing the winner in the
        battle_info attribute with the values of P1 and P2.

        Returns
        -------
            str: "P1" or "P2" depending on who is the winner. If there is no winner specified
            in the battle_info attribute, it returns "P1".

        We return P1 in the event of a tie, which will cause our %HP discrepancy display
        to have P1 as the positive direction and P2 as the negative. In a battle with a
        winner, the winner will be displayed as the positive %HP discrepancy direction
        and the loser will be displayed as the negative.
        """
        winner = self.battle_info["Winner"]

        if self.battle_info["P1"].eq(winner).any():
            return "P1"
        elif self.battle_info["P2"].eq(winner).any():
            return "P2"
        else:
            return "P1"

    def _update_player_dfs(self):
        """
        The purpose of this method is to update the keys of our various player dfs to
        reflect "winner" or "loser". This will allow easier handling of the ordering
        of the information displayed. Winners will be considered a positive %HP
        discrepancy and will always have their stats displayed on the left. Losers will
        be the negative %HP discrepancy and will have their stats displayed on the
        right.
        """
        winner = self._determine_winner()
        loser = "P1" if winner == "P2" else "P2"
        self.player_damages_dealt["winner"] = self.player_damages_dealt.pop(winner)
        self.player_damages_dealt["loser"] = self.player_damages_dealt.pop(loser)
        self.player_damages_taken["winner"] = self.player_damages_taken.pop(winner)
        self.player_damages_taken["loser"] = self.player_damages_taken.pop(loser)
        self.player_healing["winner"] = self.player_healing.pop(winner)
        self.player_healing["loser"] = self.player_healing.pop(loser)
        self.player_actions["winner"] = self.player_actions.pop(winner)
        self.player_actions["loser"] = self.player_actions.pop(loser)
        self.player_pivots["winner"] = self.player_pivots.pop(winner)
        self.player_pivots["loser"] = self.player_pivots.pop(loser)

    def create_hp_discrepancy_df(self):
        """
        Create a dataframe of HP discrepancies for each player's damage and healing details.

        Returns
        -------
        hp_discrepancy_df : pandas.DataFrame
            A dataframe containing the following columns:
            - Turn: the turn number of the event
            - Dmg_Dealer: the player's pokemon who dealt damage (for damage events only)
            - Damage: the amount of damage dealt (for damage events only)
            - Dmg_Type: the type of damage dealt (for damage events only)
            - Heal_Receiver: the player's pokemon who received healing (for healing
              events only)
            - Healing: the amount of healing received (for healing events only)
            - Heal_Type: the type of healing received (for healing events only)
            - %HP Discrepancy Change: the percentage change in the discrepancy of
              overall %HP between the winner and the loser (where + = more favorable
              to the winner)
        """
        hp_discrepancy_df = pd.concat(
            [
                self._create_hp_discrepancy_line(kwargs)
                for kwargs in self._yield_hp_discrepancy_kwargs()
            ],
            ignore_index=True,
        )
        return hp_discrepancy_df

    def _yield_hp_discrepancy_kwargs(self):
        """
        Generate dictionaries of HP discrepancy information for each player's damage and
        healing events.

        Yields
        ------
        kwargs : dict
            A dictionary containing the following keys:
            - Turn: the turn number of the event
            - Dmg_Dealer: the player's pokemon who dealt damage (for damage events only)
            - Damage: the amount of damage dealt (for damage events only)
            - Dmg_Type: the type of damage dealt (for damage events only)
            - Heal_Receiver: the player's pokemon who received healing (for healing
              events only)
            - Healing: the amount of healing received (for healing events only)
            - Heal_Type: the type of healing received (for healing events only)
        """
        for player, damage_df in self.player_damages_dealt.items():
            for _, damage_row in damage_df.iterrows():
                kwargs = {
                    "Turn": damage_row["Turn"],
                    "Dmg_Dealer": damage_row["Dmg_Dealer"],
                    "Damage": damage_row["Damage"],
                    "Dmg_Type": damage_row["Dmg_Type"],
                    "Dmg_Receiver": damage_row["Dmg_Receiver"],
                }
                yield kwargs

        for player, healing_df in self.player_healing.items():
            for _, healing_row in healing_df.iterrows():
                kwargs = {
                    "Turn": healing_row["Turn"],
                    "Heal_Receiver": healing_row["Heal_Receiver"],
                    "Healing": healing_row["Healing"],
                    "Heal_Type": healing_row["Heal_Type"],
                }
                yield kwargs

    def _create_hp_discrepancy_line(self, kwargs: dict):
        """
        Create a Pandas DataFrame with HP discrepancy information based on the input
        arguments.

        Parameters
        ----------
        kwargs : dict
            A dictionary containing the following keys:
            - Turn: the turn number of the event
            - Dmg_Dealer: the player's pokemon who dealt damage (for damage events only)
            - Damage: the amount of damage dealt (for damage events only)
            - Dmg_Type: the type of damage dealt (for damage events only)
            - Heal_Receiver: the player's pokemon who received healing (for healing
            events only)
            - Healing: the amount of healing received (for healing events only)
            - Heal_Type: the type of healing received (for healing events only)

        Returns
        -------
        return_df : pandas.DataFrame or None
            A pandas DataFrame containing the following columns:
            - Turn: the turn number of the event
            - Dmg_Dealer: the player's pokemon who dealt damage (for damage events only)
            - Damage: the amount of damage dealt (for damage events only)
            - Dmg_Type: the type of damage dealt (for damage events only)
            - Heal_Receiver: the player's pokemon who received healing (for healing
            events only)
            - Healing: the amount of healing received (for healing events only)
            - Heal_Type: the type of healing received (for healing events only)
            - %HP Discrepancy Change: the percentage change in the discrepancy of
            overall %HP between the winner and the loser (where + = more favorable
            to the winner). If all values in the dictionary are `pd.NA`, then
            this function returns `None`.
        """
        all_keywords = [
            "Turn",
            "Dmg_Dealer",
            "Damage",
            "Dmg_Type",
            "Heal_Receiver",
            "Healing",
            "Heal_Type",
        ]
        add_dict = {k: kwargs.get(k, pd.NA) for k in all_keywords}

        if "Damage" in kwargs:
            damage_sign = -1 if kwargs["Dmg_Receiver"].startswith(self.winner) else 1
            add_dict["%HP Discrepancy Change"] = float(kwargs["Damage"]) * damage_sign
        elif "Healing" in kwargs:
            healing_sign = 1 if kwargs["Heal_Receiver"].startswith(self.winner) else -1
            add_dict["%HP Discrepancy Change"] = float(kwargs["Healing"]) * healing_sign

        return pd.DataFrame(add_dict, index=[0])
