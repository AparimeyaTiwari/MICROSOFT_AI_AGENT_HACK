from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials

from dotenv import load_dotenv
import os
import time

# Load credentials from .env file
load_dotenv()
subscription_key = os.getenv("VISION_KEY")
endpoint = os.getenv("VISION_ENDPOINT")

# Authenticate
computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))

# === Get file path from user ===
file_path = input("Enter the path to your local PDF or image file: ").strip()

# Ensure file exists
if not os.path.isfile(file_path):
    print(f"File not found: {file_path}")
    exit(1)

print("===== Reading File (Local) =====")
with open(file_path, "rb") as local_file:
    read_response = computervision_client.read_in_stream(local_file, raw=True)

# Get the operation location (used to get result later)
read_operation_location = read_response.headers["Operation-Location"]
operation_id = read_operation_location.split("/")[-1]

# Poll for the result
while True:
    read_result = computervision_client.get_read_result(operation_id)
    if read_result.status not in ['notStarted', 'running']:
        break
    time.sleep(1)

# Print results
if read_result.status == OperationStatusCodes.succeeded:
    for page in read_result.analyze_result.read_results:
        for line in page.lines:
            print(line.text)

