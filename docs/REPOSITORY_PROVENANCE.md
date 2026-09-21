# Repository provenance and documentation status

The initial files and Git commit history were copied from `wenping-xie/PREDAC-TransFluB`, at commit `a3f7bb176a16806cfbfc2350b87fd2f63790e3c7`. The original repository is retained.

The new project name is **DeepCTS-B**. Existing script and data filenames are retained to preserve the original repository contents. Legacy names inside inherited scripts have not been rewritten as part of this documentation update.

Added materials:

- `seq/BV_GISAID_accessions.txt`: 6,389 unique EPI accession identifiers, one per line.
- `seq/README.md`: accession evidence and dataset scope.
- `data/HI_data_sources.txt`: all 126 author-supplied report or range entries, with scope and verification notes.
- `data/hi/README.md`: HI source-access route and report-version documentation requirements.
- `data/hi/source_overview.csv`: the source archive named in the manuscript.
- `data/hi/report_manifest.csv`: an unfilled, study-specific report inventory template.

Remaining author checks:

- Reconcile the BY accession inventory (now deposited as the 2,643-identifier prediction-input list) with the final manuscript dataset and supply the original GISAID contributor acknowledgements.
- Supply the exact HI reports and editions actually used from the WIC/Crick and WHO sources.
- The BV and BY `model_20` TensorFlow checkpoints are deposited under `model/BV/model/` and `model/BY/model/`.
- The training and prediction scripts set `seed=100` for the stratified split (`train_test_split` and `StratifiedShuffleSplit`). They do not set global Python, NumPy, or TensorFlow random seeds; therefore this documents deterministic data partitioning, not bitwise-identical retraining.

No new sequence data, model weights, or HI measurements were generated in this update. All original tracked files except the project README are preserved byte-for-byte.
