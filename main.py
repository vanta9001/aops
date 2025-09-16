#!/usr/bin/env python3
"""
duplicate_randomly.py

Duplicate files from the current directory into images/ with new names,
choosing sources randomly.

Usage examples:
  python duplicate_randomly.py                # run with defaults
  python duplicate_randomly.py --dry-run      # show planned operations but don't copy
  python duplicate_randomly.py --no-reuse     # try not to reuse a source file
"""

from pathlib import Path
import random
import shutil
import argparse
import csv
import sys

# ---------- CONFIG: source files (in root) and destination names (we will use basename) ----------
SOURCE_FILES = [
    "download (1).jpg",
    "download (2).jpg",
    "download (3).jpg",
    "download (4).jpg",
    "download.jpg",
    "images (1).jpg",
    "images (2).jpg",
    "images (3).jpg",
    "images (4).jpg",
    "images (5).jpg",
    "images.jpg",
]

DEST_NAMES = [
"images/1.svg",
"images/2.svg",
"images/3.svg",
"images/alumni_m.jpg",
"images/alumni.jpg",
"images/aops-academy.svg",
"images/aops-ba.svg",
"images/aops-logo-dev.svg",
"images/aops-logo.png",
"images/aops-logo.svg",
"images/aops-modal-help-sprite.png",
"images/aops-online-footer.svg",
"images/aops-online-mobile.svg",
"images/aops-online.svg",
"images/bellevue.png",
"images/bg-hive.svg",
"images/bronze.svg",
"images/fa-chevron-right.svg",
"images/facebook.svg",
"images/frisco.png",
"images/gold.svg",
"images/hamburger.svg",
"images/hero-circle.svg",
"images/hero-galaxy-curve-dt.png",
"images/hero-galaxy-curve.png",
"images/icon-academy.svg",
"images/icon-ba.svg",
"images/icon-online.svg",
"images/icon-search.svg",
"images/IMO-2024-full-team-mobile.jpg",
"images/IMO-2024-full-team.jpg",
"images/member0.png",
"images/member1.png",
"images/member2.png",
"images/member3.png",
"images/member4.png",
"images/member5.png",
"images/online-android-chrome-192x192.png",
"images/online-apple-touch-icon.png",
"images/online-favicon.ico",
"images/pattern-aops.png",
"images/pattern-online-gray.png",
"images/pinterest.svg",
"images/princeton.png",
"images/sandiego-cv.png",
"images/santaclara.png",
"images/silver.svg",
"images/sp-atlantic.svg",
"images/sp-forbes.svg",
"images/sp-newyorker.svg",
"images/sp-quanta.svg",
"images/sp-wired.svg",
"images/subscribe_blob.svg",
"images/twitter.svg",
"images/wasc.png",
]

# -----------------------------------------------------------------------------------------------

def main(*, no_reuse=False, dry_run=False, verbose=True):
    cwd = Path.cwd()
    images_dir = cwd / "images"
    if not dry_run:
        images_dir.mkdir(parents=True, exist_ok=True)

    # Normalize sources and check existence
    sources = []
    for name in SOURCE_FILES:
        p = cwd / name
        if not p.exists():
            print(f"WARNING: source file not found in root: {name}", file=sys.stderr)
        else:
            sources.append(p)

    if not sources:
        print("ERROR: No valid source files found in the current directory. Aborting.", file=sys.stderr)
        return 1

    # group sources by extension
    ext_to_sources = {}
    for s in sources:
        ext = s.suffix.lower()
        ext_to_sources.setdefault(ext, []).append(s)

    # Build list of destination basenames
    dest_basenames = [Path(d).name for d in DEST_NAMES]

    # Copy plan: dest -> chosen source
    plan = []
    available_sources = sources.copy()  # for no_reuse mode

    # If no_reuse and there are fewer sources than destinations, we'll allow reuse after exhausting.
    for dest_name in dest_basenames:
        dest_path = images_dir / dest_name
        dest_ext = Path(dest_name).suffix.lower()

        # Prefer same-extension sources if present
        candidates = ext_to_sources.get(dest_ext, None)
        if candidates:
            chosen = random.choice(candidates)
        else:
            # fallback to any source
            if not available_sources:
                # if we've exhausted unique sources in no_reuse mode, reset available_sources
                available_sources = sources.copy()
            if no_reuse:
                chosen = random.choice(available_sources)
                try:
                    available_sources.remove(chosen)
                except ValueError:
                    # already removed, ignore
                    pass
            else:
                chosen = random.choice(sources)

        plan.append((dest_path, chosen))

    # Report / execute
    if verbose:
        print(f"Found {len(sources)} source files, preparing to produce {len(plan)} files in '{images_dir}'.")
    mapping_path = images_dir / "mapping.csv"
    if dry_run:
        print("DRY RUN: No files will actually be copied.")
    for dest_path, src_path in plan:
        if verbose:
            print(f"{src_path.name} -> {dest_path.relative_to(cwd)}")
    # Write mapping CSV and copy files
    if not dry_run:
        try:
            with open(mapping_path, "w", newline='', encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["destination", "source"])
                for dest_path, src_path in plan:
                    # Ensure parent exists (images_dir already exists)
                    # Copy (binary-safe)
                    try:
                        shutil.copy2(src_path, dest_path)
                    except Exception as e:
                        print(f"ERROR copying {src_path} -> {dest_path}: {e}", file=sys.stderr)
                    writer.writerow([str(dest_path.relative_to(cwd)), str(src_path.relative_to(cwd))])
            if verbose:
                print(f"Done. mapping saved to: {mapping_path}")
        except Exception as e:
            print(f"ERROR writing mapping or copying files: {e}", file=sys.stderr)
            return 2

    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Duplicate root files randomly into images/ with given names.")
    parser.add_argument("--no-reuse", action="store_true", help="Try not to reuse the same source file (if possible).")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done but don't copy files.")
    parser.add_argument("--quiet", action="store_true", help="Minimal output.")
    args = parser.parse_args()
    rc = main(no_reuse=args.no_reuse, dry_run=args.dry_run, verbose=not args.quiet)
    sys.exit(rc)
