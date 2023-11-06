import os

current_dir = os.path.dirname(__file__)
while current_dir != "/":
    if os.path.basename(current_dir) == "Ninjackalytics":
        break
    current_dir = os.path.dirname(current_dir)

sprite_dir = os.path.join(current_dir, "assets/showdown_sprites")
sprites = os.listdir(sprite_dir)

sprite_height = "70%"
sprite_width = "70%"
