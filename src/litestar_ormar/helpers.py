from importlib import import_module
import pkgutil
from pathlib import Path


def load_all_models(
    apps_path: Path, prefix: str = "", models_path: str = "models"
) -> None:
    """Load all models from all apps.

    Scans all modules in indicated path for model files and imports them.
    Helpful for alembic.

    apps_path: Path to the apps folder.
    prefix: Prefix to add to all models module paths so that they can be imported.
    models_path: Path to the models file.
    """
    modules = pkgutil.walk_packages(
        path=[str(apps_path.resolve())],
        prefix=prefix,
    )
    for module in modules:
        if module.name.endswith(models_path):
            import_module(module.name)
