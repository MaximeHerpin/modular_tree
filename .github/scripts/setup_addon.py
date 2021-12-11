from genericpath import exists
import os
import zipfile
from pathlib import Path
import shutil
import platform


TMP_DIRPATH = r"./tmp"
ADDON_SOURCE_DIRNAME = "python_classes"
RESOURCES_DIRNAME = "resources"
VERSION_FILEPATH = os.path.join(Path(__file__).parent.parent.parent, "VERSION")

def setup_addon_directory():
    plateform_name = "windows" if platform.system() == "Windows" else "linux" if platform.system() == "Linux" else "macOS"
    version = read_version()
    addon_dirpath = os.path.join(TMP_DIRPATH, f"modular_tree_{version}_{plateform_name}")
    root = os.path.join(addon_dirpath, "modular_tree")
    Path(root).mkdir(exist_ok=True, parents=True)

    all_files = os.listdir(".")


    if not [i for i in all_files if i.endswith(".pyd") or i.endswith(".so")]:
        list_files(".")
        raise Exception("no libraries were output")
    for f in all_files:
        if f.endswith(".py") or f.endswith(".pyd") or f.endswith(".so"):
            shutil.copy2(os.path.join(".",f), root)
        elif f == ADDON_SOURCE_DIRNAME or f == RESOURCES_DIRNAME:
            shutil.copytree(os.path.join(".",f), os.path.join(root, f))

    return addon_dirpath

def create_zip(input_dir, output_dir):
    basename = os.path.join(output_dir, Path(input_dir).stem)
    filepath = shutil.make_archive(basename, "zip", input_dir)
    return filepath


def list_files(root_directory):
    excluded_directories = {"dependencies", "build", "__pycache__", ".github", ".git"}
    for root, _, files in os.walk(root_directory):
        should_skip = False
        for exclusion in excluded_directories:
            if exclusion in root:
                should_skip = True
                break
        if should_skip:
            continue


        level = root.replace(root_directory, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print('{}{}/'.format(indent, os.path.basename(root)))
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            print('{}{}'.format(subindent, f))

def read_version():
    with open(VERSION_FILEPATH, "r") as f:
        return f.read()

if __name__ == "__main__":
    addon_dirpath = setup_addon_directory()
    archive_filepath = create_zip(addon_dirpath, TMP_DIRPATH)