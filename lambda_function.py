import boto3
import subprocess
import os

s3 = boto3.client('s3')

# YOUR BUCKETS
CLEAN_BUCKET = "rishi-clean-bucket"
QUARANTINE_BUCKET = "rishi-quarantine-bucket"

def lambda_handler(event, context):
    for record in event['Records']:
        # Get source info
        source_bucket = record['s3']['bucket']['name']
        # S3 replaces spaces with '+' in event keys; this fixes it
        key = record['s3']['object']['key'].replace('+', ' ')
        
        # Define local path in Lambda's temp space
        download_path = f"/tmp/{os.path.basename(key)}"
        
        print(f"Checking file: {key} from {source_bucket}")
        
        try:
            # 1. Download from Upload Bucket
            s3.download_file(source_bucket, key, download_path)
            
            # 2. Run Scan
            # ClamAV exit codes: 0 = Clean, 1 = Virus, 2 = Error
            print(f"Starting ClamAV scan for {key}...")
            scan_result = subprocess.run(
                ['clamscan', '--database=/var/lib/clamav', download_path],
                capture_output=True, 
                text=True
            )
            
            # Log the ClamAV output so you can see it in CloudWatch
            print(f"Scan Output: {scan_result.stdout}")
            
            # 3. Determine Destination
            if scan_result.returncode == 0:
                dest_bucket = CLEAN_BUCKET
                print(f"SUCCESS: {key} is clean.")
            else:
                dest_bucket = QUARANTINE_BUCKET
                print(f"WARNING: {key} is INFECTED (or scan error).")

            # 4. Move to destination bucket
            print(f"Moving {key} to {dest_bucket}...")
            s3.copy_object(
                Bucket=dest_bucket,
                Key=key,
                # Note: CopySource requires the bucket name and key
                CopySource={'Bucket': source_bucket, 'Key': key}
            )
            
            # 5. Delete from Upload bucket
            s3.delete_object(Bucket=source_bucket, Key=key)
            print(f"Task complete for {key}. Removed from {source_bucket}.")

        except Exception as e:
            print(f"Error processing {key}: {str(e)}")
            raise e
        finally:
            # Clean up /tmp to prevent storage leaks
            if os.path.exists(download_path):
                os.remove(download_path)

    return {"status": "success"}
