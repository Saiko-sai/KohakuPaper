"""
Configuration settings for KohakuPaper
"""

from pathlib import Path

# Base directories
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
CACHE_DIR = PROJECT_ROOT / ".cache"

# Paper lists source
PAPERLISTS_REPO = "papercopilot/paperlists"
PAPERLISTS_RAW_URL = "https://raw.githubusercontent.com/papercopilot/paperlists/main"
PAPERLISTS_API_URL = "https://api.github.com/repos/papercopilot/paperlists/contents"

# Server settings
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 48890

# Available conferences (mapped to folder names in paperlists repo)
CONFERENCES = {
    # Machine Learning
    "iclr": "ICLR",
    "nips": "NeurIPS",
    "icml": "ICML",
    "aaai": "AAAI",
    "ijcai": "IJCAI",
    "aistats": "AISTATS",
    "colt": "COLT",
    "uai": "UAI",
    "automl": "AutoML",
    # Computer Vision
    "cvpr": "CVPR",
    "iccv": "ICCV",
    "eccv": "ECCV",
    "wacv": "WACV",
    "3dv": "3DV",
    # Graphics
    "siggraph": "SIGGRAPH",
    "siggraphasia": "SIGGRAPH Asia",
    # NLP
    "emnlp": "EMNLP",
    "acl": "ACL",
    "naacl": "NAACL",
    "coling": "COLING",
    "colm": "COLM",
    # Robotics
    "icra": "ICRA",
    "iros": "IROS",
    "corl": "CoRL",
    "rss": "RSS",
    # Others
    "kdd": "KDD",
    "acmmm": "ACM MM",
    "www": "WWW",
}

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)
