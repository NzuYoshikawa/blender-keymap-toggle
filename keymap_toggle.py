"""
Keymap Toggle Add-on for Blender
Instantly switches between "Blender" and "Industry Compatible" keymaps
using a conflict-free shortcut key.
"""

bl_info = {
    "name": "Keymap Toggle",
    "author": "Custom",
    "version": (1, 0, 1),
    "blender": (3, 0, 0),
    "location": "Preferences > Add-ons",
    "description": "Switch between Blender and Industry Compatible keymaps with a single shortcut",
    "category": "System",
}

import bpy

# ---------------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------------

def _collect_all_shortcuts(keyconfig_name: str) -> set[tuple]:
    """Return a set of (type, value, ctrl, shift, alt, oskey) tuples from a keyconfig."""
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.get(keyconfig_name)
    if kc is None:
        return set()

    shortcuts = set()
    for km in kc.keymaps:
        for kmi in km.keymap_items:
            if not kmi.active:
                continue
            shortcuts.add((
                kmi.type,
                kmi.value,
                kmi.ctrl,
                kmi.shift,
                kmi.alt,
                kmi.oskey,
            ))
    return shortcuts


def find_conflict_free_shortcut() -> tuple | None:
    """Find a key combo unused in both Blender and Industry Compatible keymaps."""
    used_blender = _collect_all_shortcuts("Blender")
    used_industry = _collect_all_shortcuts("industry_compatible")
    used = used_blender | used_industry

    # Candidates: Ctrl+Alt+Shift + letter, then Ctrl+Alt + letter
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    for letter in letters:
        combo = (letter, "PRESS", True, True, True, False)  # Ctrl+Alt+Shift+Letter
        if combo not in used:
            return combo

    for letter in letters:
        combo = (letter, "PRESS", True, False, True, False)  # Ctrl+Alt+Letter
        if combo not in used:
            return combo

    # F-keys with Ctrl+Alt
    for i in range(1, 13):
        combo = (f"F{i}", "PRESS", True, False, True, False)
        if combo not in used:
            return combo

    return None  # extremely unlikely


# ---------------------------------------------------------------------------
# Operator
# ---------------------------------------------------------------------------

_BLENDER_NAMES = {"Blender", "blender"}
_INDUSTRY_NAMES = {"industry_compatible", "Industry Compatible", "Industry_Compatible"}


def _find_keyconfig(wm, name_set: set) -> "bpy.types.KeyConfig | None":
    """Return the first KeyConfig whose name is in name_set, or partial-match fallback."""
    for kc in wm.keyconfigs:
        if kc.name in name_set:
            return kc
    # Partial match fallback (covers version-specific naming variations)
    for kc in wm.keyconfigs:
        for candidate in name_set:
            if candidate.lower() in kc.name.lower():
                return kc
    return None


class KEYMAP_OT_Toggle(bpy.types.Operator):
    bl_idname = "keymap.toggle_preset"
    bl_label = "Toggle Keymap Preset"
    bl_description = "Switch between Blender and Industry Compatible keymaps"

    def execute(self, context):
        wm = context.window_manager
        current_name = wm.keyconfigs.active.name if wm.keyconfigs.active else ""

        if current_name in _BLENDER_NAMES:
            target_kc = _find_keyconfig(wm, _INDUSTRY_NAMES)
            display_name = "Industry Compatible"
        else:
            target_kc = _find_keyconfig(wm, _BLENDER_NAMES)
            display_name = "Blender"

        if target_kc is None:
            available = [kc.name for kc in wm.keyconfigs]
            self.report({"ERROR"}, f"Target keyconfig not found. Available: {available}")
            return {"CANCELLED"}

        # Actually apply the switch (wm.keyconfigs.active is the live setting)
        wm.keyconfigs.active = target_kc

        # Also persist to preferences so it survives restart
        context.preferences.keymap.active_keyconfig = target_kc.name

        self.report({"INFO"}, f"Keymap switched to: {display_name}")
        return {"FINISHED"}


# ---------------------------------------------------------------------------
# Add-on Preferences
# ---------------------------------------------------------------------------

class KeymapTogglePreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    # Stored as individual booleans + key type because KeyMapItem can't be a
    # raw property; we manage the actual keymap item in register/unregister.
    shortcut_key: bpy.props.StringProperty(
        name="Key",
        description="Key used for toggling (e.g. K, F5)",
        default="",
    )
    shortcut_ctrl: bpy.props.BoolProperty(name="Ctrl", default=True)
    shortcut_shift: bpy.props.BoolProperty(name="Shift", default=True)
    shortcut_alt: bpy.props.BoolProperty(name="Alt", default=True)

    def draw(self, context):
        layout = self.layout

        # Current keymap display (read from live wm state, not prefs string)
        wm = context.window_manager
        active_kc = wm.keyconfigs.active
        current_name = active_kc.name if active_kc else "Unknown"
        box = layout.box()
        box.label(text=f"Active keymap: {current_name}", icon="INFO")

        # Shortcut display / re-assign
        row = layout.row(align=True)
        row.label(text="Shortcut:")
        row.prop(self, "shortcut_ctrl", toggle=True)
        row.prop(self, "shortcut_shift", toggle=True)
        row.prop(self, "shortcut_alt", toggle=True)
        row.prop(self, "shortcut_key", text="")

        layout.operator("keymap.apply_shortcut", text="Apply Shortcut", icon="CHECKMARK")
        layout.operator("keymap.detect_shortcut", text="Auto-detect conflict-free key", icon="VIEWZOOM")


