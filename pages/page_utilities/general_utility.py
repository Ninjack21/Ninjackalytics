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
