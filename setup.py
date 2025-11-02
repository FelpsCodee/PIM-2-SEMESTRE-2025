from cx_Freeze import setup, Executable

build_exe_options = {
    "packages": ["mysql.connector"],
    "include_files": ["meutemplate.py"],
}

setup(
    name="MeuPrograma",
    version="1.0",
    description="Sistema de Estoque",
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base="Win32GUI")]
)