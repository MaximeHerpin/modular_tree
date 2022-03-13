import os
import re
import sys
import platform
import subprocess

from distutils.version import LooseVersion


VCPKG_PATH = os.path.join(os.path.dirname(__file__), "dependencies", "vcpkg")

PACKAGES = ["eigen3"]


def install():
    try:
        out = subprocess.check_output(['cmake', '--version'])
    except OSError:
        raise RuntimeError("CMake must be installed")

    if platform.system() == "Windows":
        cmake_version = LooseVersion(re.search(r'version\s*([\d.]+)', out.decode()).group(1))
        if cmake_version < '3.1.0':
            raise RuntimeError("CMake >= 3.1.0 is required on Windows")

    install_vcpkg_dependencies()
    build()

    
def install_vcpkg_dependencies():
    print(f"system is {platform.system()}")
    if platform.system() == "Windows":
        subprocess.run(f"bootstrap-vcpkg.bat", cwd=VCPKG_PATH, shell=True)
    else:
        subprocess.run(os.path.join(VCPKG_PATH, "bootstrap-vcpkg.sh"))
    for package in PACKAGES:
        print(f"installing {package}")
        if platform.system() == "Windows":
            triplet = ":x64-windows"
        elif platform.system() == "Linux":
            triplet = ":x64-linux"
        else:
            triplet = ":x64-osx"
        subprocess.check_call([os.path.join(VCPKG_PATH, "vcpkg"), "install", package+triplet])

def build():
    build_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "build"))
    if not os.path.exists(build_dir):
        os.makedirs(build_dir)

    subprocess.check_call(['cmake', "../", "-DPYBIND11_PYTHON_VERSION=3.10"], cwd=build_dir)
    subprocess.check_call(['cmake', '--build', '.', "--config", "Release"], cwd=build_dir)

    print([i for i in os.listdir(os.path.join(os.path.dirname(__file__), "binaries"))])
    

if __name__ == "__main__":
    install()