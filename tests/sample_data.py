from gator.resources.build import build_changeset

SOME_VALID_CHANGESET_SPEC = """
kind: Changeset
version: v1alpha
spec:
  name: time to do a thing
  issue_title: stuff
  issue_body: other stuff
  filters:
      - kind: RegexFilter
        version: v1alpha
        spec:
          regex: '([ t]+)bo1c2:'
          paths:
            - "asd"
            - k8s.yml
  code_changes:
      - kind: RegexReplaceCodeChange
        version: v1alpha
        spec:
          replacement_details:
            - regex: '(?<=black==)(22.1.0|21.w+)'
              replace_term: "22.3.0"
              paths:
                - "requirements-test.txt"
"""

SOME_CHANGESET = build_changeset(SOME_VALID_CHANGESET_SPEC)
SOME_GITHUB_DOMAIN = "github.company.com"
SOME_GITHUB_TOKEN = "abc123"
SOME_USERNAME = "somebody"
SOME_REPO_NAME = "some-repo"
SOME_REPO_NAMESPACE = "some-org"
SOME_REPO_FULL_NAME = f"{SOME_REPO_NAMESPACE}/{SOME_REPO_NAME}"
SOME_REPOSITORIES = [SOME_REPO_FULL_NAME]

SOME_CONFIGURATION_VALUES = {
    "dry_run": False,
    "repositories": SOME_REPOSITORIES,
    "github_domain": SOME_GITHUB_DOMAIN,
    "github_token": SOME_GITHUB_TOKEN,
    "github_username": SOME_USERNAME,
    "changeset": SOME_CHANGESET,
}
