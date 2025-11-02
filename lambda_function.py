# The code downloads the image from S3 using boto3 (the AWS SDK for Python).
# It opens the image using the Pillow library.
# It resizes the image to a new width (adjust the new_width variable as needed). The height is calculated to maintain the aspect ratio.
# It saves the resized image to a BytesIO object (in memory).
# It uploads the resized image back to S3 to the output folder.

import boto3
from io import BytesIO
from PIL import Image
import os

s3 = boto3.client('s3')

def lambda_handler(event, context):
    print("EVENT:", event)
    # Accept either direct payload ({bucket,key,size}) or S3 event format
    bucket = event.get('bucket')
    key    = event.get('key')
    size   = event.get('size')
    if (not bucket or not key) and isinstance(event, dict) and 'Records' in event:
        try:
            rec = event['Records'][0]
            bucket = rec['s3']['bucket']['name']
            key = rec['s3']['object']['key']
            size = rec['s3']['object']['size']
        except Exception as e:
            return {"ok": False, "error": f"Could not parse S3 event payload: {e}"}
    if not bucket or not key:
        return {"ok": False, "error": "Could not parse S3 event payload"}

    print(f"Triggered by: s3://{bucket}/{key}(size={size})")
    try:
        # Download the image from S3
        response = s3.get_object(Bucket=bucket, Key=key)
        image_data = response['Body'].read()
        print("Image downloaded successfully")
        
        # Open the image using Pillow
        image = Image.open(BytesIO(image_data))
        print(f"Original size: {image.size}")
        
        # Resize the image
        new_width  = 500
        new_height = int(image.size[1] * (new_width / image.size[0]))
        image = image.resize((new_width, new_height))
        print(f"Resized to: {image.size}")

        # Save the resized image to a BytesIO object
        output_stream = BytesIO() # create an in-memory binary stream
        image.convert('RGB').save(output_stream, format="JPEG") # write the Pillow image into it
        output_stream.seek(0) # rewind the data

        # Upload to the DESTINATION (resized) bucket
        dest_bucket = os.environ.get('RESIZED_BUCKET') # set the target value at environment variable
        print("ENV RESIZED_BUCKET =", dest_bucket)
        if not dest_bucket:
            raise RuntimeError("RESIZED_BUCKET env var is not set")
        output_key = f"output/{os.path.splitext(os.path.basename(key))[0]}_resized.jpg"
        s3.put_object(
            Bucket=dest_bucket,
            Key=output_key,
            Body=output_stream,
            ContentType='image/jpeg'
        )
        print(f"Resized image uploaded to s3://{dest_bucket}/{output_key}")

        return {
            "ok": True, #output for success status in step function
            "destBucket": dest_bucket,
            "destKey": output_key,
            'statusCode': 200,
            'body': f"Resized image uploaded to s3://{dest_bucket}/{output_key}"
        }

    except Exception as e:
        print("ERROR during processing:", repr(e))
        return {"ok": False, "error": str(e)}
