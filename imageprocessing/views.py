from django.shortcuts import render
from django.http import JsonResponse
import boto3
from botocore.exceptions import NoCredentialsError

# Create your views here.
def upload_image(request):
    if request.method == 'POST' and request.FILES['image']:
        image = request.FILES['image']
        s3 = boto3.client('s3')
        try:
            s3.upload_fileobj(image, 'image-processing-app', image.name)
            return JsonResponse({'message': 'Image uploaded successfully'})
        except NoCredentialsError:
            return JsonResponse({'message': 'AWS credentials not available'})
    return render(request, 'upload_image.html')
    
