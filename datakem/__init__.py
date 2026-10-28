from .data import fetchAssetData
from .workflow import runWorkflow

__all__ = ["fetchAssetData", "runWorkflow"]


def main() -> None:
    runWorkflow()