class KEYMAP_OT_ApplyShortcut(bpy.types.Operator):
    bl_idname = "keymap.apply_shortcut"
    bl_label = "Apply Shortcut"
    bl_description = "Register the shortcut entered in preferences"

    def execute(self, context):
        addon_prefs = context.preferences.addons[__name__].preferences
        key = addon_prefs.shortcut_key.strip().upper()
        if not key:
            self.report({"WARNING"}, "Enter a key first.")
            return {"CANCELLED"}

        # Conflict check
        used_blender = _collect_all_shortcuts("Blender")
        used_industry = _collect_all_shortcuts("industry_compatible")
        used = used_blender | used_industry

        combo = (
            key,
            "PRESS",
            addon_prefs.shortcut_ctrl,
            addon_prefs.shortcut_shift,
            addon_prefs.shortcut_alt,
            False,
        )
        if combo in used:
            self.report({"WARNING"}, f"Conflict detected for {_combo_label(combo)}! Choose another key.")
            return {"CANCELLED"}

        _unregister_shortcut()
        _register_shortcut(
            key,
            addon_prefs.shortcut_ctrl,
            addon_prefs.shortcut_shift,
            addon_prefs.shortcut_alt,
        )
        self.report({"INFO"}, f"Shortcut set to {_combo_label(combo)}")
        return {"FINISHED"}


class KEYMAP_OT_DetectShortcut(bpy.types.Operator):
    bl_idname = "keymap.detect_shortcut"
    bl_label = "Auto-detect Conflict-free Key"
    bl_description = "Scan both keymaps and assign a shortcut with no conflicts"

    def execute(self, context):
        combo = find_conflict_free_shortcut()
        if combo is None:
            self.report({"ERROR"}, "Could not find a conflict-free shortcut.")
            return {"CANCELLED"}

        key_type, _, ctrl, shift, alt, _ = combo
        _unregister_shortcut()
        _register_shortcut(key_type, ctrl, shift, alt)

        addon_prefs = context.preferences.addons[__name__].preferences
        addon_prefs.shortcut_key = key_type
        addon_prefs.shortcut_ctrl = ctrl
        addon_prefs.shortcut_shift = shift
        addon_prefs.shortcut_alt = alt

        self.report({"INFO"}, f"Shortcut set to {_combo_label(combo)}")
        return {"FINISHED"}


# ---------------------------------------------------------------------------
# Keymap registration helpers
# ---------------------------------------------------------------------------

_addon_keymaps: list[tuple] = []  # [(km, kmi), ...]


def _combo_label(combo: tuple) -> str:
    key_type, _, ctrl, shift, alt, _ = combo
    parts = []
    if ctrl:
        parts.append("Ctrl")
    if shift:
        parts.append("Shift")
    if alt:
        parts.append("Alt")
    parts.append(key_type)
    return "+".join(parts)


def _register_shortcut(key_type: str, ctrl: bool, shift: bool, alt: bool):
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if not kc:
        return
    km = kc.keymaps.new(name="Window", space_type="EMPTY")
    kmi = km.keymap_items.new(
        KEYMAP_OT_Toggle.bl_idname,
        type=key_type,
        value="PRESS",
        ctrl=ctrl,
        shift=shift,
        alt=alt,
    )
    _addon_keymaps.append((km, kmi))


def _unregister_shortcut():
    for km, kmi in _addon_keymaps:
        km.keymap_items.remove(kmi)
    _addon_keymaps.clear()


# ---------------------------------------------------------------------------
# Register / Unregister
# ---------------------------------------------------------------------------

_classes = (
    KEYMAP_OT_Toggle,
    KEYMAP_OT_ApplyShortcut,
    KEYMAP_OT_DetectShortcut,
    KeymapTogglePreferences,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)

    # Auto-detect and assign a conflict-free shortcut on first install
    combo = find_conflict_free_shortcut()
    if combo:
        key_type, _, ctrl, shift, alt, _ = combo
        _register_shortcut(key_type, ctrl, shift, alt)

        # Persist choice in preferences
        try:
            addon_prefs = bpy.context.preferences.addons[__name__].preferences
            addon_prefs.shortcut_key = key_type
            addon_prefs.shortcut_ctrl = ctrl
            addon_prefs.shortcut_shift = shift
            addon_prefs.shortcut_alt = alt
        except Exception:
            pass  # preferences not yet available at very first load


def unregister():
    _unregister_shortcut()
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
