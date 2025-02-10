import os
import requests
import base64
import json
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Define cluster URL and cluster name as variables
cluster_url = "/api/"
cluster_name = ""
kafka_username = os.getenv("KAFKA_USERNAME")
kafka_password = os.getenv("KAFKA_PASSWORD")
partitions = os.getenv("PARTITIONS")
replication = os.getenv("REPLICATION")

if not kafka_username or not kafka_password:
    print("Error: KAFKA_USERNAME and KAFKA_PASSWORD environment variables must be set.")
    exit(1)

if not partitions or not replication:
    print("Error: PARTITIONS and REPLICATION environment variables must be set.")
    exit(1)

# Encode username and password for Basic Auth
auth_str = f"{kafka_username}:{kafka_password}"
b64_auth_str = base64.b64encode(auth_str.encode()).decode()

headers = {
    "Authorization": f"Basic {b64_auth_str}",
    "Content-Type": "application/json"
}

# Read topic names from the file
with open('topics.txt', 'r') as file:
    topic_names = [line.strip() for line in file]

for topic_name in topic_names:
    # Check if the topic already exists
    check_url = f"{cluster_url}/{cluster_name}/topic/{topic_name}"
    response = requests.get(check_url, headers=headers, verify=False)
    if response.status_code == 200:
        print(f"Topic '{topic_name}' already exists.")
        continue
    elif response.status_code not in [404, 409]:
        print(f"Error connecting to the cluster for topic '{topic_name}'. HTTP status code: {response.status_code}")
        print(f"Response body: {response.text}")
        continue

    # Create the Kafka topic
    create_url = f"{cluster_url}/{cluster_name}/topic"
    payload = {
        "cluster": cluster_name,
        "name": topic_name,
        "partition": int(partitions),
        "replication": int(replication),
        "configs": {
            "cleanup.policy": "delete",
            "retention.ms": 86400000
        }
    }
    create_response = requests.post(create_url, headers=headers, data=json.dumps(payload), verify=False)

    if create_response.status_code in [200, 201]:
        print(f"Topic '{topic_name}' created successfully.")
    else:
        print(f"Failed to create topic '{topic_name}'. HTTP status code: {create_response.status_code}")
        print(f"Response body: {create_response.text}")

    # Verify if the topic was created
    verify_response = requests.get(check_url, headers=headers, verify=False)
    if verify_response.status_code == 200:
        print(f"Topic '{topic_name}' verified successfully.")
    else:
        print(f"Failed to verify topic creation for '{topic_name}'. HTTP status code: {verify_response.status_code}")

# Clean up (if any cleanup is needed, add it here)
