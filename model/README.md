# Model weights

The trained TensorFlow checkpoints are organized by influenza B lineage:

- `BV/model/`: B/Victoria checkpoint (`model_20`).
- `BY/model/`: B/Yamagata checkpoint (`model_20`).

Each checkpoint consists of the matching `.index` and `.data-00000-of-00001` files. Keep the two lineages separate when loading the model; their weights were trained independently.
