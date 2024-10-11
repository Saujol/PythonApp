import json
import argparse


class Inputs:
    def __init__(self):
        parser = argparse.ArgumentParser(description="Approval Gate Script for GitHub Actions")
        parser.add_argument("-c", "--config", help="Config containing approval gate information", required=True)

        argument = parser.parse_args()
        self.arguments = argument

    def get_arguments(self):
        return self.arguments


class ApprovalGate:
    def __init__(self, config):
        self.user_names = config.get('approval_gates', {}).get('required_member_approvers', None)
        self.team_names = config.get('approval_gates', {}).get('required_team_approvers', None)
        self.wait_time = config.get('approval_gates', {}).get('wait_time', 0)
        self.approval_gates_enabled = config.get('approval_gates', {}).get('enabled', False)

    def prompt_approval(self):
        if self.approval_gates_enabled:
            print(f"Approval required from: {self.user_names or 'None'}, {self.team_names or 'None'}")
            response = input(f"Do you approve proceeding with wait time {self.wait_time} seconds? (yes/no): ")
            if response.lower() == 'yes':
                print("Approval granted. Continuing workflow.")
            else:
                print("Approval denied. Stopping workflow.")
                exit(1)
        else:
            print("Approval gates are disabled. Proceeding without approval.")


# Entry Point
if __name__ == "__main__":
    try:
        arguments = Inputs().get_arguments()
        config_data = json.loads(arguments.config)

        approval_gate = ApprovalGate(config_data)
        approval_gate.prompt_approval()

    except Exception as e:
        raise e
