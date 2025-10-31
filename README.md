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
  "detail-type": ["Object Created"], # what kind of S3 event occurred
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
5.1 Choose REST API as a new API
5.2 Create resource 
5.3 Create method
5.4 We choose POST for the method
5.5 Integration type : AWS service
5.6 AWS Region need to be the same as the step function you want to POST
5.7 AWS service : Step function
5.8 HTTP method : POST
5.9 Action name : StartExecution
5.10 Execution role - Permission
5.10.1 Create a role in IAM by selecing Trusted entity type : AWS service
5.10.2 Use case : API Gateway, it will include a Permissions policies that AmazonAPIGatewayPushToCloudWatchLogs
5.10.3 After creating this role, add permissions by creating inline policy, that’s allowed to call the Step Functions API that actually starts a workflow
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowStartExecution",
            "Effect": "Allow",
            "Action": "states:StartExecution", # Allows starting a new execution of an AWS Step Functions state machine
            "Resource": "The ARN of your state machine"
        }
    ]
}
5.10.4 After finish creating the roles for API Gatway, copy the ARN of this role back to Execution role
Reference : https://docs.aws.amazon.com/step-functions/latest/dg/tutorial-api-gateway.html?utm_source=chatgpt.com
5.11 Edit Mapping templates under Integration request
Content type : application/json
Template body : 
{
  "stateMachineArn": "The ARN of your state machine",
  "input": "$util.escapeJavaScript($input.body)" # a JSON-string representing the input for that execution
}
Ensures your incoming API request is transformed into the correct JSON shape that Step Functions expects.
5.12 Deploy
The link at the POST method will be API URL that you can post to the state machine

6. CloudWatch
