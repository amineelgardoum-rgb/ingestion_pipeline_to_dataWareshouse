import sys
from src.pipeline import run_full_pipeline

def main():
    """Project entry point."""
    try:
        run_full_pipeline()
    except KeyboardInterrupt:
        print("\nPipeline interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
