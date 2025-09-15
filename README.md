# Data Engineering on AWS

A comprehensive repository containing templates, scripts, and resources for the **“Data Engineering on AWS”** learning path. This repository currently provides hands-on materials for **Course 1: Designing & Ingesting Data into AWS Data Lakes**.

## 🎯 Purpose

This repository provisions IAM access for Course 1 labs and includes a cleanup utility. It uses small Python scripts with `boto3` to create **customer-managed IAM policies**, attach them to a **user or role**, and remove them afterward.

* **Course 1 Policy Setup**: Create and attach IAM policies for S3, Kinesis/Firehose, Glue, and IAM/STS.
* **Cleanup Utility**: Detach and delete the created policies to reset the environment.
* **Extensible**: Reuse the same script later by pointing to a different policy folder with `--dir`.

## 🏗 Repository Structure

### 📋 Templates

| Template                                      | Purpose                                                          | Used In  | New Features                                                              |
| --------------------------------------------- | ---------------------------------------------------------------- | -------- | ------------------------------------------------------------------------- |
| `attach_policies_designing_ingesting_data.py` | Creates & attaches the 4 Course 1 IAM policies to a user or role | Course 1 | Idempotent policy creation/attachment, policy folder override via `--dir` |


### 🔧 Template Components

* **`common.py`**: Shared helper functions for:

  * Creating customer-managed IAM policies from JSON
  * Attaching policies to IAM users or roles (idempotent)

* **`policies/`** (Course 1):

  * `policy_s3.json` — S3 bucket/object permissions for lab buckets
  * `policy_streaming.json` — Kinesis & Firehose admin/data-plane
  * `policy_glue.json` — Glue catalog/crawler + S3 read for Glue
  * `policy_iam_sts.json` — `iam:PassRole` (as written) + `sts:GetCallerIdentity`

### 🛠 Utilities

* **`utils/cleanup_policies.py`**: Detaches and deletes the 4 Course 1 policies from the specified user/role.

### 📦 Dependencies


```bash
pip install -r requirements.txt
```

---

## 🚀 Quick Start

### Prerequisites

* AWS account with permission to **create, attach, detach, and delete IAM policies**
* AWS credentials configured (AWS CLI or environment variables)
* Python **3.9+**

### Installation

```bash
# (optional) create and activate a virtual environment
python -m venv .venv && source .venv/bin/activate

# install dependencies
pip install -r requirements.txt
```

### Usage

#### Course 1: Designing & Ingesting Data into AWS Data Lakes

```bash
cd templates

# Attach to default IAM user 'learner'
python attach_policies_designing_ingesting_data.py
```

---

## 🔄 Resource Management

### Cleanup

```bash
cd utils

# Detach from default user 'learner' and delete all policies
python cleanup_policies.py
```
