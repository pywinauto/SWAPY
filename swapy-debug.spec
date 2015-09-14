# -*- mode: python -*-
a = Analysis(['swapy-ob.py'],
             pathex=['swapy-git'])
a.datas += [('swapy_dog_head.ico','swapy_dog_head.ico','DATA'),]
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.datas,
          a.scripts,
          a.binaries,
          a.zipfiles,
          exclude_binaries=False,
          name=os.path.join('dist', 'swapy-debug.exe'),
          debug=True,
          strip=False,
          upx=False,
          console=True,
          icon='swapy_dog.ico')
