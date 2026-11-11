
import sys
from backend import launch_webview, launch_web, launch_cli

if __name__ == "__main__":
    if "--cli" in sys.argv:
        launch_cli()
    elif "--browser" in sys.argv:
        launch_web()
    else:
        launch_webview()
