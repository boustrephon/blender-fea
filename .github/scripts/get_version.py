import re
import os
import sys

def get_version():
    # Check if we're in the right directory and file exists
    file_path = "__init__.py"
    
    if not os.path.exists(file_path):
        print("::error title=File Not Found::Could not find __init__.py")
        return None

    with open(file_path, "r") as f:
        content = f.read()
        # Regex to handle both single and double quotes
        match = re.search(r'bl_info\s*=\s*\{[^{]*?["\']version["\']\s*:\s*\((.*?)\)[^}]*?\}', content, re.DOTALL)
        if match:
            version_tuple_str = match.group(1)
            # Clean up the version string
            version = version_tuple_str.replace(" ", "").replace(",", ".").replace("'", "").replace('"', '')
            return version
        else:
            print("::error title=Version Extraction Failed::Could not find version in __init__.py")
            return None

if __name__ == "__main__":
    version = get_version()
    if version:
        # New method: Write to GITHUB_OUTPUT file
        with open(os.environ['GITHUB_OUTPUT'], 'a') as fh:
            print(f'version={version}', file=fh)
    else:
        sys.exit(1)
