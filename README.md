# PALM User Guide – Supporting Files

This repository provides supporting files referenced in the PALM User Guide:

👉 https://github.com/CHMI-AQ-modelling-department/palm-user-guide

The purpose of this repository is to ensure that all configuration files,
scripts, and example inputs used in the guide are publicly available and
accessible through stable links.

---

## Purpose

The PALM User Guide includes many practical examples such as:

- configuration files (`.yaml`, `.conf`)
- preprocessing scripts
- postprocessing scripts
- example input datasets

Instead of embedding these files directly in the document, they are stored
here and referenced via URLs. This approach ensures that:

- links in the guide remain valid over time
- users can directly download and reuse the files
- workflows described in the guide can be reproduced

---

## Scope of the Repository

This repository is **not intended to be installed as software**.

Instead, it serves as a collection of:

- example configuration files for PALM simulations
- scripts used in preprocessing (e.g. static driver, emissions, transport)
- scripts used in postprocessing (e.g. time series, spatial maps, performance)
- auxiliary files required for running workflows described in the guide

---

## Repository Structure

The repository is organized according to the workflow presented in the user guide:

static_driver/
configuration files and scripts for PALM-GeM

emissions/
scripts and configuration related to emission preprocessing (e.g. FUME)

transportation/
scripts for traffic intensity and transport inputs

post_processing/
time_series_analysis/
spatial_distributions/
utilities/

palm_configuration/
sample YAML and configuration files

Each file is referenced in the guide where it is used.

---

## Usage

Files in this repository are intended to be:

- downloaded individually
- adapted to the user’s own simulation setup
- used together with the instructions provided in the user guide

Example:

```bash
wget https://raw.githubusercontent.com/CHMI-AQ-modelling-department/palm-user-guide/main/post_processing/time_series_analysis/default_config.yaml
