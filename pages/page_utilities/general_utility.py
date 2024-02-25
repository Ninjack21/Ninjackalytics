import os
import difflib
import random
from ninjackalytics.services.database_interactors.table_accessor import (
    TableAccessor,
    session_scope,
)
from ninjackalytics.database.models import battle_info
from sqlalchemy import func


def _get_sprites():
    current_dir = os.path.dirname(__file__)
    while current_dir != "/":
        if os.path.basename(current_dir) == "Ninjackalytics":
            break
        current_dir = os.path.dirname(current_dir)

    sprite_dir = os.path.join(current_dir, "assets/showdown_sprites")
    sprites = os.listdir(sprite_dir)
    gifs = [sprite.split(".gif")[0] for sprite in sprites if sprite.endswith(".gif")]
    pngs = [sprite.split(".png")[0] for sprite in sprites if sprite.endswith(".png")]
    return sprite_dir, gifs, pngs


def _return_sprite_path(sprite_dir, sprite):
    return os.path.join(sprite_dir, sprite).split("Ninjackalytics")[-1]


def find_closest_sprite(name):
    sprite_dir, gifs, pngs = _get_sprites()
    name = name.lower()

    # First, look for an exact match in gifs
    if name in gifs:
        name = name + ".gif"
        return _return_sprite_path(sprite_dir, name)

    # now look for an exact match in pngs
    if name in pngs:
        name = name + ".png"
        return _return_sprite_path(sprite_dir, name)

    # Otherwise, find the closest match or subset in gifs
    closest_match = difflib.get_close_matches(name, gifs, n=1)
    if closest_match:
        closest_match = closest_match[0] + ".gif"
        return _return_sprite_path(sprite_dir, closest_match)
    else:
        for sprite in gifs:
            if name.lower() in sprite.lower():
                sprite = sprite + ".gif"
                return _return_sprite_path(sprite_dir, sprite)

    # Otherwise, find the closest match or subset in pngs
    closest_match = difflib.get_close_matches(name, pngs, n=1)
    if closest_match:
        closest_match = closest_match[0] + ".png"
        return _return_sprite_path(sprite_dir, closest_match)
    else:
        for sprite in pngs:
            if name.lower() in sprite.lower():
                sprite = sprite + ".png"
                return _return_sprite_path(sprite_dir, sprite)

    return None


def get_random_sprite():
    sprite_dir, gifs, pngs = _get_sprites()
    return _return_sprite_path(sprite_dir, random.choice(gifs) + ".gif")


class DatabaseData:
    def __init__(self, format=None):
        self.ta = TableAccessor()
        # --- first determine the viable formats before querying data ---
        self.viable_formats = self.get_viable_formats()

        # only load 1 format's data. if not specified, just pick one of viable formats for init loading
        if format:
            f_conditions = {
                "Format": {"op": "==", "value": format},
            }
            # --- now use viable formats to limit queries ---
            self.pvpmetadata = self.ta.get_pvpmetadata(conditions=f_conditions)
            self.pokemonmetadata = self.ta.get_pokemonmetadata(conditions=f_conditions)
        else:
            self.pvpmetadata = None
            self.pokemonmetadata = None

    def get_pvpmetadata(self):
        return self.pvpmetadata

    def get_pokemonmetadata(self):
        return self.pokemonmetadata

    # NOTE this is used to determine default format on main page as well as what formats are viable
    def get_viable_formats(self):
        sessionmaker = self.ta.session_maker
        with session_scope(sessionmaker()) as session:
            viable_formats = (
                session.query(battle_info.Format)
                .group_by(battle_info.Format)
                .having(
                    func.count(battle_info.Format) >= 4000
                )  # 4k is min for metadata tables
                .all()
            )
            viable_formats = [f[0] for f in viable_formats]

        return viable_formats


class FormatData:
    def __init__(self, battle_format: str, db: DatabaseData):
        self.battle_format = battle_format
        self.db = db

        format_conditions = {"Format": {"op": "==", "value": self.battle_format}}

        self.format_pvpmetadata = self.db.get_pvpmetadata()
        self.format_metadata = self.db.get_pokemonmetadata()

        self.top30 = self.format_metadata.sort_values(
            by="Popularity", ascending=False
        ).head(30)

    def get_format_available_mons(self):
        mons = self.format_metadata["Pokemon"][self.format_metadata["SampleSize"] >= 30]
        return mons.tolist()
