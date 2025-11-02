import re
import os
import sys

def get_version():
    # The __init__.py is in the current directory in GitHub Actions
    file_path = "__init__.py"
    
    if not os.path.exists(file_path):
        print("::error title=File Not Found::Could not find __init__.py")
        return None

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
