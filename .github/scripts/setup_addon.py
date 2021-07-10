from genericpath import exists
import os
import zipfile
from pathlib import Path
import shutil


TMP_DIRPATH = r"./tmp"
ADDON_SOURCE_DIR = "python_classes"

def setup_addon_directory():
    addon_dirpath = os.path.join(TMP_DIRPATH, f"modular_tree")
    Path(addon_dirpath).mkdir(exist_ok=True, parents=True)

    all_files = os.listdir(".")
    for f in all_files:
        if f.endswith(".py") or f.endswith(".pyd") or f.endswith(".so"):
            shutil.copy2(os.path.join(".",f), addon_dirpath)
        elif f == ADDON_SOURCE_DIR:
            shutil.copytree(os.path.join(".",f), os.path.join(addon_dirpath, f))

    return addon_dirpath

def create_zip(input_dir, output_dir):
    basename = os.path.join(output_dir, Path(input_dir).stem)
    filepath = shutil.make_archive(basename, "zip", input_dir)
    return filepath

if __name__ == "__main__":
    addon_dirpath = setup_addon_directory()
    archive_filepath = create_zip(addon_dirpath, TMP_DIRPATH)