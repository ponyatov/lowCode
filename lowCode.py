import os, sys


class Object:
    def __init__(self, V):
        self.value = V
        self.nest = []

    def box(self, that):
        if isinstance(that, Object): return that
        if isinstance(that, str): return S(that)
        raise TypeError(['box', type(that), that])

    def __repr__(self):
        return self.dump()

    def __format__(self, spec):
        return self.val()

    def tag(self): return self.__class__.__name__.lower()
    def val(self): return f'{self.value}'

    def __floordiv__(self, that):
        self.nest.append(self.box(that)); return self

    def __iter__(self): return iter(self.nest)

class Primitive(Object): pass

class S(Primitive):
    def __init__(self, V=None, end=None, pfx=None, sfx=None):
        super().__init__(V)
        self.end = end; self.pfx = pfx; self.sfx = sfx

    def gen(self, to, depth=0):
        assert isinstance(to, File)
        ret = ''
        if self.pfx is not None:
            ret += f'{to.tab*depth}{self.pfx}\n' if self.pfx else '\n'
        if self.value is not None:
            ret += f'{to.tab*depth}{self}\n'
        for i in self:
            ret += i.gen(to, depth + 1)
        if self.end is not None:
            ret += f'{to.tab*depth}{self.end}\n'
        if self.sfx is not None:
            ret += f'{to.tab*depth}{self.sfx}\n' if self.sfx else '\n'
        return ret

class Sec(S):
    def gen(self, to, depth=0):
        ret = ''
        if self.nest:
            if self.pfx is not None:
                ret += f'{to.tab*depth}{self.pfx}\n' if self.pfx else '\n'
            if self.value is not None:
                ret += f'{to.tab*depth}{to.comment} \\ {self}\n'
            for i in self:
                ret += i.gen(to, depth + 0)
            if self.value is not None:
                ret += f'{to.tab*depth}{to.comment} / {self}\n'
            if self.sfx is not None:
                ret += f'{to.tab*depth}{self.sfx}\n' if self.sfx else '\n'
        return ret

class Container(Object): pass

class Active(Object): pass

class Fn(Active):
    def __init__(self, V, args=[]):
        super().__init__(V)
        self.args = args

    def gen(self, to, depth=0):
        ret = to.fn(self, depth)
        for i in self: ret // i.gen(to, depth + 1)
        return ret.gen(to, depth)

class Meta(Object): pass

class Class(Meta):
    def __init__(self, C, sup=[]):
        assert callable(C)
        super().__init__(C.__name__)
        self.sup = sup

    def gen(self, to, depth=0):
        ret = to.clazz(self, depth)
        for i in self: ret // i.gen(to, depth + 1)
        return ret.gen(to, depth)


