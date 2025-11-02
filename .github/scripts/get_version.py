import re
import os
import sys

def get_version():
    # Check if we're in the right directory and file exists
    if not os.path.exists("blender-fea/__init__.py"):
        # Try alternative path
        if os.path.exists("__init__.py"):
            file_path = "__init__.py"
        else:
            print("::error title=File Not Found::Could not find __init__.py")
            return None
    else:
        file_path = "blender-fea/__init__.py"

    with open(file_path, "r") as f:
        content = f.read()
        match = re.search(r'bl_info\s*=\s*\{[^{]*?["\']version["\']\s*:\s*\((.*?)\)[^}]*?\}', content, re.DOTALL)
        # match = re.search(r'bl_info\s*=\s*\{[^{]*?\'version\'\s*:\s*\((.*?)\)[^}]*?\}', content, re.DOTALL)
        if match:
            version_tuple_str = match.group(1)
            # Clean up the version string - handle potential quotes and spaces
            version = version_tuple_str.replace(" ", "").replace(",", ".").replace("'", "").replace('"', '')
            return version
        else:
            print("::error title=Version Extraction Failed::Could not find version in __init__.py")
            return None

if __name__ == "__main__":
    version = get_version()
    if version:
        print(f"::set-output name=version::{version}")
    else:
        sys.exit(1)
