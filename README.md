# Serverless Image Resize Processing

This project demonstrates a **fully automated image resize processing workflow** on **AWS** using an **event-driven architecture**.

---

## 1. Architecture

![Architecture](https://github.com/user-attachments/assets/af073e49-1ebc-4403-b59f-b840d4a94eee)

---

## 2. S3

1. Create **one bucket** for uploading original images.  
2. Create **one bucket** for storing resized images.

---

## 3. Lambda

1. Create a Lambda function for resizing images.  
2. **Runtime:** Python 3.12  
3. **Architecture:** x86_64  
4. Create a **new role** with *basic Lambda permissions* (for CloudWatch logging).  
5. `lambda_function.py` includes resizing code.  
   - Returns `{"ok": True}` or `{"ok": False}` — used in Step Function’s Choice state.  
   - Reference: [Heuristic Technopark Blog](https://heuristictechnopark.com/blog/building-serverless-image-processing-python-aws-lambda)
6. Set **Environment Variables** under Configuration:  
   - Key = variable name used in code  
   - Value = name of the target (resized image) bucket  
7. Create a **Lambda Layer** for the Pillow library.  
   - Reference: [AWS Pillow Import Issue Solution](https://repost.aws/questions/QU11QL_JaISAOSykJteHyFHg/issue-with-importing-pillow-library-for-image-processing-in-aws-lambda-environment)  
8. Add the created layer to your Lambda function (via ARN).  
9. **IAM Permissions (Identity-Based Policy):**

   ```json
   "Statement": [
     {
       "Effect": "Allow",
       "Action": [
         "s3:GetObject",
         "s3:PutObject",
         "s3:ListBucket"
       ],
       "Resource": "The ARN of the bucket"
     }
   ]

Reference: [AWS Example Policies for S3](https://docs.aws.amazon.com/AmazonS3/latest/userguide/example-policies-s3.html)

---

## 4. Step Function – Workflow Orchestration

1. Create a **State Machine**.  
2. **Query language:** JSONPath  
3. Invoke your Lambda function (resize image).  
4. Add a **Choice state** to check success/failure of resizing.

   - **Success rule**  
     - Variable: `$.ok`  
     - Operator: `is equal to`  
     - Value: Boolean constant → `true`  

   - **Fail rule**  
     - Any result where `"ok"` is not `true`.

---

## 5. EventBridge

1. Enable **notifications** on the *original image bucket*.  
2. Create a **Rule** in EventBridge.

   - **Rule type:** Event pattern  
   - **Custom JSON pattern:**
     ```json
     {
       "source": ["aws.s3"],
       "detail-type": ["Object Created"],
       "resources": ["The ARN of the original bucket"]
     }
     ```

3. **Target:**
   - Type: AWS Service  
   - Target: Step Function state machine  
   - Execution Role permissions:
     ```json
     {
       "Effect": "Allow",
       "Action": ["states:StartExecution"],
       "Resource": ["The ARN of the state machine"]
     }
     ```

4. **Input Transformer:**

   - **Input path**
     ```json
     {"bucket":"$.detail.bucket.name","key":"$.detail.object.key","size":"$.detail.object.size"}
     ```
   - **Template**
     ```json
     {
       "bucket": <bucket>,
       "key": <key>,
       "size": <size>
     }
     ```

---

## 6. API Gateway

1. Choose **REST API** → Create new API.  
2. Create a **Resource**.  
3. Create a **Method** → Choose **POST**.  
4. **Integration type:** AWS Service  
5. **AWS Region:** Must match your Step Function region.  
6. **AWS Service:** Step Functions  
7. **HTTP method:** POST  
8. **Action name:** StartExecution  
9. **Execution Role** – Permissions
   1. Create a role with **trusted entity type:** AWS Service  
   2. **Use case:** API Gateway  
   3. This automatically includes `AmazonAPIGatewayPushToCloudWatchLogs`.  
   4. Add inline policy for Step Functions:

   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Sid": "AllowStartExecution",
         "Effect": "Allow",
         "Action": "states:StartExecution",
         "Resource": "The ARN of your state machine"
       }
     ]
   }
Reference: [AWS Step Functions API Gateway Tutorial](https://docs.aws.amazon.com/step-functions/latest/dg/tutorial-api-gateway.html?utm_source=chatgpt.com)

---

10. **Mapping Templates**

- **Content type:** `application/json`  
- **Template body:**

  ```json
  {
    "stateMachineArn": "The ARN of your state machine",
    "input": "$util.escapeJavaScript($input.body)"
  }
Ensures your incoming API request is transformed into the correct JSON shape that Step Functions expects.

---

11. **Deploy and Workflow**
   - The user sends a POST request to API Gateway.  
   - API Gateway invokes Step Functions via `StartExecution`.  
   - Step Functions runs the Lambda function `s3-trigger-resized-images`.  
   - *Note:* Current API accepts **JSON**, not image files.  
   - Lambda fetches the image from S3, resizes it, and uploads it to the target bucket.  
   - Step Functions returns an execution ARN and success response.

---

## 7. CloudWatch

Because Lambda uses a role with **basic permissions**, logs are automatically available in **CloudWatch**.  
Use it to verify errors or monitor workflow execution.

---

## 8. How to Run

### 8.1 API → Step Function

1. Use **Postman** or similar tool.  
2. **API URL:**  
https://tibg7nysfk.execute-api.ca-central-1.amazonaws.com/Resize_Image_API/resize
3. **Body (JSON):**
    ```json
    {
      "bucket": "lambda-trigger-bucket-original-images",
      "key": "b.jpg",
      "size": 1000
    }
4. **Expected Response:**
   ```json
   {
     "executionArn": " ",
     "startDate": " "
   }
5. **Expected result**
   <img width="1719" height="614" alt="image" src="https://github.com/user-attachments/assets/15acb929-9411-4c2b-975d-ecaf1bf92eff" />

### 8.2 Step Function → Lambda

1. Start a new execution.  
2. **Input:**
   ```json
   {
     "bucket": "lambda-trigger-bucket-original-images",
     "key": "b.jpg",
     "size": 1000
   }
3. **State output**
    ```json
   {
     "ok": true,
      "destBucket": "lambda-trigger-bucket-resized-images",
      "destKey": "output/b_resized.jpg",
      "statusCode": 200,
      "body": "Resized image uploaded to s3://lambda-trigger-bucket-resized-images/output/b_resized.jpg"
   }
4. **Graph view**
   
      <img width="652" height="466" alt="image" src="https://github.com/user-attachments/assets/3686440d-7405-4089-baf3-0cb2205cce6a" />

### 8.3 S3 → EventBridge → Step Function

1. Upload an image to the **original bucket**.  
2. **Expected Result:** A resized image appears in the **resized bucket**.  
3. **CloudWatch Example:**  
   ![CloudWatch Logs](https://github.com/user-attachments/assets/82f6108f-dadf-430d-9e20-719ec2524bb5)




        
