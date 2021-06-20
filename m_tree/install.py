import os
import re
import sys
import platform
import subprocess

from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
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
    extension = ".bat" if platform.system() == "Windows" else ".sh"
    subprocess.run(f"bootstrap-vcpkg{extension}", cwd=VCPKG_PATH, shell=True)

    triplet = ":x64-windows" if platform.system() == "Windows" else "x64-linux"
    for package in PACKAGES:
        subprocess.run(["vcpkg", "install", package+triplet], cwd=VCPKG_PATH, shell=True)


def build():
    build_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "build"))
    if not os.path.exists(build_dir):
        os.makedirs(build_dir)

    subprocess.check_call(['cmake', "../"], cwd=build_dir)
    subprocess.check_call(['cmake', '--build', '.', "--config", "Release"], cwd=build_dir)

if __name__ == "__main__":
    install()