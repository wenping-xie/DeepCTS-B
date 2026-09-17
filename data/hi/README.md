# HI data sources and report versions

## Source reported in the manuscript

The manuscript states that influenza B haemagglutination inhibition (HI) data were obtained from the annual and interim reports of the Worldwide Influenza Centre (WIC), The Francis Crick Institute.

- [WIC annual and interim reports](https://www.crick.ac.uk/research/platforms-and-facilities/worldwide-influenza-centre/annual-and-interim-reports)
- [WIC source overview](source_overview.csv)

Use the source archive to locate the original reports. A link to the archive identifies the data provider, but does not identify the exact reports or revised editions used in this study.

## Author-supplied source catalogue

[HI_data_sources.txt](../HI_data_sources.txt) preserves all 126 report or range entries supplied by the author across WIC/NIMR, New Zealand surveillance, ECDC, FDA, and WHO. The list includes A/H3N2 and A/H1N1 resource groups and does not establish which entries were used for the influenza B manuscript.

## Study-specific version inventory: pending

A catalogue of report titles and dates has now been supplied, but the subset actually used in this study, original PDF URLs, exact editions/revisions, and relevant tables/pages have not yet been confirmed. The historical download dates are also unknown. The archive landing page returned HTTP 403 during this audit, so its current report inventory was not inspected.

[report_manifest.csv](report_manifest.csv) currently contains column headings only. No report has been asserted to be part of the study without supporting source records. Add one row for each report edition actually used, using the original report and download records as evidence:

- Record the title, issuing institution, original report URL, and publication date as printed on the report.
- Record the revision date or edition separately, when present. If no revision is identified, state `not stated` rather than inventing one.
- Preserve date precision (`year`, `month`, or `day`). Do not invent a day for a report that states only a month or year.
- Distinguish the historical access/download date from the report publication date. Use `unknown` when the original access date cannot be recovered.
- Identify the tables/pages and lineage(s) used, and record the local source filename and SHA-256 digest when available.

An archive year, a virus collection date, and the date of this repository update must not be substituted for a report version date. The inherited CSV files are preserved from the original repository; they do not by themselves establish the exact source reports or versions.

This documentation provides the source-access route. It does not yet satisfy the reviewer's request for an exact, study-specific HI report version inventory.
