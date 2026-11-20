from pathlib import Path

from infrastructure.web.main import main

BASE_DIR = Path(__file__).resolve().parent

main(BASE_DIR)
