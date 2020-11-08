from . import cube_animation

animations = {}
for anim in [cube_animation]:
    animations.update(anim.animations)