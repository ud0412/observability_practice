"""Learner-run S3 API and persistence check. Does not deploy sample apps."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import boto3
from botocore.config import Config

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
from state import check_owner, state_path

parser = argparse.ArgumentParser()
parser.add_argument("--endpoint", default="http://127.0.0.1:8333")
parser.add_argument("--keep", action="store_true", help="Keep the test object for Pod recovery verification")
parser.add_argument("--read-existing", action="store_true", help="Read the previously kept object without uploading")
args = parser.parse_args()
path = state_path()
check_owner(path)
keys = json.loads((path / "credentials.json").read_text())
client = boto3.client("s3", endpoint_url=args.endpoint, region_name="us-east-1",
                      aws_access_key_id=keys["S3_ACCESS_KEY"], aws_secret_access_key=keys["S3_SECRET_KEY"],
                      config=Config(s3={"addressing_style": "path"}))
expected = {"mimir-blocks", "loki-data", "tempo-traces"}
assert expected <= {b["Name"] for b in client.list_buckets()["Buckets"]}, "Required buckets are missing"
record_path = path / "s3-check.json"
bucket, key = "mimir-blocks", "lab-check/pod-recovery.txt"
body = b"observability lab: persistent S3 object"
if args.read_existing:
    record = json.loads(record_path.read_text())
    bucket, key = record["bucket"], record["key"]
else:
    client.put_object(Bucket=bucket, Key=key, Body=body)
actual = client.get_object(Bucket=bucket, Key=key)["Body"].read()
digest = hashlib.sha256(actual).hexdigest()
assert actual == body, "S3 content mismatch"
if args.read_existing:
    assert digest == record["sha256"]
elif args.keep:
    record_path.write_text(json.dumps({"bucket": bucket, "key": key, "sha256": digest}))
else:
    client.delete_object(Bucket=bucket, Key=key)
print("S3 authentication, bucket listing and object read verified" + ("; object kept" if args.keep else ""))
