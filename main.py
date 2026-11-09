"""
Sugo Grand Palace Hotel - Main Application Entrypoint
Launches the native PyWebView desktop window with frontend views from views/
"""

import sys
from backend import launch_webview, launch_web, launch_cli

if __name__ == "__main__":
    if "--cli" in sys.argv:
        launch_cli()
    elif "--browser" in sys.argv:
        launch_web()
    else:
        # Default: Launch pywebview native desktop application window
        launch_webview()
