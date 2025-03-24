from pathlib import Path

import toml


def main():
    pyproject = toml.load("pyproject.toml")

    # Get release version if exists, otherwise fall back to dev version
    release_version = (
        pyproject.get("tool", {}).get("islandr", {}).get("release_version")
        or pyproject["tool"]["poetry"]["release_version"]
    )

    version_info = f"""# UTF-8
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers={tuple(map(int, release_version.split("."))) + (0,)},
    prodvers={tuple(map(int, release_version.split("."))) + (0,)},
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
        StringStruct('FileVersion', '{release_version}'),
        StringStruct('ProductName', 'RSS ISLANDR'),
        StringStruct('ProductVersion', '{release_version}'),
        StringStruct('LegalCopyright', 'Copyright © 2025 CERTH'),
        StringStruct('OriginalFilename', 'islandr.exe'),
      ])
    ]),
    VarFileInfo([VarStruct('Translation', [0x409, 1200])])
  ]
)"""

    Path("version_info.txt").write_text(version_info, encoding="utf-8")
    print(f"Generated version_info.txt for version: {release_version}")


if __name__ == "__main__":
    main()
