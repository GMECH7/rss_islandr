import re
import tomllib
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent


def read_pyproject() -> dict:
    with open(ROOT_DIR / "pyproject.toml", "rb") as pyproject_file:
        return tomllib.load(pyproject_file)["tool"]["poetry"]


def read_version() -> str:
    """Version of the app (`version` in pyproject.toml), e.g. '2.0.0'."""
    version = read_pyproject()["version"]
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError(f"Version must have the form X.Y.Z, got '{version}'")
    return version


def write_version_info(version: str) -> Path:
    """Write the file with the Windows file properties of the executable (used by islandr.spec)."""
    version_tuple = tuple(map(int, version.split("."))) + (0,)
    version_info = f"""# UTF-8
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers={version_tuple},
    prodvers={version_tuple},
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo([StringTable(
      '040904B0',
      [
        StringStruct('CompanyName', 'CERTH'),
        StringStruct('FileDescription', 'Risk Screening System (RSS) developed under the ISLANDR research project'),
        StringStruct('FileVersion', '{version}'),
        StringStruct('ProductName', 'RSS ISLANDR'),
        StringStruct('ProductVersion', '{version}'),
        StringStruct('LegalCopyright', 'Copyright © 2025 CERTH'),
        StringStruct('OriginalFilename', 'islandr.exe'),
      ])
    ]),
    VarFileInfo([VarStruct('Translation', [0x409, 1200])])
  ]
)"""
    output_file = ROOT_DIR / "version_info.txt"
    output_file.write_text(version_info, encoding="utf-8")
    return output_file


if __name__ == "__main__":
    app_version = read_version()
    write_version_info(app_version)
    print(f"Generated version_info.txt for version: {app_version}")
