# CI/CD Setup Instructions

## Overview
This project uses GitHub Actions for continuous integration and deployment. The workflow automatically tests, builds, and releases the project when code is pushed.

## Workflow Triggers

### Automatic Triggers
- **Push to main/master branches**: Runs tests and linting
- **Pull requests**: Runs tests and linting on feature branches
- **Version tags (v*)**: Full CI/CD pipeline including release

### Manual Triggers
You can manually trigger workflows from the GitHub Actions tab.

## Required Secrets

Before the release workflow can publish packages, you need to configure the following secrets in your GitHub repository:

1. **PYPI_API_TOKEN**: For publishing to PyPI
   - Go to https://pypi.org/manage/account/token/
   - Create an API token with appropriate permissions
   - In your GitHub repo: Settings → Secrets and variables → Actions → New repository secret
   - Name: `PYPI_API_TOKEN`
   - Value: Your PyPI API token

2. **GITHUB_TOKEN**: Automatically provided by GitHub (no setup needed)

## Version Tagging

To create a release, push a version tag:

```bash
# Create and push a version tag
git tag v1.0.0
git push origin v1.0.0

# Or for pre-release versions
git tag v1.0.0-beta.1
git push origin v1.0.0-beta.1
```

The workflow will:
1. Run all tests
2. Build distribution packages
3. Publish to PyPI
4. Create a GitHub Release with attached artifacts

## Release Notes

If you have a `CHANGELOG.md` file, the workflow will automatically extract the relevant section for the release. Format your changelog like this:

```markdown
## [1.0.0] - 2024-01-15
### Added
- New feature X
- New feature Y

### Fixed
- Bug fix Z

## [0.9.0] - 2024-01-01
...
```

## Workflow Jobs

### 1. Test Job
- Runs on Python 3.8, 3.9, 3.10, 3.11
- Linting with flake8
- Type checking with mypy
- Unit tests with pytest
- Code coverage reporting

### 2. Build Job
- Only runs on version tags
- Creates source and wheel distributions
- Uploads artifacts for release

### 3. Release Job
- Only runs on version tags
- Publishes to PyPI
- Creates GitHub Release with:
  - Distribution packages
  - Release notes from CHANGELOG.md
  - Automatic pre-release detection

### 4. Notify Job
- Reports overall workflow status
- Provides clear success/failure messages

## Local Testing

Before pushing, you can test locally:

```bash
# Install development dependencies
pip install flake8 mypy pytest pytest-cov build twine

# Run linting
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

# Run type checking
mypy . --ignore-missing-imports

# Run tests
pytest

# Build package
python -m build
```

## Troubleshooting

### Workflow Not Running?
- Check that you're pushing to the correct branch (main/master)
- Verify the `.github/workflows/ci_cd.yml` file exists
- Check GitHub Actions tab for any error messages

### Release Failed?
- Verify `PYPI_API_TOKEN` secret is configured
- Check that the version tag follows the pattern `v*`
- Ensure `setup.py` or `pyproject.toml` is properly configured
- Review the workflow logs for specific error messages

### Pre-release Detection
Tags containing `rc`, `alpha`, or `beta` are automatically marked as pre-releases:
- `v1.0.0-alpha.1` → Pre-release
- `v1.0.0-rc.1` → Pre-release
- `v1.0.0` → Full release

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [PyPI Publishing Guide](https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/)
- [Semantic Versioning](https://semver.org/)
