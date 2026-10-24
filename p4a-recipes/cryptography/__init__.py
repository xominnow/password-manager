"""Local python-for-android recipe for cryptography's Rust build."""

from os.path import join

from pythonforandroid.recipe import RustCompiledComponentsRecipe


class CryptographyRecipe(RustCompiledComponentsRecipe):
    """Build cryptography for Android with the selected NDK API level."""

    name = "cryptography"
    version = "50.0.2"
    url = "https://github.com/pyca/cryptography/archive/refs/tags/{version}.tar.gz"
    depends = ["openssl", "cffi"]
    # Avoid python-build's broken temporary pip environment on the current
    # Python 3.14 host; p4a installs this backend in hostpython instead.
    hostpython_prerequisites = ["maturin", "cffi==2.0.0"]
    extra_build_args = ["--no-isolation"]

    def lookup_prebuilt(self, arch):
        """Force the Android source recipe; PyPI has no matching Android wheel."""

        return False

    def get_recipe_env(self, arch, **kwargs):
        env = super().get_recipe_env(arch, **kwargs)
        openssl_build_dir = self.get_recipe("openssl", self.ctx).get_build_dir(arch.arch)
        build_target = self.RUST_ARCH_CODES[arch.arch].upper().replace("-", "_")
        env[f"{build_target}_OPENSSL_INCLUDE_DIR"] = join(openssl_build_dir, "include")
        env[f"{build_target}_OPENSSL_LIB_DIR"] = openssl_build_dir
        # Maturin reads this variable inside its isolated build environment;
        # p4a's base Rust recipe does not currently forward it.
        env["ANDROID_API_LEVEL"] = str(self.ctx.ndk_api)
        return env


recipe = CryptographyRecipe()
