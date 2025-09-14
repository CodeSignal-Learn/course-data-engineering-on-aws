import json
from typing import Optional, Tuple

import boto3
from botocore.exceptions import ClientError


def attach_policy(attach_to_type: str, attach_to_name: str, policy_arn: str) -> Tuple[bool, Optional[str]]:
    """
    Attach an existing IAM policy (by ARN) to a user or role.
    Returns (success, policy_arn_if_known).
    """
    iam = boto3.client("iam")

    # Check target principal exists
    try:
        if attach_to_type == "user":
            iam.get_user(UserName=attach_to_name)
        elif attach_to_type == "role":
            iam.get_role(RoleName=attach_to_name)
        else:
            print(f"❌ Unknown attach_to_type: {attach_to_type}")
            return False, None
    except iam.exceptions.NoSuchEntityException:
        print(f"❌ {attach_to_type.capitalize()} '{attach_to_name}' does not exist")
        return False, None

    # Already attached?
    try:
        if attach_to_type == "user":
            attached = iam.list_attached_user_policies(UserName=attach_to_name)
        else:
            attached = iam.list_attached_role_policies(RoleName=attach_to_name)
        if any(p.get("PolicyArn") == policy_arn for p in attached.get("AttachedPolicies", [])):
            print(f"✅ Policy already attached to {attach_to_type} {attach_to_name}")
            return True, policy_arn
    except ClientError as e:
        print(f"⚠️  Could not list attached policies: {e}")

    # Attach
    try:
        if attach_to_type == "user":
            iam.attach_user_policy(UserName=attach_to_name, PolicyArn=policy_arn)
        else:
            iam.attach_role_policy(RoleName=attach_to_name, PolicyArn=policy_arn)
        print(f"✅ Attached {policy_arn} to {attach_to_type} {attach_to_name}")
        return True, policy_arn
    except ClientError as e:
        print(f"❌ Failed to attach policy: {e}")
        return False, None


def create_policy(policy_name: str, policy_document: dict) -> Optional[str]:
    """
    Create (or resolve) a customer-managed IAM policy, returning its ARN.
    """
    iam = boto3.client("iam")
    sts = boto3.client("sts")
    account_id = sts.get_caller_identity()["Account"]
    policy_arn = f"arn:aws:iam::{account_id}:policy/{policy_name}"

    try:
        iam.create_policy(PolicyName=policy_name, PolicyDocument=json.dumps(policy_document))
        print(f"✅ Created IAM policy {policy_name}")
        return policy_arn
    except iam.exceptions.EntityAlreadyExistsException:
        print(f"✅ IAM policy {policy_name} already exists")
        return policy_arn
    except ClientError as e:
        print(f"❌ Failed to create policy {policy_name}: {e}")
        return None


def attach_custom_policy(
    policy_name: str,
    policy_json_path: str,
    attach_to_type: str,
    attach_to_name: str,
    replacements: Optional[dict] = None,
) -> Optional[str]:
    """
    Ensure a customer-managed policy exists from a JSON file and attach it to user/role.
    """
    try:
        with open(policy_json_path, "r", encoding="utf-8") as f:
            content = f.read()
        if replacements:
            for k, v in replacements.items():
                content = content.replace(k, v)
        document = json.loads(content)
    except Exception as e:
        print(f"❌ Failed to load policy JSON {policy_json_path}: {e}")
        return None

    policy_arn = create_policy(policy_name, document)
    if not policy_arn:
        return None

    ok, _ = attach_policy(attach_to_type, attach_to_name, policy_arn)
    return policy_arn if ok else None

