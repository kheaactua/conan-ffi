import os
from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conans.errors import ConanException


class FfiConan(ConanFile):
    name = 'ffi'
    version = '3.2.1'
    license = 'https://github.com/libffi/libffi/blob/master/LICENSE'
    url = 'https://raw.githubusercontent.com/kheaactua/conan-ffi/v3.2.1/conanfile.py'
    description = 'Compilers for high level languages generate code that follow certain conventions.'
    settings = 'os', 'compiler', 'build_type', 'arch'
    options = {'shared': [True, False]}

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
        autotools = AutoToolsBuildEnvironment(self, win_bash=('Windows' == self.settings.os))

        with tools.chdir(self.name):
            self.run('./autogen.sh')
            autotools.configure(args=[f'--prefix={self.package_folder}'])
            autotools.make()
            autotools.make(args=['install'])

    def package_info(self):
        self.cpp_info.libs = ['ffi']
        if 'Windows' == self.settings.os:
            self.env_info.manpath.append(os.path.join(self.package_folder, 'share', 'man'))

# vim: ts=4 sw=4 expandtab ffs=unix ft=python foldmethod=marker :
