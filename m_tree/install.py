import os
import re
import sys
import platform
import subprocess

from distutils.version import LooseVersion


VCPKG_PATH = os.path.join(os.path.dirname(__file__), r"./dependencies/vcpkg/")

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
    if platform.system() == "Windows":
        subprocess.run(f"bootstrap-vcpkg.bat", cwd=VCPKG_PATH, shell=True)
    else:
        subprocess.run(["sh", "./bootstrap-vcpkg.sh"], cwd=VCPKG_PATH, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    triplet = ":x64-windows" if platform.system() == "Windows" else "x64-linux"
    for package in PACKAGES:
        subprocess.run(["./vcpkg", "install", package+triplet], cwd=VCPKG_PATH, shell=True)


def build():
    build_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "build"))
    if not os.path.exists(build_dir):
        os.makedirs(build_dir)

    subprocess.check_call(['cmake', "../"], cwd=build_dir)
    subprocess.check_call(['cmake', '--build', '.', "--config", "Release"], cwd=build_dir)

if __name__ == "__main__":
    install()