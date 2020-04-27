import boto3
from botocore.exceptions import NoCredentialsError
from config_reader import ConfigReader

def upload_to_aws(local_file, bucket, s3_file , type):
    config_reader = ConfigReader()
    configuration = config_reader.read_config()

    ACCESS_KEY = configuration['AZ_ACCESS_KEY']
    SECRET_KEY = configuration['AZ_SECRET_KEY']

    s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY,
                      aws_secret_access_key=SECRET_KEY)

    try:
        s3.upload_file(local_file, bucket, s3_file, ExtraArgs= {'ContentType':type})
        print("Upload Successful")
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False
