# Publishing Guide

This guide explains how to publish `python-zeep-codegen` to PyPI.

## Prerequisites

1. **Create accounts**:
   - [PyPI account](https://pypi.org/account/register/) (production)
   - [TestPyPI account](https://test.pypi.org/account/register/) (testing)

2. **Install build tools**:
   ```bash
   pip install --upgrade build twine
   ```

3. **Configure API tokens**:
   - Create API token at https://pypi.org/manage/account/token/
   - Create API token at https://test.pypi.org/manage/account/token/
   - Store in `~/.pypirc`:
     ```ini
     [distutils]
     index-servers =
         pypi
         testpypi

     [pypi]
     username = __token__
     password = pypi-YOUR-PRODUCTION-TOKEN

     [testpypi]
     username = __token__
     password = pypi-YOUR-TEST-TOKEN
     ```

## Pre-Release Checklist

- [ ] Update version in `pyproject.toml`
- [ ] Update `CHANGELOG.md` (create if needed)
- [ ] Run all tests: `pytest`
- [ ] Run type checking: `mypy wsdl_to_schema.py pipeline/ utils/ plugins/ exceptions.py`
- [ ] Check code quality: `ruff check .`
- [ ] Update documentation if needed
- [ ] Commit all changes
- [ ] Create git tag: `git tag v0.1.0`

## Build Distribution

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build source distribution and wheel
python -m build

# Verify contents
tar tzf dist/python-zeep-codegen-*.tar.gz
unzip -l dist/python_zeep_codegen-*.whl
```

## Test on TestPyPI (Recommended)

```bash
# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# Test installation in a new virtual environment
python -m venv test-env
source test-env/bin/activate
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ python-zeep-codegen

# Test the installed package
wsdl-to-schema --help
python -c "from pipeline import convert_to_pydantic; print('Import successful')"

# Clean up
deactivate
rm -rf test-env
```

## Publish to PyPI

```bash
# Upload to PyPI (production)
python -m twine upload dist/*

# Push git tag
git push origin v0.1.0

# Create GitHub release
# Go to: https://github.com/nokout/python-zeep-codegen/releases/new
# - Select tag: v0.1.0
# - Add release notes from CHANGELOG
# - Attach distribution files (optional)
```

## Post-Release

1. **Verify installation**:
   ```bash
   pip install python-zeep-codegen
   wsdl-to-schema --help
   ```

2. **Update documentation**:
   - Update README installation instructions if needed
   - Update version badges

3. **Announce**:
   - Create release notes on GitHub
   - Update project status

## Version Numbering

Follow [Semantic Versioning](https://semver.org/):
- **MAJOR.MINOR.PATCH** (e.g., `1.2.3`)
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

Examples:
- `0.1.0` - Initial beta release
- `0.2.0` - Added new features
- `0.2.1` - Bug fixes
- `1.0.0` - First stable release

## Troubleshooting

### Upload fails with 403 error
- Check API token is correct in `~/.pypirc`
- Ensure token has upload permissions

### Package already exists
- Version numbers cannot be reused
- Increment version in `pyproject.toml`
- Rebuild: `python -m build`

### Import errors after installation
- Check `pyproject.toml` package configuration
- Verify `__init__.py` files exist in all packages
- Test locally: `pip install -e .`

### Missing files in distribution
- Update `MANIFEST.in` to include files
- Rebuild and verify: `tar tzf dist/*.tar.gz`

## Automation (Future)

Consider setting up GitHub Actions for:
- Automated testing on push
- Automated publishing on tag creation
- Version bumping automation

Example workflow location: `.github/workflows/publish.yml`
