# DeepCTS-B: Transformer-Based Deep Learning for Prioritizing Candidate Sites Associated with Influenza B Antigenic Cluster Transitions

This repository contains the Python scripts used for the analyses in the paper "[Unraveling the Molecular Determinants of Antigenic Evolution of Influenza B Virus by Transformer-Based Deep Learning]". The project focuses on predicting the antigenic relationship of influenza viruses (BV and BY) using a deep learning model called PREDAC-TransFluB.

## Contents

The repository is organized into the following main directories:

*   `/csv`: Contains the primary input datasets in CSV format for testing (e.g., `inputdata_data.csv`).
*   `/script`: Contains all the Python scripts required to run the model training and analysis.
*   `/result`: Contains the prediction and clustering results.
*   `/model`: Contains the trained models for antigenic evolution.
*   `/seq`: Contains the sequence data for testing (e.g., `sequences.fasta`).
*   `/external`: Contains the AAIndex data (e.g., `aaindex_feature_BV.txt`).

### File and Folder Descriptions

```
.
├── csv/
│   ├── inputdata_data.csv     # Input data file for testing the model.
│
├── seq/
│   └── sequences_test.fasta      # Sequence file for testing the model.
│
├── external/
│   ├── aaindex_feature_BV.txt  # AAIndex feature data for BV antigenic evolution.
│   └── aaindex_feature_BY.txt  # AAIndex feature data for BY antigenic evolution.
│ 
├── script/
│   ├── generate_esm.py                             # Script to generate ESM embeddings for sequences.
│   ├── matrix-generatre-ems2-7-features.py         # Script to generate the input feature matrix.
│   ├── model_train.py                              # Main script to train the PREDAC-Transformer model.
│   ├── model_pred.py                               # Script to make predictions using the trained model.
│   └── kmeans_cluster.py                           # Script for clustering the predicted antigenic sites.
│
├── result/
│   ├── pred/
│   │   ├── pred.csv              # Prediction results for antigenic evolution.
│   └── cluster/
│       ├── cluster_results.csv   # K-means clustering results of predicted antigenic sites.
│
└── model/
    ├── model_01/                 # Folder containing the trained model.
    └── model_02/                
```

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

