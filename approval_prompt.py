def get_user_approval():
    # Ask for user input to approve or reject the task
    decision = input("Do you approve the continuation of the workflow? (yes/no): ").strip().lower()

    if decision == "yes":
        print("Approval granted. Proceeding with the pipeline.")
        return True
    elif decision == "no":
        print("Approval rejected. Exiting the pipeline.")
        return False
    else:
        print("Invalid input. Please enter 'yes' or 'no'.")
        return get_user_approval()

def main():
    approved = get_user_approval()

    if approved:
        exit(0)  # Continue the pipeline (normal exit)
    else:
        exit(1)  # Stop the pipeline (non-zero exit code to indicate failure)

if __name__ == "__main__":
    main()
