import glob
from pathlib import Path

ASSET_IMPORT_DIR = (
    Path(__file__).parent.parent.parent.parent.parent.resolve() / "assets" / "import"
)
ASSET_EXPORT_DIR = (
    Path(__file__).parent.parent.parent.parent.parent.resolve() / "assets" / "export"
)
IMAGES_DIR = Path(__file__).parent.parent.parent.parent.parent.resolve() / "assets" / "images"

asset_paths = [path for path in glob.glob(str(ASSET_IMPORT_DIR / "**"), recursive=True)]
obj_assets = [path for path in asset_paths if path.lower().endswith(".obj")]
gltf_assets = [path for path in asset_paths if path.lower().endswith(".gltf")]
glb_assets = [path for path in asset_paths if path.lower().endswith(".glb")]
off_assets = [path for path in asset_paths if path.lower().endswith(".off")]

image_paths = [
    path
    for path in glob.glob(str(IMAGES_DIR / "**"), recursive=True)
    if path.lower().endswith((".jpg", ".png"))
]
