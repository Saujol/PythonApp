import requests
import argparse
import os
import json

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


class Inputs:
    def __init__(self):
        parser = argparse.ArgumentParser(description="Script to build Approval Gates inside of our CICD Pipelines")
        parser.add_argument("-c", "--config", help="Config containing account information", required=True, default="")
        parser.add_argument("-o", "--github-org", help="Github Organization Name", required=True, default="")
        parser.add_argument("-r", "--github-repo", help="Github Repo Name", required=True, default="")

        argument = parser.parse_args()
        status = False
        
        if argument.config:
            print(argument.config)
            status = True
        if argument.github_org:
            status = True
        if argument.github_repo:
            status = True
        if not status:
            print("Maybe you want to use -c or -o -r as arguments ?")
        
        self.arguments = argument
    
    def get_arguments(self):
        return self.arguments


class HTTP:
    
    def __init__(self, payload, type):
        self.graphql_url = "https://api.github.com/graphql"
        self.github_rest_url = "https://api.github.com"
        self.headers = {
            'Accept': 'application/vnd.github.v4.idl',
            'Authorization': 'token ' + os.environ['PAT_TOKEN'],  # Ensure PAT_TOKEN is set in the environment
            'Content-Type': 'application/json',
        }
        self.payload = payload
        self.type = type

    def http_graphql(self):
        try:
            session = requests.Session()
            retry = Retry(connect=3, backoff_factor=0.5)
            adapter = HTTPAdapter(max_retries=retry)
            session.mount('https://', adapter)

            response = session.request(self.type, self.graphql_url, headers=self.headers, data=self.payload)
            if response.status_code != 200:
                raise Exception(f'"Response Code": [{response.status_code}], "Response": [{response.text}]"')

            data = json.loads(response.text)
            if data.get('errors', None):
                raise Exception(f'"Response Code": [{response.status_code}], "Response": [{response.text}]"')

            return data['data']
        except Exception as e:
            raise e

    def http_rest(self, endpoint):
        try:
            session = requests.Session()
            retry = Retry(connect=3, backoff_factor=0.5)
            adapter = HTTPAdapter(max_retries=retry)
            session.mount('https://', adapter)

            response = session.request(self.type, self.github_rest_url + endpoint, headers=self.headers, data=self.payload)
            return response
        except Exception as e:
            raise e


class GithubGraphQLCall:

    def __init__(self, github_org, github_repo):
        self.github_org = github_org
        self.github_repo = github_repo

    @staticmethod
    def __get_user_ids(user_names_list):
        try:
            user_ids = []
            if user_names_list:
                for user_name in user_names_list:
                    payload = "{\"query\":\"query($username: String!) {\\r\\n    user(login: $username) {\\r\\n        databaseId\\r\\n        id\\r\\n        email\\r\\n        name\\r\\n        login\\r\\n        organizations(first: 100){\\r\\n            nodes {\\r\\n                name\\r\\n                login\\r\\n            }\\r\\n        }\\r\\n    }\\r\\n}\",\"variables\":{\"username\":\"" + user_name.strip() + "\"}}"
                    response = HTTP(payload=payload, type="POST").http_graphql()
                    print(f"user_name: {response['user']['login']}, user_id: {response['user']['id']}")
                    user_ids.append(response['user']['id'])

            return user_ids
        except Exception as e:
            raise e

    def __get_team_ids(self, team_names_list):
        try:
            team_ids = []
            if team_names_list:
                for team_name in team_names_list:
                    payload = "{\"query\":\"query($githubOrg: String!, $teamName: String!) {\\r\\n    organization(login: $githubOrg) {\\r\\n        team(slug: $teamName) {\\r\\n            databaseId\\r\\n            id\\r\\n            combinedSlug\\r\\n            name\\r\\n            slug\\r\\n        }\\r\\n    }\\r\\n}\",\"variables\":{\"githubOrg\":\"" + self.github_org + "\",\"teamName\":\"" + team_name + "\"}}"
                    response = HTTP(payload=payload, type="POST").http_graphql()
                    if not response.get('organization', None).get('team', None):
                        raise Exception(f'Error: attempting to find team_id for team [{team_name}]. Response: {response}.')

                    print(f"team_name: {response['organization']['team']['combinedSlug']}, Team_id: {response['organization']['team']['id']}")
                    team_ids.append(response['organization']['team']['id'])

            return team_ids
        except Exception as e:
            raise e

    def __get_repository_id(self):
        try:
            payload = "{\"query\":\"query($owner: String!, $repo: String!) {\\r\\n    repository(owner: $owner, name: $repo) {\\r\\n        name\\r\\n        id\\r\\n    }\\r\\n}\",\"variables\":{\"owner\":\"" + self.github_org + "\",\"repo\":\"" + self.github_repo + "\"}}"
            response = HTTP(payload=payload, type="POST").http_graphql()['repository']['id']
            return response
        except Exception as e:
            raise e

    def build_approval_gates(self, user_names, team_names):
        try:
            user_names_list, team_names_list = [], []

            if user_names:
                for user_name in user_names.split(','):
                    if user_name.strip():
                        user_names_list.append(user_name.strip())

            if team_names:
                for team_name in team_names.split(','):
                    if team_name.strip():
                        team_names_list.append(team_name.strip())

            user_ids = self.__get_user_ids(user_names_list=user_names_list)
            team_ids = self.__get_team_ids(team_names_list=team_names_list)
            reviewer_ids = user_ids + team_ids

            if len(user_names_list + team_names_list) > 6:
                raise Exception(f"Too many reviewers passed through. Limit 6. Please remove one of the following: [{user_names_list + team_names_list}]")

            print("Reviewer IDs:", reviewer_ids)

        except Exception as e:
            raise e


class UpdateApprovalSettings:

    def __init__(self, config, github_org, github_repo):
        self.github_org = github_org
        self.github_repo = github_repo
        self.user_names = config.get('approval_gates', {}).get('required_member_approvers', None)
        self.team_names = config.get('approval_gates', {}).get('required_team_approvers', None)

    def update_approval_settings(self):
        try:
            github = GithubGraphQLCall(github_org=self.github_org, github_repo=self.github_repo)
            github.build_approval_gates(
                user_names=self.user_names,
                team_names=self.team_names
            )
        except Exception as e:
            raise e


# Entry Point
if __name__ == "__main__":
    try:
        arguments = Inputs().get_arguments()
        full_config = json.loads(arguments.config)

        update_approval = UpdateApprovalSettings(
            full_config,
            arguments.github_org,
            arguments.github_repo
        ).update_approval_settings()

    except Exception as e:
        print("Error:", str(e))
