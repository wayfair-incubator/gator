# About Gator

Gator is short for "change propagator", and can be used to make changes across multiple Github repositories at once.

The entrypoint will be a dockerized CLI and a python package.

You will give Gator an imperative yaml spec file, and some repos to process. Gator will create PRs or Issues in Github according to the spec. The CLI will allow you to test your specs locally, making sure that the code changes look as you expect before PRs are created.

If the reusable code modifications do not suffice, you will be able to make changes to code programatically, and use Gator to automate the git aspects, and assist you with testing. An example `Changeset` specification will look like this:

```yaml
kind: Changeset
version: v1alpha
spec:
  name: Docker image registry migration
  issue_title: Replace all usages of outdated Docker image registry URL with new URL
  issue_body: |
      # Artifactory Has Moved
      
      ... Some text to be included in the PR or issue body.
  filters:
      - kind: RegexFilter
        version: v1alpha
        spec:
          regex: 'registry.company.com'
          paths:
            - definitions/application_spec.yml
  code_changes:
      - kind: RegexReplaceCodeChange
        version: v1alpha
        spec:
          replacement_details:
            - regex: 'registry.company.com'
              replace_term: "registry.parent-company.com"
              paths:
                - definitions/application_spec.yml
```

# Development Status

Gator has not reached Minimum Viable Product status yet, but is actively in development as of early 2022.

# Contributing

If you're interested in contributing, please check out the CONTRIBUTING.md file at repo root.
