# Publishing msd-sdk to PyPI

## Quick Start

```bash
python publish.py
```

This will:
1. Prompt for your PyPI API token
2. Build the package with `uv build`
3. Publish to PyPI

## Publishing Updates

### Bump Version and Publish

```bash
# Bump patch version (X.Y.Z -> X.Y.Z+1)
python publish.py --bump

# Bump minor version (X.Y.Z -> X.Y+1.0)
python publish.py --bump minor

# Bump major version (X.Y.Z -> X+1.0.0)
python publish.py --bump major
```

### Manual Version Update

1. Edit version in `pyproject.toml`:
   ```toml
   version = "X.Y.Z"
   ```

2. Edit version in `src/msd_sdk/__init__.py`:
   ```python
   __version__ = "X.Y.Z"
   ```

3. Run publish script:
   ```bash
   python publish.py
   ```

4. Commit changes:
   ```bash
   git add -A && git commit -m "Release vX.Y.Z"
   git tag vX.Y.Z
   git push && git push --tags
   ```

## PyPI Token

### Getting a Token

1. Go to https://pypi.org/manage/account/token/
2. Click "Add API token"
3. Name: `msd-sdk` (or any name)
4. Scope: "Entire account" or "Project: msd-sdk" (after first publish)
5. Copy token (starts with `pypi-`)

### Storing the Token

The script prompts for the token each time (secure, no storage).

For automation, set environment variable:
```bash
export UV_PUBLISH_TOKEN=pypi-xxx
```

## Verify Publication

After publishing:
```bash
pip install msd-sdk --upgrade
python -c "import msd_sdk; print(msd_sdk.__version__)"
```

View on PyPI: https://pypi.org/project/msd-sdk/

## Troubleshooting

### Version Already Exists
PyPI doesn't allow re-uploading the same version. Bump the version number.

### Token Invalid
Ensure token starts with `pypi-` and hasn't expired.

### Build Fails
Check `pyproject.toml` syntax. Run `uv build` manually to see errors.
