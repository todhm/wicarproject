import os
from PIL import Image as  PilImage
from resizeimage import resizeimage
from wand.image import Image
from utilities.timeutil import timestamp as now
from flask import current_app as app
from flask import request
from io import BytesIO
import requests
import boto3
from boto3.s3.transfer import S3Transfer
import os.path



def modify_image(image, format):
    pil_image = Image.open(image)

    # Prints out (1280, 960)
    print(pil_image.size)

    in_mem_file = io.BytesIO()

    # format here would be something like "JPEG". See below link for more info.
    pil_image.save(in_mem_file, format="JPEG")
    return in_mem_file.getvalue()

def save_image(f,car_id,image_location='UPLOADED_FOLDER',image_width=640,image_height=320):
    image_id= now()
    image_id = int(image_id)
    filename_template =  '{}.{}.jpg'.format(car_id,image_id)
    AWS_BUCKET= app.config['AWS_BUCKET']
    try:
        with PilImage.open(f) as image:
            image.format='JPEG'
            UPLOADED_FOLDER=app.config[image_location]
            img_path = "."+os.path.join(UPLOADED_FOLDER,filename_template)
            if image.width < image_width or image.height < image_height:
                request._tracking_data = {
                      'car_id':car_id,
                     'action':"image_add_fail",
                     'message':"size does not match"
                     }
                return None
            image = image.resize((int(image.width*0.5),int(image.height*0.5)),PilImage.LANCZOS)
            try:
                image = image.convert("RGB")
                image.save(img_path, image.format,quality=95)
                if AWS_BUCKET:
                    s3 = boto3.client('s3',
                        region_name=app.config['S3_REGION_NAME'],
                        aws_access_key_id=app.config['AWS_ACCESS_KEY_ID'],
                        aws_secret_access_key=app.config['AWS_SECRET_ACCESS_KEY']
                        )
                    transfer = S3Transfer(s3)
                    transfer.upload_file(
                        img_path,
                        AWS_BUCKET,
                        os.path.join(UPLOADED_FOLDER,filename_template)[1:],
                        extra_args={'ACL': 'public-read', 'ContentType': 'image/jpeg'}
                        )
                    os.remove(img_path)
                return image_id
            except Exception as e:
                request._tracking_data = {
                     'car_id':car_id,
                     'action':"image_add_fail",
                     'message':str(e)
                     }
                return None
    except Exception as e:
        request._tracking_data = {
             'car_id':car_id,
             'action':"image_add_fail",
             'message':str(e)
             }
        return None


def save_user_profile(profile,user_id):
    image_id= now()
    image_id = int(image_id)
    filename_template =  '{}.{}.raw.png'.format(user_id,image_id)
    response = requests.get(profile)
    f = BytesIO(response.content)
    AWS_BUCKET  = app.config['AWS_BUCKET']
    with PilImage.open(f) as image:
        #crop_center(image)
        image.format='png'
        if image.height >= 50 and image.width >= 50:
            try:
                cover = image
                USER_IMAGE_FOLDER=app.config['USER_IMAGE_FOLDER']
                file_path = "."+os.path.join(USER_IMAGE_FOLDER,filename_template)
                cover.save(file_path, image.format)
                if AWS_BUCKET:
                    s3 = boto3.client('s3',
                        region_name=app.config['S3_REGION_NAME'],
                        aws_access_key_id=app.config['AWS_ACCESS_KEY_ID'],
                        aws_secret_access_key=app.config['AWS_SECRET_ACCESS_KEY']
                        )
                    transfer = S3Transfer(s3)
                    transfer.upload_file(
                        file_path,
                        AWS_BUCKET,
                        os.path.join(USER_IMAGE_FOLDER,filename_template)[1:],
                        extra_args={'ACL': 'public-read', 'ContentType': 'image/png'}
                        )
                    os.remove(file_path)
                return image_id
            except Exception as e:
                request._tracking_data = {
                     'action':"image_add_fail",
                     'user_id':user_id,
                     'message':str(e)
                     }
                return None
        else:
            return None

def thumbnail_process(file,sizes=[("sm",50),("lg",75),("xlg",200)]):
    image_id = now()
    filename_template =  '.%s.%s.png'
    UPLOADED_FOLDER=app.config['UPLOADED_FOLDER']

    with Image(filename=file) as img:
        crop_center(img)
        img.format = 'png'
        img.save(filename=os.path.join(UPLOADED_FOLDER,filename_template %(image_id,'raw')))
    os.remove(file)
    return image_id

def crop_center(image):
    dst_landscape = 1> image.width /image.height
    wh = image.width if dst_landscape else image.height
    image.crop(
        left = int((image.width -wh)/2),
        top = int((image.height -wh)/2),
        width = int(wh),
        height= int(wh)
    )

def check_file_exists(filename_template,UPLOADED_FOLDER,AWS_BUCKET):
    if AWS_BUCKET:
        s3 = boto3.resource('s3',
            region_name=app.config['S3_REGION_NAME'],
            aws_access_key_id=app.config['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=app.config['AWS_SECRET_ACCESS_KEY']
            )

        bucket = s3.Bucket(AWS_BUCKET)
        key =os.path.join(UPLOADED_FOLDER,filename_template)[1:]
        objs = list(bucket.objects.filter(Prefix=key))
        if len(objs) > 0 and objs[0].key == key:
            return True
        else:
            return False

    else:
        img_path = "."+os.path.join(UPLOADED_FOLDER,filename_template)
        return os.path.isfile(img_path)


def check_img_exists(filename_template,folder_loc='UPLOADED_FOLDER'):
    AWS_BUCKET  = app.config['AWS_BUCKET']
    UPLOADED_FOLDER=app.config[folder_loc]
    if AWS_BUCKET:
        s3 = boto3.resource('s3',
            region_name=app.config['S3_REGION_NAME'],
            aws_access_key_id=app.config['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=app.config['AWS_SECRET_ACCESS_KEY']
            )

        bucket = s3.Bucket(AWS_BUCKET)
        key =os.path.join(UPLOADED_FOLDER,filename_template)[1:]
        objs = list(bucket.objects.filter(Prefix=key))
        if len(objs) > 0 and objs[0].key == key:
            return True
        else:
            return False

    else:
        img_path = "."+os.path.join(UPLOADED_FOLDER,filename_template)
        return os.path.isfile(img_path)


def check_bookingimg_exists(bookingImage,folder_loc='UPLOADED_FOLDER'):
    AWS_BUCKET  = app.config['AWS_BUCKET']
    UPLOADED_FOLDER=app.config[folder_loc]
    filename_template =  bookingImage.filename
    check_file_exists(filename_template,UPLOADED_FOLDER,AWS_BUCKET)
