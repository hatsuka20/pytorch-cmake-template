import os
import re
import subprocess
import sys
from pathlib import Path

from setuptools import Extension, setup, find_packages
from setuptools.command.build_ext import build_ext

package_name = "mylib"

class CMakeExtension(Extension):
    def __init__(self, name: str, sourcedir: str = "") -> None:
        super().__init__(name, sources=[])
        self.sourcedir = os.fspath(Path(sourcedir).resolve())


class CMakeBuild(build_ext):
    def build_extension(self, ext: CMakeExtension) -> None:
        ext_fullpath = Path.cwd() / self.get_ext_fullpath(ext.name)
        extdir = ext_fullpath.parent.resolve() / package_name

        debug = int(os.environ.get("DEBUG", 0)) if self.debug is None else self.debug
        cfg = "Debug" if debug else "Release"

        cmake_generator = os.environ.get("CMAKE_GENERATOR", "")
        if not cmake_generator or cmake_generator == "Ninja":
            try:
                import ninja

                ninja_executable_path = Path(ninja.BIN_DIR) / "ninja"
                cmake_args += [
                    "-GNinja",
                    f"-DCMAKE_MAKE_PROGRAM:FILEPATH={ninja_executable_path}",
                ]
            except ImportError:
                pass

        import torch.utils

        cmake_args = [
            f"-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={extdir}{os.sep}",
            f"-DPYTHON_EXECUTABLE={sys.executable}",
            f"-DCMAKE_BUILD_TYPE={cfg}",
            f"-DCMAKE_PREFIX_PATH={torch.utils.cmake_prefix_path}",
            f"-DEXAMPLE_VERSION_INFO={self.distribution.get_version()}"
        ]
        build_args = []

        single_config = any(x in cmake_generator for x in {"NMake", "Ninja"})
        contains_arch = any(x in cmake_generator for x in {"ARM", "Win64"})
        if not single_config:
            cmake_args += [
                f"-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_{cfg.upper()}={extdir}"
            ]
            build_args += ["--config", cfg]

        if "CMAKE_BUILD_PARALLEL_LEVEL" not in os.environ:
            if hasattr(self, "parallel") and self.parallel:
                build_args += [f"-j{self.parallel}"]

        build_temp = Path(self.build_temp) / ext.name
        if not build_temp.exists():
            build_temp.mkdir(parents=True)

        subprocess.run(
            ["cmake", ext.sourcedir, *cmake_args], cwd=build_temp, check=True
        )
        subprocess.run(
            ["cmake", "--build", ".", *build_args], cwd=build_temp, check=True
        )


setup(
    packages=find_packages(),
    ext_modules=[CMakeExtension(package_name)],
    cmdclass={"build_ext": CMakeBuild},
)
