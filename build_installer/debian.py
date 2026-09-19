import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image
from rich.console import Console

from build_installer.common import APP_DIR, DIST_DIR, BuildError, build_app, run
from build_installer.version import ROOT_DIR, read_pyproject

PACKAGE_NAME = "rss-islandr"
INSTALL_DIR = f"/opt/{PACKAGE_NAME}"
ARCHITECTURE = "amd64"

#: Ubuntu 24.04 is the oldest supported system. The build image and the first test image.
BUILD_IMAGE_TAG = "rss-islandr-build:ubuntu24.04"
TEST_IMAGES = ["ubuntu:24.04", "ubuntu:26.04"]

#: System libraries needed by the bundled Qt WebEngine (map viewer) and the Qt/Tk windows.
DEPENDS = [
    "libasound2t64",
    "libatk-bridge2.0-0t64",
    "libatk1.0-0t64",
    "libcups2t64",
    "libdbus-1-3",
    "libdrm2",
    "libegl1",
    "libfontconfig1",
    "libgbm1",
    "libgl1",
    "libnspr4",
    "libnss3",
    "libwayland-client0",
    "libwayland-cursor0",
    "libwayland-egl1",
    "libx11-xcb1",
    "libxcb-cursor0",
    "libxcb-icccm4",
    "libxcb-image0",
    "libxcb-keysyms1",
    "libxcb-randr0",
    "libxcb-render-util0",
    "libxcb-shape0",
    "libxcb-xinerama0",
    "libxcb-xkb1",
    "libxcomposite1",
    "libxdamage1",
    "libxfixes3",
    "libxkbcommon-x11-0",
    "libxkbcommon0",
    "libxrandr2",
    "libxtst6",
]

DESKTOP_ENTRY = f"""[Desktop Entry]
Type=Application
Name=RSS-ISLANDR
Comment=Risk Screening System (ISLANDR project)
Exec={PACKAGE_NAME}
Icon={PACKAGE_NAME}
Terminal=false
Categories=Science;Geology;
"""


def deb_path(version: str) -> Path:
    return DIST_DIR / f"{PACKAGE_NAME}_{version}_{ARCHITECTURE}.deb"


def _stage_package(stage_dir: Path, version: str) -> None:
    """Create the file tree of the package."""
    shutil.copytree(APP_DIR, stage_dir / INSTALL_DIR.lstrip("/"), symlinks=True)

    bin_dir = stage_dir / "usr" / "bin"
    bin_dir.mkdir(parents=True)
    (bin_dir / PACKAGE_NAME).symlink_to(f"{INSTALL_DIR}/islandr")

    applications_dir = stage_dir / "usr" / "share" / "applications"
    applications_dir.mkdir(parents=True)
    (applications_dir / f"{PACKAGE_NAME}.desktop").write_text(DESKTOP_ENTRY, encoding="utf-8")

    icon_dir = stage_dir / "usr" / "share" / "icons" / "hicolor" / "256x256" / "apps"
    icon_dir.mkdir(parents=True)
    with Image.open(ROOT_DIR / "rss_islandr" / "static" / "islandr.ico") as icon:
        icon.convert("RGBA").resize((256, 256)).save(icon_dir / f"{PACKAGE_NAME}.png")

    doc_dir = stage_dir / "usr" / "share" / "doc" / PACKAGE_NAME
    doc_dir.mkdir(parents=True)
    shutil.copy(ROOT_DIR / "LICENSE", doc_dir / "copyright")

    installed_size_kb = sum(f.stat().st_size for f in stage_dir.rglob("*") if f.is_file()) // 1024
    project = read_pyproject()
    control = f"""Package: {PACKAGE_NAME}
Version: {version}
Section: science
Priority: optional
Architecture: {ARCHITECTURE}
Depends: {", ".join(DEPENDS)}
Installed-Size: {installed_size_kb}
Maintainer: {project["authors"][0]}
Homepage: https://github.com/GMECH7/rss_islandr
Description: Risk Screening System (RSS) of the ISLANDR project
 Screening tool for contaminated land based on the source-pathway-receptor
 model. Includes a map viewer, and PDF and Excel reports.
"""
    control_dir = stage_dir / "DEBIAN"
    control_dir.mkdir()
    (control_dir / "control").write_text(control, encoding="utf-8")


