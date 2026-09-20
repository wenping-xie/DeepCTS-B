# GISAID accession inventory

[BV_GISAID_accessions.txt](BV_GISAID_accessions.txt) contains 6,389 unique B/Victoria HA sequence accession identifiers, one per line.

[BY_GISAID_accessions.txt](BY_GISAID_accessions.txt) contains 2,643 unique EPI identifiers extracted from the BY prediction input used for the antigenic-cluster analysis. The identifiers were collected from the `new_name_1` and `new_name_2` columns of the supplied BY input CSV; non-EPI vaccine or strain names were excluded. The source file was `BY-HA1-seq-and-BY-vaccine-seq-new-UNIQUE-11-27_alltopredict3600586-replaced-beijing184.csv`.

## Status: partial inventory under review

- 6,365 identifiers were retained from the original BV analysis FASTA headers.
- 24 identifiers were added by retrospective matching of compatible strain names and exact ungapped HA1 sequences against the supplied reference FASTA (`BV-1987-20260525-filtered.fasta`). These matches do not independently establish the historical download provenance.
- Of the 6,410 records in the supplied analysis FASTA, 21 remain unresolved: 12 have multiple candidate identifiers, eight have no exact sequence match, and one has a strain-name discrepancy. Unresolved candidates are excluded from the accession list.

These inventories are not yet claimed to be the complete, finalized accession inventory for all manuscript analyses. The final BV dataset scope remains to be reconciled with the manuscript, and the BY list reflects the supplied prediction input. The date embedded in the BV reference filename is not asserted to be the original study download date.

The file contains accession identifiers only, not sequence data. Access to the corresponding records remains through GISAID under its applicable Database Access Agreement. Contributor acknowledgements and any EPI_SET/DOI reference must be supplied separately.
