from django.shortcuts import render
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.core.files.storage import default_storage
import boto3
from PIL import Image, ImageOps, ImageFilter, UnidentifiedImageError
from botocore.exceptions import NoCredentialsError, ClientError

# Create your views here.
def upload_image(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST' and "image" in request.FILES and 'filter' in request.POST:
        try:
            image = Image.open(request.FILES["image"])

            filter_name = request.POST.get('filter')

            if filter_name == 'grayscale':
                grayscale_image = ImageOps.grayscale(image)
                processed_image_path = f'grayscale-{request.FILES["image"].name}'
                grayscale_image.save(processed_image_path)
            elif filter_name == 'sepia':
                sepia_image = sepia(image)
                processed_image_path = f'sepia-{request.FILES["image"].name}'
                sepia_image.save(processed_image_path)
            elif filter_name == 'poster':
                poster_image = ImageOps.posterize(image, 4)
                processed_image_path = f'poster-{request.FILES["image"].name}'
                poster_image.save(processed_image_path)
            elif filter_name == 'edge':
                edge_image = image.filter(ImageFilter.FIND_EDGES)
                processed_image_path = f'edge-{request.FILES["image"].name}'
                edge_image.save(processed_image_path)
            elif filter_name == 'blur':
                blur_image = image.filter(ImageFilter.BLUR)
                processed_image_path = f'blur-{request.FILES["image"].name}'
                blur_image.save(processed_image_path)
            elif filter_name == 'solar':
                solar_image = ImageOps.solarize(image, threshold=128)
                processed_image_path = f'solar-{request.FILES["image"].name}'
                solar_image.save(processed_image_path)                

            with open(processed_image_path, 'rb') as s3_file:
                s3_path = f'processed/{processed_image_path}'
                s3 = boto3.client('s3')

                try:
                    bucket_name = 'image-processing-app'
                    location = 'us-east-2'

                    s3.upload_fileobj(s3_file, bucket_name, s3_path)
                    default_storage.delete(processed_image_path)

                    return render(request, 'upload_image.html', {
                        's3_path': f"https://{bucket_name}.s3.{location}.amazonaws.com/{s3_path}",
                        'filter': filter_name.capitalize()
                    })
                except NoCredentialsError as e:
                    return JsonResponse({'message': f'{e}'}, status=500)
                except ClientError as e:
                    return JsonResponse({'message': f'{e}'}, status=500)
        except UnidentifiedImageError as e:
            return JsonResponse({'message': f'{e}'}, status=400)
            
    return render(request, 'upload_image.html')

def sepia(image):
    width, height = image.size
    for x in range(width):
        for y in range(height):
            r, g, b = image.getpixel((x, y))
            tr = int(0.393 * r + 0.769 * g + 0.189 * b)
            tg = int(0.349 * r + 0.686 * g + 0.168 * b)
            tb = int(0.272 * r + 0.534 * g + 0.131 * b)
            image.putpixel((x, y), (tr, tg, tb))
    return image
