import os


def send_acknowledgement(email, filename, status):

    os.makedirs("output/acknowledgements", exist_ok=True)

    ack_message = f"""
ACKNOWLEDGEMENT

To: {email}
Document: {filename}
Processing Status: {status}

Thank you. Your document has been processed.
"""

    print(ack_message)

    safe_name = filename.replace(".", "_")

    output_file = f"output/acknowledgements/{safe_name}.txt"

    with open(output_file, "w") as f:
        f.write(ack_message)