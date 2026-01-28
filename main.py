# main.py
"""
Swem Team Trading Suite: Main Entry Point
Orchestrates the strategy auditor application.
"""

import sys
from gui import launch_gui

def main():
    """Main application entry"""
    try:
        launch_gui()
    except KeyboardInterrupt:
        print("\nApplication terminated by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
