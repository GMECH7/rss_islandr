"""Creates version_info.txt from the version in pyproject.toml (also done by `poetry run rss-build`)."""

from build_tools.version import read_version, write_version_info

if __name__ == "__main__":
    version = read_version()
    write_version_info(version)
    print(f"Generated version_info.txt for version: {version}")
