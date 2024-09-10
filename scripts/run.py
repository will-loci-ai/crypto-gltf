from pathlib import Path
from tempfile import TemporaryDirectory

from crypto_gltf import Asset
from crypto_gltf.data.types import FileType

"""Local testing"""
TEST_ASSET_DIR = Path(__file__).parent.parent / "tests" / "assets"
ASSET_PATHS = [
    p for p in TEST_ASSET_DIR.glob("*") if p.suffix.lower() in FileType.ASSET.extensions
]
if __name__ == "__main__":

    filepath = ASSET_PATHS[0] 
    asset = Asset.load(str(filepath))

    with TemporaryDirectory() as tmp_dir:

        plnm_plaintext = asset.file.plnm.__copy__()
        encryption_response = asset.encrypt()
        export_path = asset.save(tmp_dir)

        encrypted_asset = Asset.load(export_path)
        encrypted_asset.decrypt(
            k3=encryption_response.key.k3,
        )
        assert plnm_plaintext == encrypted_asset.file.plnm

        print()
