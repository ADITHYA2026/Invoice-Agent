import json
import os


def save_json(data, filename):

    os.makedirs("output/extracted_json", exist_ok=True)

    output_file = f"output/extracted_json/{filename}.json"

    with open(output_file, "w") as f:
        json.dump(data, f, indent=4)