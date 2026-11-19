# Genin2 changelog

## Version 2.1.8, 19/11/2026

- Fix FD and FE genotypes not being recognized

## Version 2.1.7, 18/11/2026

- Add genotypes: **EA-2026-FA**, **EA-2026-FB**, **EA-2026-FC**, **EA-2025-FD**, **EA-2026-FE**
- When parsing input samples, accept `M` as alias for `MP`
- In the output, use clearer flags for unassigned segments:
  - `?/m`: missing; the segment was not found in the input file
  - `?/q`: low quality; valid nucleotides are too few w.r.t. reference
  - `?/n`: nucleotide error; invalid characters found in the sequence
  - `?/u`: unassigned; the model failed to identify a cluster with proper confidence
  - `?/?`: a more generic, unexpected internal error has occurred

## Version 2.1.6, 08/04/2026

- Add genotype: **EA-2024-DV**

## Version 2.1.5, 14/11/2025

- Fix a critical bug introduced in v2.1.4 that labelled all samples as "unassigned"

## Version 2.1.4, 14/11/2025

- Add subgenotype: `DI.2.1`
- Improve overall accuracy

## Version 2.1.2, 08/04/2025

- Add genotype: **EA-2025-EG**

## Version 2.1.0, 01/04/2025

- Add genotype: **EA-2024-EF**
- Add `Subgenotype` column to output data
- Add `DI`, `DI.1`, and `DI.2` to the recognized sub-genotypes
- Removed confidence values as they were too little correlated and therefore misleading

## Version 2.0.3, 20/02/2025

- Add genotype: **EA-2024-EE**
- Add automatic check and notification for new version availability

## Version 2.0.0, 18/02/2025

- Initial release
