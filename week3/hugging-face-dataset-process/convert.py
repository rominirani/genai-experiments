from datasets import load_dataset, Dataset
import pandas as pd
import json
from sklearn.model_selection import train_test_split

# Update the function definition and code below to take the dataset name in the function

def get_dataset_details(dataset_name):
    dataset_train = load_dataset(dataset_name)
    print(len(dataset_train))
    print(dataset_train.shape)
    print(dataset_train.column_names)

def convert_evaluation_data_to_jsonl(hf_csv_file):
    train_df = pd.read_csv(hf_csv_file)
    for df, filename in [(train_df, "eval.jsonl")]:
        columns_to_keep = ["prompt", "output"]
        df = df[columns_to_keep]

        formatted_data = []
        for index, row in df.iterrows():
            formatted_data.append({
                "input_text": row["prompt"],
                "output_text": row["output"]
            })

        with open(filename, "w") as f:
            for item in formatted_data:
                f.write(json.dumps(item) + "\n")

        print(f"File {filename} converted to JSONL")

def convert_and_split_to_jsonl(hf_csv_file):
    # Load the data
    df = pd.read_csv(hf_csv_file)
    print("Data shape:", df.shape)
    print(df.head())

    # Split the data into training and validation sets (e.g., 80% train, 20% validation)
    train_df, validation_df = train_test_split(df, test_size=0.2, random_state=42)

    # Process and convert both DataFrames
    for df, filename in [(train_df, "train.jsonl"), (validation_df, "validation.jsonl")]:
        columns_to_keep = ["prompt", "output"]
        df = df[columns_to_keep]

        formatted_data = []
        for index, row in df.iterrows():
            formatted_data.append({
                "messages": [
                    {"role": "user", "content": row["prompt"]},
                    {"role": "model", "content": row["output"]}
                ]
            })

        with open(filename, "w") as f:
            for item in formatted_data:
                f.write(json.dumps(item) + "\n")

        print(f"File {filename} converted to JSONL")

if __name__ == "__main__":
    #get_dataset_details("cyberblip/Travel_india")
    convert_and_split_to_jsonl("hf://datasets/cyberblip/Travel_india/TRAIN.csv")
    #convert_evaluation_data_to_jsonl("hf://datasets/cyberblip/Travel_india/TRAIN.csv")
