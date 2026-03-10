# How to Run CI/CD Pipeline

This document explains how to run the CI/CD pipeline for the News Trend Analyzer project.

## GitHub Actions Workflow

The project includes a GitHub Actions workflow defined in `.github/workflows/ci.yml` that performs automated testing when code is pushed or merged.

### Workflow Details

- **Trigger**: The workflow runs on push and pull request events to the main branch
- **Runner**: Uses Ubuntu-latest environment
- **Python Version**: 3.9
- **Steps**:
  1. Checkout the repository
  2. Set up Python environment
  3. Install dependencies from requirements.txt
  4. Install the package in editable mode (`pip install -e .`)
  5. Run tests using pytest with verbose output

### Running Tests Locally

To run the same tests that the CI pipeline executes, use the following command:

```bash
python -m pytest tests/ -v
```

### Manual CI Execution

To trigger the CI pipeline manually, you can:

1. Push changes to a branch
2. Create a pull request to main
3. Or use GitHub CLI:
   ```bash
   gh workflow run ci.yml
   ```

### Best Practices

- Always run tests locally before pushing changes
- Ensure all tests pass before merging pull requests
- Update tests when modifying functionality
- Add new tests for new features