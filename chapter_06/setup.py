from cx_Freeze import setup, Executable


base = None

executables = [Executable("wormy.py", base=base)]

packages = ["idna"]
options = {
    'build_exe': {
        'packages': packages,
    },

}

setup(
    name="Worm-E",
    options=options,
    version="1.0",
    description='<any description>',
    executables=executables
)
