# convert.py

This script converts a Hugging Face dataset in CSV format to JSONL format, suitable for training language models. It performs the following steps:

1. **Loads the dataset:** Uses the `datasets` library to load a specified Hugging Face dataset.
2. **Splits the data:** Splits the dataset into training and validation sets using `sklearn.model_selection.train_test_split`.
3. **Converts to JSONL:** 
    - Selects the desired columns ("prompt" and "output" in this case).
    - Iterates through the DataFrame rows and formats the data into a list of dictionaries, where each dictionary represents a conversation turn with "role" and "content" keys.
    - Writes the formatted data to JSONL files (train.jsonl and validation.jsonl), with each line representing a JSON object.

## Usage

1. **Install dependencies:**
  ```bash
  pip install datasets pandas scikit-learn
  ```

2. **Update the script:**

  - Replace `hf://datasets/cyberblip/Travel_india/TRAIN.csv` in the `convert_and_split_to_jsonl()` function call with the path to your Hugging Face CSV file.
  - Optionally, modify the `columns_to_keep` list if your dataset uses different column names for prompts and outputs.

3. **Run the script:**

```
python convert.py
```

This will create two files:

  - `train.jsonl`: Contains the training data in JSONL format.
  - `validation.jsonl`: Contains the validation data in JSONL format.

## Example

To convert the `cyberblip/Travel_india` dataset, you would use the following command:

`python convert.py`
This assumes that the hf_csv_file variable in the script has been updated to point to the correct file path for the `cyberblip/Travel_india` dataset.
