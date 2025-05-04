#!/usr/bin/env python

import argparse
import os
from datetime import datetime

import yaml
from github import Auth, Github

# TODO: There is a lot of repeating code that you can refactor,
#  but I'll keep it as is because it’s easier to follow and learn.


def pause(env, service, repo, branch):
    """Pause Continuous Delivery (C/D) of the service in the target environment."""

    # Create a file path for the Application resource e.g. envs/dev/users/application.yaml
    file_path = f'envs/{env}/{service}/application.yaml'

    # Retrieve the content of the Application from the remote "main" branch of the repository
    contents = repo.get_contents(file_path, ref=repo.default_branch)

    # Parse the YAML file and load it into a Python dictionary.
    app = yaml.safe_load(contents.decoded_content.decode())

    # Create an ignore annotation: argocd-image-updater.argoproj.io/<image_name>.ignore-tags = '*'
    key = f'argocd-image-updater.argoproj.io/{service}.ignore-tags'
    app['metadata']['annotations'][key] = '*'

    # Create a YAML file with an Application resource that includes an ignore annotation
    app_yaml = yaml.dump(app, default_flow_style=False, explicit_start=True)

    # Update the Application resource in the remote 'pause-<env>-<date>' branch of the repository
    repo.update_file(contents.path, f'Pause {service} in {env}.', app_yaml, contents.sha, branch=branch)

    # Log the action that was performed.
    print(f'Updated the "{file_path}" file in the "{branch}" branch of the "{repo.name}" remote repository')


def resume(env, service, repo, branch):
    """Resume Continuous Delivery (C/D) of the service in the target environment."""

    # Create a file path for the Application resource e.g. envs/dev/users/application.yaml
    file_path = f'envs/{env}/{service}/application.yaml'

    # Retrieve the content of the Application from the remote "main" branch of the repository
    contents = repo.get_contents(file_path, ref=repo.default_branch)

    # Parse the YAML file and load it into a Python dictionary.
    app = yaml.safe_load(contents.decoded_content.decode())

    # Remove an ignore annotation: argocd-image-updater.argoproj.io/<image_name>.ignore-tags = '*'
    key = f'argocd-image-updater.argoproj.io/{service}.ignore-tags'
    app['metadata']['annotations'].pop(key, None)

    # Create a YAML file with an Application resource that includes an ignore annotation
    app_yaml = yaml.dump(app, default_flow_style=False, explicit_start=True)

    # Update the Application resource in the remote 'resume-<env>-<date>' branch of the repository
    repo.update_file(contents.path, f'Resume {service} in {env}.', app_yaml, contents.sha, branch=branch)

    # Log the action that was performed.
    print(f'Updated the "{file_path}" file in the "{branch}" branch of the "{repo.name}" remote repository')


def get_versions(charts_dir, env, repo):
    """Get the latest deployed versions of the services."""

    # Initialize a dictionary to store service versions
    versions = {}

    # Retrieve the service folders from the remote repository e.g. helm-charts/payments
    services = repo.get_contents(charts_dir)

    # Go over each service you have and get the latest deployed version
    for service in services:
        # Create a path for the file e.g. helm-charts/payments/.argocd-source-payments.yaml
        file_path = f'{service.path}/.argocd-source-{service.name}-{env}.yaml'

        # Retrieve the content of the Application from the remote "main" branch of the repository
        contents = repo.get_contents(file_path, ref=repo.default_branch)

        # Parse the YAML file and load it into a Python dictionary.
        params = yaml.safe_load(contents.decoded_content.decode())

        # Go over each Helm parameter and save the image tag of each service into a dictionary
        for param in params['helm']['parameters']:
            if param['name'] == 'image.tag':
                versions[service.name] = param['value']

    # Return service versions
    return versions


def options():
    """Add command-line arguments to the script."""

    # Create an instance of the ArgumentParser
    parser = argparse.ArgumentParser()

    # Add an source environment flag for the prod push, e.g., dev, staging
    parser.add_argument('--source-env', help='Select environment')

    # Add an target environment flag for the prod push, e.g., prod
    parser.add_argument('--target-env', help='Select environment')

    # Add an action flag, e.g., pause, resume, push
    parser.add_argument('--action', help='Select an action to perform')

    # Parse and return command-line arguments
    return parser.parse_args()


