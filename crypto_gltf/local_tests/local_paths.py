import glob
from pathlib import Path

ASSET_IMPORT_DIR = (
    Path(__file__).parent.parent.parent.parent.resolve() / "assets" / "import"
)
ASSET_EXPORT_DIR = (
    Path(__file__).parent.parent.parent.parent.resolve() / "assets" / "export"
)
LOCI_ASSET_DIR = (
    Path(__file__).parent.parent.parent.parent.resolve() / "assets" / "loci_assets"
)
IMAGES_DIR = Path(__file__).parent.parent.parent.parent.resolve() / "assets" / "images"
PAPER_ASSETS_DIR = (
    Path(__file__).parent.parent.parent.parent.resolve()
    / "assets"
    / "paper_figs"
    / "assets"
)

PAPER_DIR = (
    Path(__file__).parent.parent.parent.parent.resolve() / "assets" / "paper_figs"
)
PRINCETON = (
    Path(__file__).parent.parent.parent.parent.resolve()
    / "multimediaretrieval"
    / "Datasets"
    / "Princeton"
)

XL = (
    Path(__file__).parent.parent.parent.parent.resolve()
    / "assets"
    / "paper_figs"
    / "xl_assets"
)
supported = (".off", ".glb", "gltf")
asset_paths = [path for path in glob.glob(str(ASSET_IMPORT_DIR / "**"), recursive=True)]
obj_assets = [path for path in asset_paths if path.lower().endswith(".obj")]
gltf_assets = [path for path in asset_paths if path.lower().endswith(".gltf")]
glb_assets = [path for path in asset_paths if path.lower().endswith(".glb")]
off_assets = [path for path in asset_paths if path.lower().endswith(".off")]
loci_assets = [
    path
    for path in glob.glob(str(LOCI_ASSET_DIR / "**"), recursive=True)
    if path.endswith(supported)
]
princeton_assets = [
    path
    for path in glob.glob(str(PRINCETON / "**"), recursive=True)
    if path.endswith(supported)
]

paper_figs_paths = [
    path
    for path in glob.glob(str(PAPER_ASSETS_DIR / "**"), recursive=True)
    if path.lower().endswith(supported)
]
xl_paths = [
    path
    for path in glob.glob(str(XL / "**"), recursive=True)
    if path.lower().endswith(supported)
]


image_paths = [
    path
    for path in glob.glob(str(IMAGES_DIR / "**"), recursive=True)
    if path.lower().endswith((".jpg", ".png"))
]
