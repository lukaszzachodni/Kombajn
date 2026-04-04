import argparse
from backend.app.modules.color_book.generator.core.app import App
from dotenv import load_dotenv


def main():
    """
    Główna funkcja uruchamiająca aplikację.
    """
    load_dotenv()

    parser = argparse.ArgumentParser(description="Coloring Book Generator")
    parser.add_argument(
        "--iterations",
        type=int,
        default=1,
        help="Number of times to run the project generation process.",
    )
    args = parser.parse_args()

    print("Launching coloring book generator...")
    for i in range(args.iterations):
        if args.iterations > 1:
            print(f"--- Starting iteration {i + 1} of {args.iterations} ---")

        # Create a new App instance for each iteration for complete isolation
        app = App()
        app.run()

    print("Coloring book generator finished operation.")


if __name__ == "__main__":
    main()
