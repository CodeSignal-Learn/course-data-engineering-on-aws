#!/usr/bin/env python3
"""
Create & attach all 4 course policies from ./policies to a user/role.

Usage:
  python apply_all_policies.py                 # attaches to user 'learner'
  python apply_all_policies.py --user alice    # attach to a different user
  python apply_all_policies.py --role CourseLabRole
  python apply_all_policies.py --dir ./policies  # custom policies folder
"""

import argparse
import os
from typing import List, Tuple, Optional
from common import attach_custom_policy  # uses your existing helper

# Policy name -> file mapping (filenames must exist under --dir)
POLICY_FILES: List[Tuple[str, str]] = [
    ("CourseLab-S3",        "policy_s3.json"),
    ("CourseLab-Streaming", "policy_streaming.json"),
    ("CourseLab-Glue",      "policy_glue.json"),
    ("CourseLab-IAM-STS",   "policy_iam_sts.json"),
]

def attach_one(name: str, path: str, principal_type: str, principal_name: str) -> Optional[str]:
    if not os.path.exists(path):
        print(f"❌ Missing policy file: {path}")
        return None
    arn = attach_custom_policy(
        policy_name=name,
        policy_json_path=path,
        attach_to_type=principal_type,  # "user" or "role"
        attach_to_name=principal_name,
    )
    if arn:
        print(f"✅ Attached {name} → {principal_type} {principal_name}")
    else:
        print(f"❌ Failed to attach {name} → {principal_type} {principal_name}")
    return arn

def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--user", help="IAM user to attach to (default: learner)")
    group.add_argument("--role", help="IAM role to attach to")
    parser.add_argument("--dir", default="policies", help="Folder with policy JSON files")
    args = parser.parse_args()

    principal_type = "role" if args.role else "user"
    principal_name = args.role if args.role else (args.user or "learner")

    print("=== Applying Course Policies ===")
    print(f"Target: {principal_type} {principal_name}")
    print(f"Policy folder: {args.dir}\n")

    attached, failed = [], []
    for name, fname in POLICY_FILES:
        path = os.path.join(args.dir, fname)
        (attached if attach_one(name, path, principal_type, principal_name) else failed).append(name)

    print("\n=== Summary ===")
    if attached: print("Attached:", ", ".join(attached))
    if failed:   print("Failed:  ", ", ".join(failed))
    if failed: exit(1)
    print("🎉 Done.")

if __name__ == "__main__":
    main()

