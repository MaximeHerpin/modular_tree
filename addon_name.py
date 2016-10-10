import os


def get_file():
    return os.path.join(os.path.dirname(__file__), "addon_name.txt")


def get_addon_name():
    with open(get_file(), 'r') as f:
        name = f.read().strip()
    return name


def save_addon_name(name):
    with open(get_file(), 'w') as f:
        print(name, file=f)
