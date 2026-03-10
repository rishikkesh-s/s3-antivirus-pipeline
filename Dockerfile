FROM public.ecr.aws/lambda/python:3.11

# Install ClamAV
RUN yum install -y clamav clamav-update && \
    yum clean all

# Update virus definitions
RUN freshclam

# Copy your Lambda function
COPY lambda_function.py ${LAMBDA_TASK_ROOT}

CMD ["lambda_function.lambda_handler"]
