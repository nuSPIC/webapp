from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect

from lib.decorators import render_to

from upload.forms import UploadFileForm


def handle_uploaded_file(pk, f):
    with open('media/files/%s_%s' %(pk,f), 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

@render_to('upload.html')
@login_required
def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.user.pk, request.FILES['file'])
            return {'form': form, 'url_to_file': '/media/files/%s_%s' %(request.user.pk, request.FILES['file'])}

    else:
        form = UploadFileForm()
    return {'form': form}

