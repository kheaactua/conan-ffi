import os, platform
from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conans.errors import ConanException


class FfiConan(ConanFile):
    """
    Builds libffi, only tested on linux and cross-compiling to arm.  By default
    this builds the static and shared ffi libs.
    """

    name = 'ffi'
    version = '3.2.1'
    license = 'https://github.com/libffi/libffi/blob/master/LICENSE'
    url = 'https://raw.githubusercontent.com/kheaactua/conan-ffi/v3.2.1/conanfile.py'
    description = 'Compilers for high level languages generate code that follow certain conventions.'
    settings = 'os', 'compiler', 'build_type', 'arch'
    requires = 'helpers/[>=0.2.0]@ntc/stable',

    def system_requirements(self):

        pack_names = None
        if tools.os_info.linux_distro == 'ubuntu':
            pack_names = ['texinfo']

            if self.settings.arch == 'x86':
                full_pack_names = []
                for pack_name in pack_names:
                    full_pack_names += [pack_name + ':i386']
                pack_names = full_pack_names

        if pack_names:
            try:
                installer = tools.SystemPackageTool()
                installer.update() # Update the package database
                installer.install(' '.join(pack_names)) # Install the package
            except ConanException:
                self.output.warn('Could not install system requirements')


    def source(self):
        self.run(f"git clone https://github.com/libffi/libffi {self.name}")
        self.run(f"cd {self.name} && git checkout v{self.version}")

    def build(self):
        win_bash=(platform.system() == "Windows")

        autotools = AutoToolsBuildEnvironment(self, win_bash=win_bash)

        with tools.chdir(self.name):
            self.run('./autogen.sh', win_bash=win_bash)
            autotools.configure(args=[f'--prefix={self.package_folder}'])
            autotools.make()
            autotools.make(args=['install'])

    def package_info(self):
        self.cpp_info.libs = ['ffi']
        self.env_info.MANPATH.append(os.path.join(self.package_folder, 'share', 'man'))

        # Populate the pkg-config environment variables
        import site; site.addsitedir(self.deps_cpp_info['helpers'].rootpath) # Compensate for #2644
        from platform_helpers import adjustPath, appendPkgConfigPath

        self.env_info.PKG_CONFIG_LIBFFI_PREFIX = adjustPath(self.package_folder)
        appendPkgConfigPath(adjustPath(os.path.join(self.package_folder, 'lib', 'pkgconfig')), self.env_info)

        # Populate the pkg-config environment variables
        import site; site.addsitedir(self.deps_cpp_info['helpers'].rootpath) # Compensate for #2644
        from platform_helpers import adjustPath, appendPkgConfigPath
        self.env_info.PKG_CONFIG_FLANN_PREFIX = adjustPath(self.package_folder)
        appendPkgConfigPath(adjustPath(os.path.join(self.package_folder, 'lib', 'pkgconfig')), self.env_info)


# vim: ts=4 sw=4 expandtab ffs=unix ft=python foldmethod=marker :
