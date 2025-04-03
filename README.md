# manufacturing-agent-mongo

## 🧠 Overview
This project contains the backend and frontend for a smart document indexing agent using MongoDB, AWS Lambda, Textract, and VoyageAI.

---

## ✨ Setup Instructions (Backend)

### 📁 Project Structure
```
manufacturing-agent-mongo/
│
├── backend/                  # CDK app and Lambda code
│   ├── lambda/               # Your Lambda function code (e.g. index_new_document.py)
│   └── layer/                # Shared Python layer for Lambda
│       └── python/           # Required structure for Lambda layer packaging
│
├── frontend/                 # Your frontend project (if any)
├── README.md                 # This file
└── requirements.txt          # Python deps for CDK only
```

---

## 🐍 Lambda Dependencies via Docker (ARM64)
If your Lambda function depends on native packages like `numpy` (used internally by `voyageai`), and you're building on a Mac (ARM), you must build a compatible Lambda layer.

### Step 1: Prepare the Layer Directory
```bash
mkdir -p backend/layer/python
```

### Step 2: Build the Lambda Layer Using Docker (ARM64)
```bash
docker run --rm --platform linux/arm64 \
  -v "$PWD/backend/layer":/layer \
  --entrypoint bash \
  public.ecr.aws/lambda/python:3.11 \
  -c "pip install --no-cache-dir voyageai pymongo[srv] -t /layer/python"
```

> 💡 This ensures that compiled packages like numpy are built for the correct architecture (`arm64`).

### Step 3: Verify Compiled Files
```bash
find backend/layer/python/numpy -name "*.so"
```
You should see files with names ending in `.cpython-311-aarch64-linux-gnu.so`.

---

## 💠 CDK Deployment

### Step 1: Activate your virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Step 2: Deploy
```bash
cd backend
cdk deploy
```

---

## ✅ Verifying in CloudWatch
You can check if the correct versions of `numpy` and `pymongo` are being used by adding this to your Lambda handler (for debugging):
```python
import numpy
import pymongo
print("✅ numpy version:", numpy.__version__)
print("✅ numpy path:", numpy.__file__)
print("✅ pymongo version:", pymongo.__version__)
```

---

## 🧼 Common Pitfalls
- **Missing `numpy.core._multiarray_umath`**: This means you're using numpy built for the wrong architecture.
- **x86_64/arm64 mismatch**: Ensure your Lambda function architecture matches the one used when building the layer.
  - You can check it via CLI:
    ```bash
    aws lambda get-function-configuration \
      --function-name IndexNewDocument \
      --query 'Architectures'
    ```
  - If needed, change it in your CDK code:
    ```python
    architecture=_lambda.Architecture.ARM_64
    ```

---

## 💡 Pro Tip
If you’re ever unsure, you can even dynamically install packages in the Lambda runtime (not recommended for prod):
```python
import subprocess, sys
subprocess.run([sys.executable, '-m', 'pip', 'install', 'voyageai', '-t', '/tmp/dep'])
sys.path.insert(0, '/tmp/dep')
import voyageai
```

---

## 📵 Questions?
Reach out to @chleiva for any clarifications.

---
Happy hacking! 🚰

