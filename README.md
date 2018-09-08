# Blender Tween Objects
Control interpolation for objects in Blender to help breakdown animation.

To be used on available curves keyframes at current frame for selected objects. (Armatures on test)

* use slider, or:
* `ALT` + `SHIFT` + `W` (temporary)
* `CTRL` to snap to tenth
* `SHIFT` for precision mode

* Notes:
  - When tweening a keyframe at the current frame, you can check the animation sliding frames and continue to ajust the tween value at the exact same frame. This is possible only if you keep the same active object since a property is saving one frame number associated to a tween value.
  But if you try to tween at an other frame, the value will be reset at 0.5 (but the displayed value won't show 0.5)

License GPLv2
