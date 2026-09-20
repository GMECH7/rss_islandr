# Risk Screening System (RSS) - ISLANDR

RSS-ISLANDR is a desktop application for the screening of contaminated land. It was conceived as a Python-based implementation of the Risk Screening System (RSS) of the [New Zealand Ministry for the Environment](https://environment.govt.nz/publications/contaminated-land-management-guidelines-no-3-risk-screening-system/), developed for [CERTH](https://www.certh.gr/) under the [ISLANDR](https://islandr-project.eu/) project.

The system evaluates environmental risk with the Source-Pathway-Receptor (SPR) model. The risk is the product of three components:

1. **Source (hazard):** the origin of the potential contamination.
2. **Pathway:** the route through which the hazard reaches the receptor (soil, groundwater, surface water, air, sediment).
3. **Receptor:** the entity that may be affected, for example a water resource or an ecosystem.

## Documentation

The documentation is split into three parts:

1. [Local development](docs/local-development.md): For developers. Setting up the environment, the project layout, the available commands, testing, and the automated GitHub workflows.
2. [Installers](docs/installers.md): For end users and maintainers. How to download, install and uninstall the application on Ubuntu and Windows, and how the installers are built.
3. [Features](docs/features.md): For users and reviewers. An overview of the methodology and of the features of the application. The user interface, the map viewer, and the reports and files it produces.

## Quick start

End users can download the installer for Windows 10/11 or Ubuntu 24.04 from the [Releases page](https://github.com/GMECH7/rss_islandr/releases). Installation and checksum commands are in [Installers](docs/installers.md#4-downloading-a-release-from-github).

Developers and contributors to this project should use the following commands:

```bash
git clone https://github.com/GMECH7/rss_islandr.git
```
```bash
cd rss_islandr
```
```bash
poetry install
```
```bash
poetry run islandr
```

The prerequisites (Python, Poetry and, on Ubuntu, system libraries) are listed in [Local development](docs/local-development.md#1-prerequisites).

## Requirements

| | |
|---|---|
| Operating system | Windows 10/11 or Ubuntu 24.04 and later (when using the installers). macOS is untested |
| Python | 3.12 to 3.14, only when running from the source code |
| Internet connection | Needed only for the map viewer. All other functions work offline |

## References

- **New Zealand Ministry for the Environment**: [Contaminated Land Management Guidelines No. 3 - Risk Screening System](https://environment.govt.nz/publications/contaminated-land-management-guidelines-no-3-risk-screening-system/).
- **Source-Pathway-Receptor (SPR) model**: A foundational framework for environmental risk assessment.

## Acknowledgements

Funded by the European Union, Grant agreement n°1001112889 (ISLANDR project).

Views and opinions expressed are however those of the author(s) only and do not necessarily reflect those of the European Union or the European Climate, Infrastructure and Environment Executive Agency (CINEA). Neither the European Union nor the granting authority can be held responsible for them.

## License

This project is released under the [MIT License](LICENSE). Copyright (c) 2025 CERTH.
