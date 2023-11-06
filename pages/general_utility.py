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
    gifs = [sprite for sprite in sprites if sprite.endswith(".gif")]
    pngs = [sprite for sprite in sprites if sprite.endswith(".png")]
    return sprite_dir, gifs, pngs


def _return_sprite_path(sprite_dir, sprite):
    return os.path.join(sprite_dir, sprite).split("Ninjackalytics")[-1]


def find_closest_sprite(name):
    sprite_dir, gifs, pngs = _get_sprites()

    # First, look for an exact match in gifs
    if name in gifs:
        return _return_sprite_path(sprite_dir, name)

    # Otherwise, find the closest match or subset in gifs
    closest_match = difflib.get_close_matches(name, gifs, n=1)
    if closest_match:
        return _return_sprite_path(sprite_dir, closest_match[0])
    else:
        for sprite in gifs:
            if name.lower() in sprite.lower():
                return _return_sprite_path(sprite_dir, sprite)

    # If no match is found in gifs, try again with pngs
    # First, look for an exact match in pngs
    if name in pngs:
        return _return_sprite_path(sprite_dir, name)

    # Otherwise, find the closest match or subset in pngs
    closest_match = difflib.get_close_matches(name, pngs, n=1)
    if closest_match:
        return _return_sprite_path(sprite_dir, closest_match[0])
    else:
        for sprite in pngs:
            if name.lower() in sprite.lower():
                return _return_sprite_path(sprite_dir, sprite)

    # If no match is found, return None
    return None


def get_random_sprite():
    sprite_dir, gifs, pngs = _get_sprites()
    return _return_sprite_path(sprite_dir, random.choice(gifs + pngs))
