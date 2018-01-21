# Copyright 2016 Maxime Herpin, Jake Dube
#
# ##### BEGIN GPL LICENSE BLOCK ######
# This file is part of Modular Tree.
#
# Modular Tree is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Modular Tree is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Modular Tree.  If not, see <http://www.gnu.org/licenses/>.
# ##### END GPL LICENSE BLOCK #####

import bpy, os

from .addon_name import get_addon_name


def save_text(text):
    """Saves Blender text block that is stored externally.

    Args:
        text: Blender text block to save.
    """
    # get filepath and text
    text_path = text.filepath
    text_as_string = text.as_string()
    # write to file
    with open(text_path, "w") as d:
        d.write(str(text_as_string))


def always_save():
    """Saves .blend file and referenced images/texts.

    Does not save 'Render Result' or 'Viewer Node'

    Returns:
        "BLEND_ERROR", None: IF file has not been saved (no filepath)
        "IMAGE_ERROR", image: IF image has not been saved
        "SUCCESS", None: IF saved all required types correctly
    """
    try:
        addon_prefs = bpy.context.user_preferences.addons[get_addon_name()].preferences
    except KeyError:
        print("Could not find addon prefs! Files not saved!")
        return "FAILED", None

    print("\n")

    # save file
    if addon_prefs.always_save_prior:
        if bpy.data.is_saved:
            bpy.ops.wm.save_mainfile()
            print("Blend file saved...")
        else:
            bpy.ops.wm.save_as_mainfile(filepath=os.path.join( bpy.context.user_preferences.filepaths.temporary_d irectory,'modular_tree'), copy=True)


    # save all images
    if addon_prefs.save_all_images:
        for image in bpy.data.images:
            if image.has_data and image.is_dirty and not image.packed_file:
                if image.filepath:
                    image.save()
                    print("Image \"", image.name, "\" saved...", sep="")
                elif image.name != 'Render Result' and image.name != 'Viewer Node':
                    return "IMAGE_ERROR", image

    # save all texts
    if addon_prefs.save_all_texts:
        for text in bpy.data.texts:
            if text.filepath and text.is_dirty:
                # my function for saving texts
                save_text(text)
                print("Text \"", text.name, "\" saved...", sep="")

    print("\n")

    return "SUCCESS", None


def save_everything(twig=False):
    messages = []
    message_lvls = []
    scene = bpy.context.scene
    mtree_props = scene.mtree_props

    # if twig:
    #     # do illegal settings checks here
    #     if mtree_props.leaf_object not in scene.objects:
    #         messages += ["Requires a valid leaf object! Add one with the object selector in the twig UI."]
    #         message_lvls += ['ERROR']
    #         return messages, message_lvls, 'CANCELLED'

    # save files
    save_return, bad_file = always_save()
    if save_return == "IMAGE_ERROR":
        messages += [
            "Image '" + bad_file.name + "' does not have a valid file path (for saving). Assign " + "a valid path, pack image, or disable save images in " + "user prefs"]
        message_lvls += ['ERROR']
        return messages, message_lvls, 'CANCELLED'

    elif save_return == "TEXT_ERROR":
        messages += [
            "Text '" + bad_file.name + "' does not have a valid file path (for saving). " + "Assign a valid path or disable save texts in user prefs"]
        message_lvls += ['ERROR']
        return messages, message_lvls, 'CANCELLED'

    else:
        return [], [], ''  # this is what we want
