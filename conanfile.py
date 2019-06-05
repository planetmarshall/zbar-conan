from conans import ConanFile, tools, AutoToolsBuildEnvironment
import os.path


class ZbarConan(ConanFile):
    name = 'zbar'
    version = '0.10.0'
    license = 'https://www.gnu.org/licenses/lgpl-3.0.en.html'
    author = 'Andrew Marshall <planetmarshalluk@gmail.com>'
    url = 'http://zbar.sourceforge.net/'
    description = 'ZBar is an open source software suite for reading bar codes from various sources'
    settings = 'os', 'compiler', 'build_type', 'arch'
    options = {
        'shared': [True, False],
        'fPIC': [True, False],
        'with_x': [True, False],
        'with_xv': [True, False],
        'with_jpeg': [True, False],
        'with_imagemagick': [True, False],
        'with_npapi': [True, False],
        'with_python': [True, False],
        'with_qt': [True, False],
        'with_gtk': [True, False],
        'enable_video': [True, False]
    }
    default_options = {
        'shared': False,
        'fPIC': True,
        'with_x': False,
        'with_xv': False,
        'with_jpeg': False,
        'with_imagemagick': False,
        'with_npapi': False,
        'with_python': False,
        'with_qt': False,
        'with_gtk': False,
        'enable_video': False
    }
    generators = 'cmake'

    @property
    def _staging_folder(self):
        return os.path.join(self.build_folder, 'stage')

    def requirements(self):
        if self.settings.os == 'Android' and int(self.settings.os.api_level.value) < 28:
            self.requires('iconv/1.16.0@algodynamic/testing')

    def source(self):
        patch = r'''--- config.sub.original	2019-06-03 22:24:50.736966356 +0100
+++ config.sub	2019-06-03 22:25:57.564006475 +0100
@@ -120,7 +120,7 @@
 # Here we must recognize all the valid KERNEL-OS combinations.
 maybe_os=`echo $1 | sed 's/^\(.*\)-\([^-]*-[^-]*\)$/\2/'`
 case $maybe_os in
-  nto-qnx* | linux-gnu* | linux-dietlibc | linux-newlib* | linux-uclibc* | \
+  nto-qnx* | linux-gnu* | linux-dietlibc | linux-newlib* | linux-uclibc* | linux-android* | \
   uclinux-uclibc* | uclinux-gnu* | kfreebsd*-gnu* | knetbsd*-gnu* | netbsd*-gnu* | \
   kopensolaris*-gnu* | \
   storm-chaos* | os2-emx* | rtmk-nova*)
@@ -242,7 +242,7 @@
 	| alpha | alphaev[4-8] | alphaev56 | alphaev6[78] | alphapca5[67] \
 	| alpha64 | alpha64ev[4-8] | alpha64ev56 | alpha64ev6[78] | alpha64pca5[67] \
 	| am33_2.0 \
-	| arc | arm | arm[bl]e | arme[lb] | armv[2345] | armv[345][lb] | avr | avr32 \
+	| arc | arm | arm[bl]e | arme[lb] | armv[2345] | armv[345][lb] | avr | avr32 | aarch64 \
 	| bfin \
 	| c4x | clipper \
 	| d10v | d30v | dlx | dsp16xx | dvp \
 	'''

        url = '''https://downloads.sourceforge.net/project/zbar/zbar/0.10/zbar-0.10.tar.bz2'''
        tools.get(url)
        tools.patch('zbar-0.10/config', patch_string=patch)

    def build(self):

        def on(arg):
            return 'yes' if arg else 'no'

        config = ['--enable-shared=' + on(self.options.shared)]
        config += ['--enable-static' + on(not self.options.shared)]

        if 'iconv' in self.deps_cpp_info.deps:
            config += ['--with-libiconv-prefix=' + self.deps_cpp_info['iconv'].rootpath]

        if self.settings.os == 'Android':
            config += ['--disable-pthread']

        config += [
            '--with-x=' + on(self.options.with_x),
            '--with-xv=' + on(self.options.with_xv),
            '--with-jpeg= ' + on(self.options.with_jpeg),
            '--with-imagemagick=' + on(self.options.with_imagemagick),
            '--with-npapi=' + on(self.options.with_npapi),
            '--with-gtk=' + on(self.options.with_gtk),
            '-with-python=' + on(self.options.with_python),
            '--with-qt=' + on(self.options.with_qt),
            '--enable-video=' + on(self.options.enable_video),
            '--prefix=' + self._staging_folder
        ]

        with tools.chdir(os.path.join(self.source_folder, 'zbar-0.10')):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=config)
            autotools.make()
            autotools.install()

    def package(self):
        self.copy('*', src=self._staging_folder, keep_path=True)

    def package_info(self):
        self.cpp_info.libs = ['zbar']

