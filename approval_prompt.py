import time
import os

def check_for_approval():
    print("Waiting for approval...")
    
    # Simulate polling for user approval (you can replace this with an actual approval check, e.g., reading from a file, API)
    while True:
        # Look for an "approval.txt" file with 'approve' or 'reject'
        if os.path.exists("approval.txt"):
            with open("approval.txt", "r") as f:
                decision = f.read().strip().lower()
                if decision == "approve":
                    print("Approval granted. Proceeding with the pipeline.")
                    return True
                elif decision == "reject":
                    print("Approval rejected. Exiting the pipeline.")
                    return False
        time.sleep(10)  # Poll every 10 seconds

def main():
    approved = check_for_approval()
    
    if approved:
        exit(0)  # Exit normally, which means continue the pipeline
    else:
        exit(1)  # Exit with failure, which means stop the pipeline

if __name__ == "__main__":
    main()