def build_deb(console: Console) -> Path:
    """Build the Debian package (only on Linux)."""
    if not sys.platform.startswith("linux"):
        raise BuildError("--deb can only be built on Linux (use --docker on other systems that have Docker)")
    version = build_app(console)

    console.rule("Creating the Debian package")
    output_file = deb_path(version)
    with tempfile.TemporaryDirectory() as tmp_dir:
        stage_dir = Path(tmp_dir) / "stage"
        stage_dir.mkdir()
        _stage_package(stage_dir, version)
        run(console, ["dpkg-deb", "--build", "--root-owner-group", "-Zxz", "-z6", stage_dir, output_file])
    return output_file


def build_deb_in_docker(console: Console) -> Path:
    """Build the package in the Ubuntu 24.04 image (same environment as in GitHub Actions)."""
    version = build_version()  # Read once: the container builds from a copy of the current files
    console.rule("Building the Docker image (Ubuntu 24.04)")
    run(console, ["docker", "build", "-t", BUILD_IMAGE_TAG, "-f", "build_installer/docker/Dockerfile.build", "build_installer/docker"])

    console.rule("Building the package in the container")
    DIST_DIR.mkdir(exist_ok=True)
    user = subprocess.run(["id", "-u"], capture_output=True, text=True).stdout.strip()
    group = subprocess.run(["id", "-g"], capture_output=True, text=True).stdout.strip()
    run(
        console,
        [
            "docker", "run", "--rm",
            "--user", f"{user}:{group}",
            "-v", f"{ROOT_DIR}:/src",
            BUILD_IMAGE_TAG,
            "bash", "/src/build_installer/docker/build-deb.sh",
        ],
    )  # fmt: skip
    return deb_path(version)


def build_version() -> str:
    from build_installer.version import read_version

    return read_version()


def test_deb(console: Console, package_file: Path) -> None:
    """Install the package in clean containers and run the self-test and the map process there."""
    if not package_file.exists():
        raise BuildError(f"{package_file} does not exist. Build it first with --deb")

    map_payload = (
        '{"map_html": "/opt/rss-islandr/_internal/maps/index.html", "background_color": "#222", "polygons": [], '
        '"lat": null, "lng": null, "crs": "", "result_file": "/tmp/map_state.json"}'
    )
    script = f"""set -e
apt-get update -qq
DEBIAN_FRONTEND=noninteractive apt-get install -y -qq xvfb /pkg/{package_file.name} > /dev/null
echo "--- self-test"
xvfb-run -a {PACKAGE_NAME} --self-test
echo "--- system libraries"
export LD_LIBRARY_PATH={INSTALL_DIR}/_internal:{INSTALL_DIR}/_internal/PyQt6/Qt6/lib
# The GTK theme plugin and the audio libraries of Qt are optional and not installed on purpose
missing=$(find {INSTALL_DIR} \\( -name "*.so" -o -name "*.so.*" -o -name QtWebEngineProcess \\) -type f \\
    | xargs ldd 2>/dev/null | grep "not found" | grep -Ev "libpulse|libgtk-3|libgdk|libcairo|libpango|libharfbuzz" || true)
if [ -n "$missing" ]; then echo "Missing system libraries:"; echo "$missing"; exit 1; fi
unset LD_LIBRARY_PATH
echo "--- map process (must still run after 10 s and have written its state)"
echo '{map_payload}' > /tmp/payload.json
set +e
xvfb-run -a timeout 10 {PACKAGE_NAME} --map-process < /tmp/payload.json
code=$?
set -e
[ "$code" = 124 ] && [ -f /tmp/map_state.json ]
echo "--- remove"
apt-get remove -y -qq {PACKAGE_NAME} > /dev/null
[ ! -e {INSTALL_DIR} ]
echo "Package test passed"
"""
    for image in TEST_IMAGES:
        console.rule(f"Testing {package_file.name} on {image}")
        run(console, ["docker", "run", "--rm", "-v", f"{package_file.parent}:/pkg:ro", image, "bash", "-c", script])
    console.print("[green]The package works on all test images[/green]")
