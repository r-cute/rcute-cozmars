from . import cube_charge_animation

animations = {}
for anim in [cube_charge_animation]:
    animations.update(anim.animations)