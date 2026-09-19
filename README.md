# Risk Screening System (RSS) - ISLANDR

RSS-ISLANDR is a desktop application for the screening of contaminated land. It is a Python implementation of the Risk Screening System (RSS) of the [New Zealand Ministry for the Environment](https://environment.govt.nz/publications/contaminated-land-management-guidelines-no-3-risk-screening-system/), developed for CERTH under the ISLANDR project.

The system evaluates environmental risk with the Source-Pathway-Receptor (SPR) model. The risk is the product of three components:

1. **Source (hazard):** the origin of the potential contamination.
2. **Pathway:** the route through which the hazard reaches the receptor (soil, groundwater, surface water, air, sediment).
3. **Receptor:** the entity that may be affected, for example a water resource or an ecosystem.

The application is a screening tool for desk studies and the prioritisation of sites. It does not replace a site investigation or a quantitative risk assessment.

## Documentation

| Document | Contents |
|---|---|
| [Features](docs/features.md) | The method and the equation, the pages and parameters of the application, the map viewer and its map services, the reports and files, and the limitations |
| [Local development](docs/local-development.md) | Installing Poetry and the dependencies, the project layout, the commands, the tests, the version, the GitHub workflows and how a release is created |
| [Installers](docs/installers.md) | Building the Ubuntu and Windows installers locally, installing and uninstalling them, and downloading a release from GitHub with the checksum check |

## Quick start

**Users:** download the installer for Windows 10/11 or Ubuntu 24.04 and later from the [Releases page](https://github.com/GMECH7/rss_islandr/releases). Installation and checksum commands are in [Installers](docs/installers.md#4-downloading-a-release-from-github).

**Developers:**

```bash
git clone https://github.com/GMECH7/rss_islandr.git
cd rss_islandr
poetry install --with dev,build
poetry run islandr
```

The prerequisites (Python, Poetry and, on Ubuntu, system libraries) are listed in [Local development](docs/local-development.md#1-prerequisites).

## Requirements

| | |
|---|---|
| Operating system | Windows 10/11 or Ubuntu 24.04 and later (the installers). macOS is untested |
| Python | 3.12 to 3.14, only when running from the source code |
| Internet connection | Needed only for the map viewer. All other functions work offline |
| Microsoft Excel | Not required. The Excel reports are written directly |

## References

- New Zealand Ministry for the Environment, [Contaminated Land Management Guidelines No. 3 - Risk Screening System](https://environment.govt.nz/publications/contaminated-land-management-guidelines-no-3-risk-screening-system/).
- The Source-Pathway-Receptor (SPR) model, a general framework for environmental risk assessment.

## Acknowledgements

Funded by the European Union, Grant agreement n°1001112889 (ISLANDR project).

Views and opinions expressed are however those of the author(s) only and do not necessarily reflect those of the European Union or the European Climate, Infrastructure and Environment Executive Agency (CINEA). Neither the European Union nor the granting authority can be held responsible for them.

## License

This project is released under the [MIT License](LICENSE). Copyright (c) 2025 CERTH.
