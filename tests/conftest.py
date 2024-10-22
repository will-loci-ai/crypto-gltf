from pathlib import Path

import pytest
from crypto_gltf import Asset
from crypto_gltf.data.types import FileType
from crypto_gltf.io.file.base_file import BaseFile
from crypto_gltf.io.file.file import File

TEST_ASSET_DIR = Path(__file__).parent / "assets"
ASSET_PATHS = [
    p for p in TEST_ASSET_DIR.glob("*") if p.suffix.lower() in FileType.ASSET.extensions
]
CRYPTO_SYSTEMS = [
    "AdaptiveV1",
    "AdaptiveV2",
    "AdaptiveV3",
]


@pytest.fixture(scope="session", params=ASSET_PATHS, ids=lambda p: p.name)
def asset_path(request) -> str:
    """Return each available asset path."""
    return str(request.param)


@pytest.fixture(scope="function")
def asset(asset_path) -> Asset:
    """Return asset object for each test asset filepath."""
    return Asset.load(asset_path)


@pytest.fixture(scope="class")
def invalid_asset_file_path() -> Path:
    """Return an invalid asset path."""
    return TEST_ASSET_DIR / "invalid" / "fake_asset.glb"


@pytest.fixture(scope="function")
def file(asset_path) -> BaseFile:
    """Return asset file for each test asset filepath."""
    return File(asset_path)
