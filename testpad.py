from gator.resources.build import build_changeset

spec = """
kind: Changeset
version: v1alpha
stuff: "stuff"
spec:
  issue_title: stuff
  issue_body: other stuff
  filters:
      - kind: RegexFilter
        version: v1alpha
        spec:
          regex: '([ \t]+)bo1c2\:'
          paths:
            - k8s.yaml
            - k8s.yml
  code_changes:
      - kind: RegexReplaceCodeChange
        version: v1alpha
        spec:
          replacement_details:
            - regex: '(?<=black==)(22\.1\.0|21\.\w+)'
              replace_term: "22.3.0"
              paths:
                - "requirements-test.txt"
"""

build_changeset(spec)