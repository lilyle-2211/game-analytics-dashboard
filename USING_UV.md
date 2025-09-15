# Managing Python Packages with uv

## 1. Add a Package
```
uv add <package-name>
```
This adds the package to your `pyproject.toml` and installs it.

## 2. Install All Packages from pyproject.toml
```
uv pip sync pyproject.toml
```
This installs all dependencies listed in `pyproject.toml`.

## 3. Remove a Package
```
uv remove <package-name>
```
This removes the package from `pyproject.toml` and uninstalls it.

## 4. List Installed Packages
```
uv pip list
```

## 5. Update All Packages
```
uv pip install -U -r pyproject.toml
```

---

- Only list your direct dependencies in `pyproject.toml`.
- uv will handle all sub-dependencies automatically.
- For more, see: https://github.com/astral-sh/uv
