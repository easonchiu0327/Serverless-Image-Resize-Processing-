# Serverless-Image-Resize-Processing

This project demonstrates a **fully automated image resize processing workflow** on AWS using an **event-driven architecture**.

1. S3
1.1 Create 1 bucket for uploading original image.
1.2 Create 1 bucket for output the reaized image.
2. Lambda
2.1 Create a function for resizing the image
2.2 Runtime : Python 3.12
2.3 Architecture : x86_64
2.4 Create a new role with basic Lanbda permissions
2.5 lambda_function.py include the resizing code
Reference from : https://heuristictechnopark.com/blog/building-serverless-image-processing-python-aws-lambda
2.6 Set key(variable string in code) and the value(name of the target bucket) at Environment under Configuration, point the resized imagep to the target bucket.
2.7 Create a layer for Pillow library, follow the instruction from : https://repost.aws/questions/QU11QL_JaISAOSykJteHyFHg/issue-with-importing-pillow-library-for-image-processing-in-aws-lambda-environment
2.8 Add the layer for the function specify with an ARN.
2.9 Identity-based policy-Permission
2.9.1 Support the read → process → write workflow for image resizing.
"Statement":[
    "Effect":"Allow",
    "Action":[
            "s3:GetObject", # Read/download/fetch the file
            "s3:PutObject", # Write/Process/upload the file
            "s3:ListBucket" # See what files exist
         ],
    "Resource":"The ARN of the bucket"
]
Reference : https://docs.aws.amazon.com/AmazonS3/latest/userguide/example-policies-s3.html
4. Step function
4.1 State machine
6. EventBridge
7. API Getway
5. CloudWatch

## 📘 AWS Docs Reference

- [Tutorial: Using AWS Lambda with Step Functions](https://docs.aws.amazon.com/step-functions/latest/dg/tutorial-lambda.html)
- [Choice State in AWS Step Functions](https://docs.aws.amazon.com/step-functions/latest/dg/awl-choice-state.html)
- [EventBridge Rule for S3 Object Created Events](https://docs.aws.amazon.com/AmazonS3/latest/userguide/ev-events.html)
- [Using Amazon EventBridge with Amazon S3](https://docs.aws.amazon.com/AmazonS3/latest/userguide/EventBridge.html)