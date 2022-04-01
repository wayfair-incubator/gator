# Codechange Testing
This directory contains a testing framework that powers our testing of the various code_change resources.

This will allow developers of `CodeChangeResource`s to describe their tests without writing any code.

The `code_change_test_data` directory will contain a directory for each test scenario. Each scenario will contain three parts:

- `initial` directory, containing an example filesystem prior to a code_change.
- `code_change.yaml` containing a list of `CodeChangeResource` definitions.
- `expected` directory, containing the expected filesytem after the code_change

Although the `CodeChangeResource`s will be present in changesets via a resource such as the `CodeChangePROutput`, they are expected to be provided in a raw list form in the `code_change.yaml` as follows:

```yaml
- kind: NewFileCodeChange
  version: v1alpha
  spec:
    files:
    - file_path: foobar.txt
      file_content: some content
...
```

Each testing scenario will:
- Apply code changes defined in `code_change.yaml` against the `initial` directory.
- Assert that the contents of the modified `initial` directory are identical to the contents of the `expected` directory.

If there are discrepencies between the altered `inital` dir and the `expected` dir, the test case will provide information as to the diff that was identified.
