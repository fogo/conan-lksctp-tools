"""Conan recipe for LKSCTP Tools
"""
from os import unlink
from os.path import join
from tempfile import mkdtemp
from conans import ConanFile
from conans import AutoToolsBuildEnvironment
from conans.tools import download
from conans.tools import unzip
from conans.tools import chdir
from conans.tools import environment_append
from conans.tools import check_md5


class LKSCTPToolsConan(ConanFile):
    """Download LKSCTP Tools, build and create package
    """
    name = "lksctp-tools"
    version = "1.0.17"
    generators = "cmake", "txt"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False]}
    default_options = "shared=True"
    url = "https://github.com/uilianries/conan-lksctp-tools"
    author = "Uilian Ries <uilianries@gmail.com>"
    license = "GPL-2"
    release_name = "%s-%s" % (name, version)
    build_dir = mkdtemp(suffix="conan-klsctp-tools")

    def source(self):
        tar_name = "%s.tar.gz" % self.release_name
        download("https://github.com/sctp/lksctp-tools/archive/%s" % tar_name,
                 tar_name)
        check_md5(tar_name, "910a4f1d4024d71149b91f50f97eae23")
        unzip(tar_name)
        unlink(tar_name)

    def build(self):
        env_build = AutoToolsBuildEnvironment(self)
        with environment_append(env_build.vars):
            with chdir("%s-%s" % (self.name, self.release_name)):
                self.run("./bootstrap")
                library_type = "--disable-static" if self.options.shared else "--disable-shared"
                self.run("./configure --prefix=%s --disable-tests %s" %
                         (self.build_dir, library_type))
                self.run("make")
                self.run("make install")

    def package(self):
        self.copy(
            pattern="*.h", dst="include", src=join(self.build_dir, "include"))
        self.copy(
            pattern="*.a",
            dst="lib",
            src=join(self.build_dir, "lib"),
            keep_path=False)
        self.copy(
            pattern="*.so*",
            dst="lib",
            src=join(self.build_dir, "lib"),
            keep_path=False)
        self.copy(pattern="*", dst="bin", src=join(self.build_dir, "bin"))

    def package_info(self):
        self.cpp_info.libs = ['sctp', 'withsctp']
        if self.settings.os == "Linux":
            self.cpp_info.libs.append("dl")
