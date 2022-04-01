from gator.resources.build import build_changeset, register_custom_resource
from pydantic import BaseModel
from pathlib import Path
from gator.resources.models import CodeChangeResource

spec = """
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
          regex: '([ \t]+)bo1c2\:'
          paths:
            - "asd"
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

print(build_changeset(spec))

# class DoNothingSpec(BaseModel):
#     some_value: str
#
# class DoNothingCodeChange(CodeChangeResource):
#     kind = 'DoNothingCodeChange'
#     version = 'v1alpha'
#     spec: DoNothingSpec
#
#     def make_code_changes(self, path: Path) -> None:
#         pass
#
# register_custom_resource(DoNothingCodeChange)
#
# another_spec = """
# kind: Changeset
# version: v1alpha
# spec:
#   name: time to do a thing
#   issue_title: stuff
#   issue_body: other stuff
#   code_changes:
#       - kind: DoNothingCodeChange
#         version: v1alpha
#         spec:
#           some_value: "concrete value"
#
# """
#
# print(build_changeset(another_spec))
