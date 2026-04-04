import os
from dotenv import load_dotenv

# Wczytaj zmienne środowiskowe z pliku .env (jeśli istnieje)
load_dotenv()

# Get the absolute path to the directory where this script is located (src/)
_current_dir = os.path.dirname(os.path.abspath(__file__))
# Go up one level to get the project root directory
PROJECT_ROOT = os.path.dirname(_current_dir)

# Domyślne wymiary przycięcia w calach
TRIM_WIDTH_IN = float(os.getenv('TRIM_WIDTH_IN', 6))
TRIM_HEIGHT_IN = float(os.getenv('TRIM_HEIGHT_IN', 9))

# Główny katalog z projektami kolorowanek
COLORBOOKS_BASE_DIR = os.getenv('COLORBOOKS_DIR', '/home/lakis90/projects/genai_projects/colorbooks/')

# Ścieżka do pliku z rozmiarami okładek
COVER_SIZES_PATH = os.path.join(PROJECT_ROOT, 'data', 'cover_sizes.json')

# Domyślne ścieżki dla generowania Excela
KDP_JSON_PATH = os.path.join(PROJECT_ROOT, 'data', 'KDPUploaderJSON.json')
KDP_TEMPLATE_PATH = os.path.join(PROJECT_ROOT, 'data', 'KDPUploader_template_v4.18.xlsx')
KDP_OUTPUT_PATH = os.path.join(PROJECT_ROOT, 'data', 'KDPUploader.xlsx')
PROJECT_SCHEMA_PATH = os.path.join(PROJECT_ROOT, 'data', 'project_scheme.json')

# Ścieżki do czcionek
DEFAULT_FONT_PATH = os.path.join(PROJECT_ROOT, 'assets', 'fonts', 'ComicNeue-Regular.ttf')
BOLD_FONT_PATH = os.path.join(PROJECT_ROOT, 'assets', 'fonts', 'ComicNeue-Bold.ttf')
