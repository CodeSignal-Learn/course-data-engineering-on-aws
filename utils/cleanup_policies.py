#!/usr/bin/env python3
"""
Detach & delete the 4 CourseLab policies created by apply_all_policies.py.

Usage:
  python cleanup_all_policies.py                  # acts on user 'learner'
  python cleanup_all_policies.py --user alice
  python cleanup_all_policies.py --role CourseLabRole
"""

import argparse
import sys
import boto3
from botocore.exceptions import ClientError

POLICY_NAMES = [
    "CourseLab-S3",
    "CourseLab-Streaming",
    "CourseLab-Glue",
    "CourseLab-IAM-STS",
]

def detach_policy(iam, principal_type: str, principal_name: str, policy_arn: str):
    try:
        if principal_type == "user":
            iam.detach_user_policy(UserName=principal_name, PolicyArn=policy_arn)
        else:
            iam.detach_role_policy(RoleName=principal_name, PolicyArn=policy_arn)
        print(f"✅ Detached {policy_arn} from {principal_type} {principal_name}")
    except iam.exceptions.NoSuchEntityException:
        print(f"ℹ️  Not attached (or already removed): {policy_arn}")
    except ClientError as e:
        print(f"⚠️  Could not detach {policy_arn}: {e.response.get('Error', {}).get('Message')}")
    except Exception as e:
        print(f"⚠️  Could not detach {policy_arn}: {e}")

def delete_policy(iam, policy_arn: str):
    try:
        # Delete non-default versions first (if any)
        versions = iam.list_policy_versions(PolicyArn=policy_arn)["Versions"]
        for v in versions:
            if not v["IsDefaultVersion"]:
                iam.delete_policy_version(PolicyArn=policy_arn, VersionId=v["VersionId"])
        iam.delete_policy(PolicyArn=policy_arn)
        print(f"✅ Deleted {policy_arn}")
    except iam.exceptions.NoSuchEntityException:
        print(f"ℹ️  Policy already gone: {policy_arn}")
    except ClientError as e:
        code = e.response.get("Error", {}).get("Code")
        msg = e.response.get("Error", {}).get("Message")
        if code == "DeleteConflict":
            print(f"⚠️  Cannot delete {policy_arn}: still attached to another entity. Detach everywhere first.")
        else:
            print(f"⚠️  Could not delete {policy_arn}: {msg}")
    except Exception as e:
        print(f"⚠️  Could not delete {policy_arn}: {e}")

def main():
    parser = argparse.ArgumentParser()
    tgt = parser.add_mutually_exclusive_group()
    tgt.add_argument("--user", help="IAM user name (default: learner)")
    tgt.add_argument("--role", help="IAM role name")
    args = parser.parse_args()

    principal_type = "role" if args.role else "user"
    principal_name = args.role if args.role else (args.user or "learner")

    iam = boto3.client("iam")
    sts = boto3.client("sts")
    account_id = sts.get_caller_identity()["Account"]

    print(f"Target: {principal_type} {principal_name}")
    confirm = input("This will detach & delete CourseLab policies. Proceed? (y/N): ").strip().lower()
    if confirm not in ("y", "yes"):
        print("Cancelled.")
        sys.exit(1)

    policy_arns = [f"arn:aws:iam::{account_id}:policy/{name}" for name in POLICY_NAMES]

    print("\n=== Detaching ===")
    for arn in policy_arns:
        detach_policy(iam, principal_type, principal_name, arn)

    print("\n=== Deleting ===")
    for arn in policy_arns:
        delete_policy(iam, arn)

    print("\n🎉 Cleanup complete.")

if __name__ == "__main__":
    main()

