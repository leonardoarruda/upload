from django.shortcuts import render, redirect
from django.conf import settings
from django.core.files.storage import FileSystemStorage

from uploads.core.models import Document
from uploads.core.forms import DocumentForm
from google.cloud import storage

def home(request):
    """List files"""
    blobs = list_blobs('upload_files_leonardo')
    return render(request, 'core/home.html', {
        'blobs': blobs
    })

def remove(request):
    """Confirm delete file"""
    delete_file(request.GET['filename'])
    return render(request, 'core/remove.html')

def add(request):
    """Download data to a server"""
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        filepath = './media/{}'.format(filename)
        uploaded_file_url = upload_to_bucket(filename, filepath, 'upload_files_leonardo')
        return render(request, 'core/add.html', {
            'uploaded_file_url': uploaded_file_url
        })
    return render(request, 'core/add.html')

#### GOOGLE CLOUD ####
def delete_file(filename):
    """Removes file from bucket"""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket('upload_files_leonardo')
    blob = bucket.blob(filename)

    blob.delete()

def list_blobs(bucket_name):
    """Lists all the blobs in the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)

    return bucket.list_blobs()

def upload_to_bucket(blob_name, path_to_file, bucket_name):
    """Upload data to a bucket"""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)

    blob = bucket.blob(blob_name)
    blob.upload_from_filename(path_to_file)

    #returns a public url
    return blob.public_url