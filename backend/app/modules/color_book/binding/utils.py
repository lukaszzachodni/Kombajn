
import os
import shutil

def clean_empty_dirs(path, messenger):
    for dirpath, dirnames, filenames in os.walk(path):
        if not dirnames and not filenames:
            try:
                os.rmdir(dirpath)
                messenger.info(f"Removed empty directory: {dirpath}")
            except OSError as e:
                messenger.warning(f"Could not remove directory {dirpath}: {e}")
