"""Hand-in program for the make.fun news-image entry (stdlib only).

Copies entry.png from the repository root (next to this file) into the
output directory named by MAKEFUN_OUTPUT_DIR (default /output).
"""
import os
import shutil


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    shutil.copyfile(src, os.path.join(out_dir, "entry.png"))


if __name__ == "__main__":
    main()