class Project(Meta):
    def __init__(self, V=None):
        if not V: V = os.getcwd().split('/')[-1]
        super().__init__(V)
        self.mod = []
        self.dirs()
        self.metainfo()
        self.mk()
        self.apt()
        self.giti()

    def giti(self):
        self.giti = giti(); self.d // self.giti
        self.giti // (Sec(sfx='') // '*~' // '*.swp' // '*.log')
        self.giti // (Sec(sfx='') // f'/docs/' // f'/{self}/')

    def metainfo(self):
        self.TITLE = f'{self}'
        self.AUTHOR = 'Dmitry Ponyatov'
        self.EMAIL = 'dponyatov@gmail.com'
        self.YEAR = 2020
        self.LICENSE = 'All rights reserved'
        self.GITHUB = 'https://bitbucket.org/ponyatov'

    def apt(self):
        self.apt = File('apt', '.txt'); self.d // self.apt
        self.apt // 'git make curl' // 'code meld doxygen' // 'python3 python3-pip python3-venv'

    def __or__(self, that):
        return that.pipe(self)

    def sync(self):
        self.readme()
        self.d.sync()

    def dirs(self):
        self.d = Dir(f'{self}')
        #
        self.vscode()
        self.bin()
        self.doc()
        self.lib()
        self.src()
        self.tmp()

    def vscode(self):
        self.vscode = Dir('.vscode'); self.d // self.vscode
        self.settings()
        self.extensions()
        self.tasks()

    def settings(self):
        self.settings = jsonFile('settings'); self.vscode // self.settings

        def multi(key, cmd): return \
            (S('{', '},')
                // f'"command": "multiCommand.{key}",'
                // (S('"sequence": [')
                    // '"workbench.action.files.saveAll",'
                    // '{"command": "workbench.action.terminal.sendSequence",'
                    // f'    "args": {{"text": "\\u000D clear ; LANG=C {cmd} \\u000D"}}}}]'
                    ))
        #
        exclude = (S('"files.exclude": {', '},')
                   // f'"**/{self}/**":true,')
        watcher = (S('"files.watcherExclude": {', '},'))
        for i in ['docs']:
            mask = f'"**/{i}/**":true,'
            exclude // mask; watcher // mask
        assoc = (S('"files.associations": {', '},'))
        files = Sec('files', pfx='') // exclude // watcher // assoc
        #
        editor = (Sec('editor', pfx='')
                  // '"editor.tabSize": 4,'
                  // '"editor.rulers": [80],'
                  // '"workbench.tree.indent": 32,')
        self.settings // (S('{', '}')
                          // (S('"multiCommand.commands": [', '],')
                              // multi('f12', 'make all')
                              )
                          // files
                          // editor)

    def extensions(self):
        self.extensions = jsonFile('extensions')
        self.vscode // self.extensions

    def tasks(self):
        self.tasks = jsonFile('tasks'); self.vscode // self.tasks

    def bin(self):
        self.bin = Dir('bin'); self.d // self.bin
        self.bin.giti = giti(); self.bin // (self.bin.giti // '*')

    def doc(self):
        self.doc = Dir('doc'); self.d // self.doc
        self.doc.giti = giti(); self.doc // (self.doc.giti // '*.pdf')

    def lib(self):
        self.lib = Dir('lib'); self.d // self.lib
        self.lib.giti = giti(); self.lib // self.lib.giti

    def src(self):
        self.src = Dir('src'); self.d // self.src
        self.src.giti = giti(); self.src // (self.src.giti // '*-*/')

    def tmp(self):
        self.tmp = Dir('tmp'); self.d // self.tmp
        self.tmp.giti = giti(); self.tmp // (self.tmp.giti // '*')

    def readme(self):
        self.readme = File('README.md'); self.d // self.readme
        (self.readme
            // f'#  {self}'
            // f'## {self.TITLE}'
            // ''
            // f'(c) {self.AUTHOR} <<{self.EMAIL}>> {self.YEAR} {self.LICENSE}'
            // ''
            // f'github: {self.GITHUB}/{self}/')

    def mk(self):
        self.mk = Makefile(); self.d // self.mk
        #
        self.mk.var = Sec('var'); self.mk // self.mk.var
        (self.mk.var
         // 'MODULE  = $(notdir $(CURDIR))'
         // 'OS      = $(shell uname -o|tr / _)'
         // 'NOW     = $(shell date +%d%m%y)'
         // 'REL     = $(shell git rev-parse --short=4 HEAD)'
         // 'BRANCH  = $(shell git rev-parse --abbrev-ref HEAD)'
         // 'PEPS    = E26,E302,E305,E401,E402,E701,E702')
        #
        self.mk.version = Sec('version', pfx=''); self.mk // self.mk.version
        #
        self.mk.dir = Sec('dir', pfx=''); self.mk // self.mk.dir
        #
        self.mk.tool = Sec('tool', pfx=''); self.mk // self.mk.tool
        (self.mk.tool
         // 'CURL    = curl -L -o'
         // 'CF      = clang-format-11 -style=file -i'
         // 'PY      = $(shell which python3)'
         // 'PIP     = $(shell which pip3)'
         // 'PEP     = $(shell which autopep8) --ignore=$(PEPS) --in-place')
        #
        self.mk.src = Sec('src', pfx=''); self.mk // self.mk.src
        (self.mk.src
         // 'Y += $(MODULE).py'
         // 'S += $(Y)')
        #
        self.mk.cfg = Sec('cfg', pfx=''); self.mk // self.mk.cfg
        #
        self.mk.all = Sec('all', pfx=''); self.mk // self.mk.all
        (self.mk.all
         // (S('all: $(PY) $(MODULE).py')
             // '$^' // '$(MAKE) tmp/format_py'))
        #
        self.mk.format = Sec('format', pfx=''); self.mk // self.mk.format
        (self.mk.format
         // (S('tmp/format_py: $(Y)')
             // '$(PEP) $? && touch $@'))
        #
        self.mk.rule = Sec('rule', pfx=''); self.mk // self.mk.rule
        #
        self.mk.doc = Sec('doc', pfx=''); self.mk // self.mk.doc
        #
        self.mk.install = Sec('install', pfx=''); self.mk // self.mk.install
        #
        self.mk.merge = Sec('merge', pfx=''); self.mk // self.mk.merge


class IO(Object):
    def __init__(self, V):
        super().__init__(V)
        self.path = V

class Dir(IO):
    def __floordiv__(self, that):
        that.path = f'{self.path}/{that.path}'
        return super().__floordiv__(that)

    def sync(self):
        try: os.mkdir(self.path)
        except FileExistsError: pass
        for i in self: i.sync()

class File(IO):
    def __init__(self, V, ext='', tab=' ' * 4, comment='#'):
        super().__init__(V + ext)
        self.tab = tab; self.comment = comment
        self.top = Sec()
        self.bot = Sec()

    def sync(self):
        with open(self.path, 'w') as F:
            F.write(self.top.gen(self))
            for i in self: F.write(i.gen(self))
            F.write(self.bot.gen(self))

class giti(File):
    def __init__(self, V='', ext='.gitignore'):
        super().__init__(V, ext)
        self.bot // '!.gitignore'

class jsonFile(File):
    def __init__(self, V, ext='.json', comment='//'):
        super().__init__(V, ext, comment=comment)

class pyFile(File):
    def __init__(self, V, ext='.py'):
        super().__init__(V, ext)

    def clazz(self, clazz, depth):
        sup = list(map(lambda i: i.__name__, clazz.sup))
        sup = '(%s)' % ', '.join(sup) if sup else ''
        pazz = ' pass' if not clazz.nest else ''
        ret = S(f'class {clazz}{sup}:{pazz}', pfx='')
        return ret

    def fn(self, fn, depth):
        args = ', '.join(fn.args)
        ret = S(f'def {fn}({args}):')
        return ret

class Makefile(File):
    def __init__(self, V='Makefile', ext='', tab='\t'):
        super().__init__(V, ext, tab=tab)

class Mod(Meta):
    def __init__(self, V=None):
        if not V: V = self.tag()
        super().__init__(V)

    def pipe(self, p):
        p.mod += [self.__class__]
        self.src(p)
        return p

    def src(self, p): pass

class Py(Mod):
    def src(self, p):
        p.py = pyFile(f'{p}'); p.d // p.py
        p.py.imports = (Sec(sfx='')); p.py // p.py.imports

class metaL(Mod):
    def src(self, p):
        assert Py in p.mod
        p.py.imports // 'import os, sys'
        p.py.object = Class(Object)
        (p.py.object
            // (Sec()
                // Fn('__init__', ['self', 'V'])
                // Fn('box', ['self', 'that'])
                )
            // (Sec()
                // Fn('__repr__', ['self'])
                // Fn('__format__', ['self', 'spec'])
                )

         )
        p.py // p.py.object
        #
        p.py // Class(Primitive, [Object])
        #
        p.py.s = (Class(S, [Primitive])
                  // Fn('__init__', ['self', 'V=None', 'end=None', 'pfx=None', 'sfx=None'])
                  // Fn('gen', ['self', 'to', 'depth=0']))
        p.py // p.py.s
        #
        p.py.sec = (Class(Sec, [S])
                    // Fn('gen', ['self', 'to', 'depth=0'])
                    )
        p.py // p.py.sec
        #
        p.py // Class(Container, [Object])
        #
        p.py // Class(Active, [Object])
        p.py // (Class(Fn, [Active])
                 // Fn('__init__', ['self', 'V', 'args=[]'])
                 // Fn('gen', ['self', 'to', 'depth=0'])
                 )
        #
        p.py // Class(Meta, [Object])
        p.py // (Class(Class, [Meta])
                 // Fn('__init__', ['self', 'C', 'sup=[]']))
        p.py // Class(Project, [Meta])
        #
        p.py // (Class(IO, [Object])
                 // Fn('__init__', ['self', 'V', 'ext', "tab=' '*4", "comment='#'"])
                 )
        p.py // (Class(Dir, [IO])
                 // Fn('sync', ['self']))
        p.py // (Class(File, [IO])
                 // Fn('sync', ['self']))
        p.py // (Class(giti, [File])
                 // Fn('__init', ['self']))
        p.py // (Class(Makefile, [File])
                 // Fn('__init', ['self', "V='Makefile'", "ext=''", "tab='\\t'"]))
        p.py // (Class(jsonFile, [File])
                 // Fn('__init', ['self']))
        p.py // (Class(pyFile, [File])
                 // Fn('__init', ['self']))
        #
        p.py // Class(Mod, [Meta])
        p.py // Class(Py, [Mod])
        p.py // Class(metaL, [Mod])

if __name__ == '__main__':
    p = Project() | Py() | metaL()
    p.TITLE = 'lowCode platform'
    p.sync()
