#!/usr/bin/env python3
"""
Create and attach course policies (from ./policies/*.json) to a user/role.

Usage:
  python apply_course_policies.py                   # attaches to user 'learner'
  python apply_course_policies.py --role CourseLabRole
  python apply_course_policies.py --user alice --dir ./my_policies
"""
import argparse
import os
from typing import List, Tuple, Optional
from common import attach_custom_policy  # local helper

# Default policy files (put these under ./policies/)
DEFAULT_POLICY_FILES: List[Tuple[str, str]] = [
    ("CourseLab-S3",            os.path.join("policies", "policy_s3.json")),
    ("CourseLab-Streaming",     os.path.join("policies", "policy_streaming.json")),
    ("CourseLab-Glue",          os.path.join("policies", "policy_glue.json")),
    ("CourseLab-IAM-STS",       os.path.join("policies", "policy_iam_sts.json")),
]

def attach_one(name: str, path: str, principal_type: str, principal_name: str) -> Optional[str]:
    if not os.path.exists(path):
        print(f"❌ Policy file missing: {path}")
        return None
    arn = attach_custom_policy(
        policy_name=name,
        policy_json_path=path,
        attach_to_type=principal_type,   # "user" or "role"
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
    group.add_argument("--user", help="IAM user name (default: learner)")
    group.add_argument("--role", help="IAM role name")
    parser.add_argument("--dir", default="policies", help="Folder with policy JSON files")
    args = parser.parse_args()

    principal_type = "role" if args.role else "user"
    principal_name = args.role if args.role else (args.user or "learner")

    # Build file list using --dir
    policy_files = [(name, os.path.join(args.dir, os.path.basename(path))) for name, path in DEFAULT_POLICY_FILES]

    print("=== Applying Course Policies ===")
    print(f"Target: {principal_type} {principal_name}")
    print(f"Policy folder: {args.dir}\n")

    attached, failed = [], []
    for name, path in policy_files:
        (attached if attach_one(name, path, principal_type, principal_name) else failed).append(name)

    print("\n=== Summary ===")
    if attached: print("Attached:", ", ".join(attached))
    if failed:   print("Failed:  ", ", ".join(failed))
    if failed: exit(1)
    print("🎉 Done.")

if __name__ == "__main__":
    main()