def update_versions(env, versions, repo, branch):
    """Update the service versions to the latest ones deployed in the specified environment."""

    # Create a path for the target environment folder, e.g. envs/prod
    target_dir = f'envs/{env}'

    # Retrieve the service folders from the remote repository e.g. envs/prod/payments
    services = repo.get_contents(target_dir)

    # Go over each service and set the version to the latest deployed in the dev environment
    for service in services:

        # Create a path for the file e.g. envs/prod/payments/application.yaml
        file_path = f'{service.path}/application.yaml'

        # Retrieve the content of the Application from the remote "main" branch of the repository
        contents = repo.get_contents(file_path, ref=repo.default_branch)

        # Parse the YAML file and load it into a Python dictionary.
        app = yaml.safe_load(contents.decoded_content.decode())

        # Initialize a new list to store existing Helm parameters
        new_params = []

        # Go over each parameter that is not an image tag and add it to the list
        for param in app['spec']['source']['helm']['parameters']:
            if param['name'] != 'image.tag':
                new_params.append(param)

        # Create a new image tag with the latest version and add it to the list
        image_tag = {'name': 'image.tag', 'value': versions[service.name]}
        new_params.append(image_tag)

        # Take the existing Application resource and replace all Helm parameters, including the version tag
        app['spec']['source']['helm']['parameters'] = new_params

        # Create a YAML file with an Application resource that includes new image tags
        app_yaml = yaml.dump(app, default_flow_style=False, explicit_start=True)

        # Update the Application resource in the remote 'push-<env>-<date>' branch of the repository
        repo.update_file(contents.path, f'Updated {service.name} in {env}.', app_yaml, contents.sha, branch=branch)

        # Log the action that was performed.
        print(f'Updated the "{file_path}" file in the "{branch}" branch of the "{repo.name}" remote repository')


def create_branch(repo, branch):
    """Create a new branch in the remote GitHub repository."""

    # Get a reference to the "main" branch
    sb = repo.get_branch(repo.default_branch)

    # Create a new branch in the remote repo
    repo.create_git_ref(ref='refs/heads/' + branch, sha=sb.commit.sha)

    # Log the action that was performed.
    print(f'Created a "{branch}" branch in the "{repo.name}" remote repository')


def create_pr(repo, branch, title):
    """Create a Pull Request in the remote GitHub repository."""

    # Get a reference to the "main" branch
    base = repo.default_branch

    # Create a Pull Request in the remote repo
    repo.create_pull(base=base, head=branch, title=title)

    # Log the action that was performed.
    print(f'Created a pull request in the "{repo.name}" remote repository')


def get_repo(name):
    """Get GitHub repository by name"""

    # Get the personal authorization token from an environment variable, e.g., export GITHUB_TOKEN=github_pat_123
    github_token = os.environ['GITHUB_TOKEN']

    # Create authorization based on the token.
    auth = Auth.Token(github_token)

    # Authorize with GitHub using the token
    g = Github(auth=auth)

    # Return the GitHub repository
    return g.get_repo(name)


def main():
    """Entrypoint to the GitOps script."""
    # Get the GitHub repository for the Kubernetes deployments
    repository = get_repo('antonputra/k8s')

    # Parse command-line arguments
    args = options()

    # Get today's date to use it in the branch name
    today = datetime.today().strftime('%Y-%m-%d')

    # Create a path for the target environment, e.g., envs/dev
    env_dir = f'envs/{args.target_env}'

    # Freeze the selected environment, e.g., stop continuous delivery for all services
    if args.action == 'pause':

        # Create a new branch name for the Pull Request, e.g., pause-dev-2024-07-29
        new_branch = f'pause-{args.target_env}-{today}'

        # Create a new branch in the remote GitHub repo
        create_branch(repository, new_branch)

        # Retrieve the service folders from the remote repository e.g. envs/dev/payments,envs/dev/users
        services = repository.get_contents(env_dir)

        # Go over each service and add an annotation to disable the ArgoCD image updater
        for svc in services:
            pause(args.target_env, svc.name, repository, new_branch)

        # Create a Pull Request to disable Continuous Delivery
        create_pr(repository, new_branch, f'Freeze the {args.target_env} environment.')

    # Unfreeze the selected environment, e.g., resume continuous delivery for all services
    if args.action == 'resume':

        # Create a new branch name for the Pull Request, e.g., resume-dev-2024-07-29
        new_branch = f'resume-{args.target_env}-{today}'

        # Create a new branch in the remote GitHub repo
        create_branch(repository, new_branch)

        # Retrieve the service folders from the remote repository e.g. envs/dev/payments,envs/dev/users
        services = repository.get_contents(env_dir)
        for svc in services:
            resume(args.target_env, svc.name, repository, new_branch)

        # Create a Pull Request to enable Continuous Delivery
        create_pr(repository, new_branch, f'Unfreeze the {args.target_env} environment.')

    # Prepare the production push with the latest deployed versions from the dev environment
    if args.action == 'push':

        # Create a new branch name for the Pull Request, e.g., prod-push-2024-07-29
        new_branch = f'prod-push-{today}'

        # Create a new branch in the remote GitHub repo
        create_branch(repository, new_branch)

        # Get the latest deployed versions from the dev environment
        latest_versions = get_versions('helm-charts', args.source_env, repository)

        # Update versions in the specified environment to the latest ones
        update_versions(args.target_env, latest_versions, repository, new_branch)

        # Create a Pull Request to enable Continuous Delivery
        create_pr(repository, new_branch, f'Production Push.')


if __name__ == "__main__":
    main()
