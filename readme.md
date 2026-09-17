# DeepCTS-B: Transformer-Based Deep Learning for Prioritizing Candidate Sites Associated with Influenza B Antigenic Cluster Transitions

This repository contains the code and accompanying data documentation for **DeepCTS-B: Transformer-Based Deep Learning for Prioritizing Candidate Sites Associated with Influenza B Antigenic Cluster Transitions**. It preserves the files and Git history of [PREDAC-TransFluB](https://github.com/wenping-xie/PREDAC-TransFluB).

## Data availability

- **GISAID accession identifiers:** [BV accession list](seq/BV_GISAID_accessions.txt), containing 6,389 unique EPI identifiers. This is a **partial inventory under review**: 21 of the 6,410 records in the supplied BV analysis FASTA remain unresolved. See [scope and matching evidence](seq/README.md). The BY inventory and contributor acknowledgement table remain to be supplied.
- **HI data access:** [author-supplied report/source catalogue](data/HI_data_sources.txt), [source-access instructions](data/hi/README.md) and [source overview](data/hi/source_overview.csv). The study-specific [report version inventory](data/hi/report_manifest.csv) is pending confirmation of the actual report editions used; it currently contains column headings only.
- **Migration and outstanding resources:** [repository provenance](docs/REPOSITORY_PROVENANCE.md). This update does not claim that trained weights, the original environment file, or analysis-specific seeds have been deposited.

## Contents

```
.
├── csv/                         # Original input data files
├── external/                    # Original AAIndex spreadsheets
├── script/                      # Original analysis scripts
├── seq/
│   ├── sequence.fasta           # Original example file
│   ├── BV_GISAID_accessions.txt # Partial BV identifier inventory
│   └── README.md                # Identifier scope and limitations
├── data/
│   ├── HI_data_sources.txt      # Author-supplied resource catalogue
│   └── hi/
│       ├── README.md            # HI source-access documentation
│       ├── source_overview.csv  # Source archive
│       └── report_manifest.csv # Exact report versions: pending
└── docs/
    └── REPOSITORY_PROVENANCE.md
```

The usage instructions below are inherited from the original repository. This migration preserves those scripts and does not independently validate their execution environment.

---

## System Requirements & Dependencies

The code was developed and tested using Python 3.7.12. To run the scripts, you will need to install the following major libraries. We recommend using a virtual environment (e.g., `conda` or `venv`).


*   `tensorflow=2.7.0`
*   `torch=1.10.1`
*   `scikit-learn=0.19.2`
*   `pandas=1.3.5`
*   `numpy=1.21.6`
*   `keras=2.7.0`

---

### Usage Instructions

1 **Navigate to the `script` directory:**

```
cd script
```

2 **Generate ESM embeddings:**
To generate ESM embeddings for the sequence data, run the following command:

```
python generate_esm.py \
  --seq /path/to/seq/BV_sequences.fasta (BY_sequences.fasta) \
  --datatype BV (or BY) \
  --outdir /path/to/output/directory
```

Install ESM by following the instructions on the [Facebook ESM GitHub repository](https://github.com/facebookresearch/esm).

After installing ESM, you can extract the ESM features using the following command:

```shell
#bash
mkdir -p /path/to/BV_esm_seq (or BY_esm_seq)
esm-extract esm2_t6_8M_UR50D BV_HA1_forhi_sequences.fasta ./esm_seq --repr_layers 0 5 6 --include per_tok
```

3 **Generate Input Matrix:**
After generating ESM embeddings, run the following to generate the input feature matrix:

```python
python generate_matrix.py \
  --aaindex_file /path/to/external/aaindex_feature_BV.txt (or aaindex_feature_BY.txt) \
  --esm_dir /path/to/esm/embeddings \
  --seq_dir /path/to/csv \
  --dir /path/to/csv \
  --thread 50
```

4 **Train the Model:**
To train the PREDAC-TransFluB model, run the following:

```python
 mkdir -p /path/5fold_train
 cd /path/5fold_train
 python3 /path/script/model_train.py
 --shape_0 346 --shape_1 654 \
 --input_dir /path/to/csv \
 --filename input_data.csv.npy \
 --epoch 200 \
 --number_columns 654
```

5 **Make Predictions:**
After training, you can use the model to make predictions on new data:

```python
 for i in 1 2 3 4 5
 do
 echo "fold==${i}"
 mkdir -p /path/5fold_pred_npy
 python3 /path/script/model_predict.py --shape_0 346 --shape_1 654 \
 --input_dir /path/to/csv \
 --filename inputdata_test.csv.npy  \
 --model_path /path/to/model \
 --number_columns 654 \
 --fold ${i} \
 --outdir /path/5fold_pred_npy \
 echo '####################'
 done
```

6 **Cluster Results:**
Finally, you can perform k-means clustering on the prediction results.

```
###The input here uses the probability value of antigenic similarity between two strains when the model predicts it.
python3 UMAP-and-kmeans.py
```

## License

*   The code in the `/script` directory is released under the **Creative Commons Attribution 4.0 International (CC-BY 4.0)**.

---

## Contact & Citation


For any questions regarding the code or data, please contact [Wenping Xie] at [wenpingxie2020@163.com].

