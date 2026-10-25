"""Local python-for-android CFFI recipe for the cryptography build."""

import os

from pythonforandroid.recipe import PyProjectRecipe


class CffiRecipe(PyProjectRecipe):
    """Build CFFI without the broken temporary Python 3.14 pip environment."""

    name = "cffi"
    version = "2.0.0"
    url = "https://github.com/python-cffi/cffi/archive/refs/tags/v{version}.tar.gz"
    depends = ["pycparser", "libffi"]
    extra_build_args = ["--no-isolation"]

    def lookup_prebuilt(self, arch):
        """Force the Android source recipe; PyPI has no matching Android wheel."""

        return False

    def get_hostrecipe_env(self, arch=None):
        env = super().get_hostrecipe_env(arch)
        libffi = self.get_recipe("libffi", self.ctx)
        env["FFI_INC"] = ",".join(libffi.get_include_dirs(arch))
        return env

    def get_recipe_env(self, arch=None, **kwargs):
        env = super().get_recipe_env(arch, **kwargs)
        libffi = self.get_recipe("libffi", self.ctx)
        includes = libffi.get_include_dirs(arch)
        env["CFLAGS"] = " -I".join([env.get("CFLAGS", "")] + includes)
        env["CFLAGS"] += " -I{}".format(self.ctx.python_recipe.include_root(arch.arch))
        env["LDFLAGS"] = env.get("CFLAGS", "") + " -L" + self.ctx.get_libs_dir(arch.arch)
        env["LDFLAGS"] += " -L{}".format(os.path.join(self.ctx.bootstrap.build_dir, "libs", arch.arch))
        env["LDFLAGS"] += " -L{}".format(arch.ndk_lib_dir_versioned)
        env["LDFLAGS"] += " -L{}".format(self.ctx.python_recipe.link_root(arch.arch))
        env["LDFLAGS"] += " -lpython{}".format(self.ctx.python_recipe.link_version)
        return env


recipe = CffiRecipe()
