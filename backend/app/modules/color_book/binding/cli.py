
import argparse
import sys
import os
from backend.app.modules.color_book.binding.excel_generation.kdp_excel_generator import generate_kdp_excel
from backend.app.modules.color_book.binding import config
from backend.app.modules.color_book.binding.console import ConsoleMessenger
from backend.app.modules.color_book.binding.utils import clean_empty_dirs
from backend.app.modules.color_book.binding.processing.colorbook_processor import ColorbookProcessor

def main():
    messenger = ConsoleMessenger()
    parser = argparse.ArgumentParser(description='Create and manage colorbooks.')
    subparsers = parser.add_subparsers(dest='command')

    # --- Common arguments for processing commands ---
    processing_args = argparse.ArgumentParser(add_help=False)
    processing_args.add_argument('--extract-lines', action='store_true', help='Extract black lines from images before creating the PDF')
    processing_args.add_argument('--draw-title', action='store_true', help='Draw the title on the cover')
    processing_args.add_argument('--re-do', action='store_true', help='Force reprocessing of already processed projects')
    processing_args.add_argument('--trim_width', type=float, default=config.TRIM_WIDTH_IN, help='Trim width in inches')
    processing_args.add_argument('--trim_height', type=float, default=config.TRIM_HEIGHT_IN, help='Trim height in inches')

    # --- Process All Command ---
    process_all_parser = subparsers.add_parser(
        'process-all', 
        help='Process all colorbooks from the base directory', 
        parents=[processing_args]
    )
    process_all_parser.add_argument('--clean-empty', action='store_true', help='Clean up empty directories before processing')

    # --- Process Single Command ---
    process_single_parser = subparsers.add_parser(
        'process-single', 
        help='Process a single colorbook from a specified path', 
        parents=[processing_args]
    )
    process_single_parser.add_argument('--project-path', required=True, help='Absolute path to the project directory')

    # --- Deprecated Commands (for now) ---
    pdf_parser = subparsers.add_parser('create-pdf', help='DEPRECATED: Use process-single instead')

    args = parser.parse_args()
    processor = ColorbookProcessor(messenger, args)

    if args.command == 'process-all':
        if args.clean_empty:
            messenger.info("Cleaning up empty directories...")
            clean_empty_dirs(config.COLORBOOKS_BASE_DIR, messenger)
        processor.process_all_colorbooks()

    elif args.command == 'process-single':
        if not os.path.isdir(args.project_path):
            messenger.error(f"Error: Provided project path is not a valid directory: {args.project_path}")
            sys.exit(1)
        processor.process_project(args.project_path)

    elif args.command == 'create-pdf':
        messenger.error("The 'create-pdf' command is deprecated. Please use 'process-single' instead.")
        sys.exit(1)

    else:
        parser.print_help()

if __name__ == '__main__':
    main()
