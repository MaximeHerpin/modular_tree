from genericpath import exists
import os
import zipfile
from pathlib import Path
import shutil
import platform


TMP_DIRPATH = r"./tmp"
ADDON_SOURCE_DIR = "python_classes"
VERSION_FILEPATH = os.path.join(Path(__file__).parent.parent.parent, "VERSION")

def setup_addon_directory():
    plateform_name = "windows" if platform.system() == "Windows" else "linux" if platform.system() == "Linux" else "macOS"
    version = read_version()
    addon_dirpath = os.path.join(TMP_DIRPATH, f"modular_tree_{version}_{plateform_name}")
    root = os.path.join(addon_dirpath, "modular_tree")
    Path(root).mkdir(exist_ok=True, parents=True)

    all_files = os.listdir(".")
    if not [i for i in all_files if i.endswith(".pyd") or i.endswith(".so")]:
        raise Exception("no libraries were output")
    for f in all_files:
        if f.endswith(".py") or f.endswith(".pyd") or f.endswith(".so"):
            shutil.copy2(os.path.join(".",f), root)
        elif f == ADDON_SOURCE_DIR:
            shutil.copytree(os.path.join(".",f), os.path.join(root, f))

    return addon_dirpath

def create_zip(input_dir, output_dir):
    basename = os.path.join(output_dir, Path(input_dir).stem)
    filepath = shutil.make_archive(basename, "zip", input_dir)
    return filepath


def read_version():
    with open(VERSION_FILEPATH, "r") as f:
        return f.read()

if __name__ == "__main__":
    addon_dirpath = setup_addon_directory()
    archive_filepath = create_zip(addon_dirpath, TMP_DIRPATH)