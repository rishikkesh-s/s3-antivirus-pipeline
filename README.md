# s3-antivirus-pipeline
A serverless, event-driven malware scanning pipeline for Amazon S3 using AWS Lambda, Docker, and ClamAV.
----------------------------------------------------------------------------------------------------------------------------------------------------------------------
The Problem & Solution
The Challenge: Users can upload malicious files to public S3 buckets, potentially infecting downstream users or internal systems.
The Solution: A serverless "security gate." As soon as a file hits the Upload Bucket, an S3 Event triggers a Lambda function. The function pulls a fresh ClamAV database, scans the file in memory, and moves it to either a Clean or Quarantine bucket based on the result.
----------------------------------------------------------------------------------------------------------------------------------------------------------------------
Architecture
Storage: Amazon S3 (Upload, Clean, and Quarantine buckets)

Compute: AWS Lambda (Container Image)

Security Engine: ClamAV (Open Source Antivirus)

Logging: AWS CloudWatch

Deployment: Docker + ECR
----------------------------------------------------------------------------------------------------------------------------------------------------------------------
Implementation Details
1. The Trigger
The pipeline is automated using S3 Event Notifications. Any ObjectCreated event in the upload bucket instantly wakes up the Lambda scanner.

2. The Scanner Engine (Docker)
Because ClamAV requires specific Linux libraries and large virus definition files, I packaged the scanner into a Docker Container and deployed it to AWS ECR. This bypasses the 50MB Lambda layer limit and ensures a consistent environment.
-------------------------------------------------------------------------------------------------------------------------------------------------------------------
Testing & Results
To test the system, I uploaded two files: testfile.txt (Clean) and Virus.txt (a simulated malware file).

Step 1: Uploading Files
Both files were uploaded simultaneously to the landing bucket.

Step 2: Automated Sorting
The Lambda function processed both files in seconds. As seen below, the files were correctly identified and separated.
-------------------------------------------------------------------------------------------------------------------------------------------------------------------
Monitoring & Logs
Full observability is maintained through AWS CloudWatch. Every scan is logged, allowing for auditing and troubleshooting of the scanning engine.
-------------------------------------------------------------------------------------------------------------------------------------------------------------------
Skills Demonstrated
Cloud Security: Implementation of the "Quarantine Pattern."

Serverless Architecture: Event-driven computing with AWS Lambda.

Containerization: Packaging complex software with Docker for Cloud deployment.

IAM & Permissions: Managing Least Privilege access for S3 and CloudWatch.
-------------------------------------------------------------------------------------------------------------------------------------------------------------------
How to use this
Clone the repository.

Build the Docker image: docker build -t clamav-lambda .

Push to AWS ECR.

Configure S3 buckets with the provided Lambda trigger permissions.
-------------------------------------------------------------------------------------------------------------------------------------------------------------------
