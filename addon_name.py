def get_addon_name():
    with open("addon_name.txt", 'r') as f:
        name = f.read().strip()
    return name


def save_addon_name(name):
    with open("addon_name.txt", 'w') as f:
        print(name, file=f)
