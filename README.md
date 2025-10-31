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
2.5 lambda_function.py include the resizing code. 
*The return of true and false will be the the output for choice under state machine.
return{"ok": True};return{"ok": False}
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

3. Step function - Orchestrates the workflow
3.1 Create a State machine
3.2 Query language : JSONPath
3.3 Invoke a lambda function, pick the created lambda function (resize image)
3.4 A choice state after lambda that checks if the image resizing was successful, success and fail state. 
3.4.1 Rule for Success state
The return of "ok" from lambda_function.py
Variable : $.ok
Operator : is equal to
Value : Bollean constant --> true
3.4.2 Rule for Fail state
The retuns of "ok" are not true will be fail state.

4. EventBridge
4.1 Set the notification
Set the notification "on" at Amazon EventBridge at properties under oringinal image bucket.
4.2 Create rule under Amazon EventBridge
4.2.1 Rule type : event pattern
4.2.2 Custom pattern JSJON editor # When an object is uploaded to this bucket, capture that event.
{
  "source": ["aws.s3"],
  "detail-type": ["Object Created"],
  "resources": ["The ARN of the original bucket"]
}
4.2.3 Target
Type : AWS service
Target : Step function state machine
State machine : The one you create to Orchestrates the image resize workflow
Execution role : Create a new role for this specific resource
"Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "states:StartExecution" # Allows starting a new execution of an AWS Step Functions state machine
            ],
            "Resource": [
                "The ARN of the state machine"
            ]
        }
]
Configure target input : Input transformer
Input path # Will be the expected input JSON either from bucket or API
{"bucket":"$.detail.bucket.name","key":"$.detail.object.key","size":"$.detail.object.size"}
Template
{
  "bucket": <bucket>,
  "key": <key>,
  "size": <size>
}
5. API Getway
6. CloudWatch

## 📘 AWS Docs Reference

- [Tutorial: Using AWS Lambda with Step Functions](https://docs.aws.amazon.com/step-functions/latest/dg/tutorial-lambda.html)
- [Choice State in AWS Step Functions](https://docs.aws.amazon.com/step-functions/latest/dg/awl-choice-state.html)
- [EventBridge Rule for S3 Object Created Events](https://docs.aws.amazon.com/AmazonS3/latest/userguide/ev-events.html)
- [Using Amazon EventBridge with Amazon S3](https://docs.aws.amazon.com/AmazonS3/latest/userguide/EventBridge.html)