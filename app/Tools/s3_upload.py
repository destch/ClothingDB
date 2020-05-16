def upload_profile_photo():
    bucket = 'cf-simple-s3-origin-db-556603787203'
    image_file = files
    client = boto3.client('s3',
                          region_name='sfo2',
                          endpoint_url='https://example.xxx.amazonaws.com',
                          aws_access_key_id=os.environ['ACCESS_KEY'],
                          aws_secret_access_key=os.environ['SECRET_KEY'])

    filename = secure_filename(image_file.filename)  # This is convenient to validate your filename, otherwise just use file.filename

    client.put_object(Body=image_file,
                      Bucket=bucket,
                      Key=filename,
                      ContentType=content_type)
