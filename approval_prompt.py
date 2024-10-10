import requests
import argparse
import os
import json
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def prompt_approval():
    # Simple terminal prompt for approval
    while True:
        user_input = input("Do you want to proceed with the remaining GitHub Action workflow? (yes/no): ").lower()
        if user_input in ['yes', 'no']:
            return user_input == 'yes'
        print("Invalid input, please type 'yes' or 'no'.")

def setup_requests_with_retries():
    session = requests.Session()
    retry_strategy = Retry(
        total=3,  # Retry 3 times
        status_forcelist=[429, 500, 502, 503, 504],
        method_whitelist=["HEAD", "GET", "POST"],  # Specify HTTP methods to retry
        backoff_factor=1  # Backoff factor for retries
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session

def perform_action(session):
    # Example of a simple request (can be replaced with your GitHub API request)
    response = session.get("https://api.github.com")
    if response.status_code == 200:
        print("GitHub API is reachable, proceeding with the action...")
        return True
    else:
        print(f"Failed to reach GitHub API: {response.status_code}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Trigger GitHub Action with approval.")
    parser.add_argument("--trigger", action="store_true", help="Whether to trigger the next task in the GitHub Action.")
    args = parser.parse_args()

    # Check for approval
    if prompt_approval():
        print("Approval granted. Proceeding with the workflow.")
        session = setup_requests_with_retries()

        # Execute action (for example, making a GitHub API call)
        if perform_action(session):
            print("Workflow executed successfully.")
        else:
            print("Workflow execution failed.")
    else:
        print("Workflow cancelled by user.")

if __name__ == "__main__":
    main()
