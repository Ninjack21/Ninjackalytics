import os
import difflib
import random


def _get_sprites():
    current_dir = os.path.dirname(__file__)
    while current_dir != "/":
        if os.path.basename(current_dir) == "Ninjackalytics":
            break
        current_dir = os.path.dirname(current_dir)

    sprite_dir = os.path.join(current_dir, "assets/showdown_sprites")
    sprites = os.listdir(sprite_dir)
    return sprite_dir, sprites


def _return_sprite_path(sprite_dir, sprite):
    return os.path.join(sprite_dir, sprite).split("Ninjackalytics")[-1]


def find_closest_sprite(name):
    sprite_dir, sprites = _get_sprites()

    # First, look for an exact match
    if name in sprites:
        return _return_sprite_path(sprite_dir, name)

    # Otherwise, find the closest match
    closest_match = difflib.get_close_matches(name, sprites, n=1)
    if closest_match:
        return _return_sprite_path(sprite_dir, closest_match[0])

    # If no match is found, return None
    return None


def get_random_sprite():
    sprite_dir, sprites = _get_sprites()
    return _return_sprite_path(sprite_dir, random.choice(sprites))
