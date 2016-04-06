import json
import os
from urllib2 import HTTPError

import requests
from django.db import IntegrityError
from django.http import JsonResponse
from rest_framework.authtoken import views as rest_views

from brca import settings
from .models import MyUser


def token_auth(request):
    response = rest_views.obtain_auth_token(request)
    response["Access-Control-Allow-Origin"] = "*"
    return response


def register(request):
    image = None
    if request.FILES:
        image = request.FILES["image"]

    email = request.POST.get('email', '')
    password = request.POST.get('password', '')

    first_name = request.POST.get('firstName', '')
    last_name = request.POST.get('lastName', '')
    title = request.POST.get('title', '')
    affiliation = request.POST.get('affiliation', '')
    institution = request.POST.get('institution', '')
    city = request.POST.get('city', '')
    state = request.POST.get('state', '')
    country = request.POST.get('country', '')
    phone_number = request.POST.get('phoneNumber', '')
    comment = request.POST.get('comment', '')
    include_me = request.POST.get('includeMe', True)
    hide_number = request.POST.get('hideNumber', True)
    hide_email = request.POST.get('hideEmail', True)
    captcha = request.POST.get('captcha')

    response = {'success': True}

    # Check the CAPTCHA
    try:
        post_data = {'secret': settings.CAPTCHA_SECRET,
                     'response': captcha}
        response = requests.post('https://www.google.com/recaptcha/api/siteverify', data=post_data)
        content = json.loads(response.content)
        response = {'success': content['success']}
    except HTTPError:
        response = {'success': False}

    # Create the user
    try:
        created_user = MyUser.objects.create_user(email, password, first_name, last_name, title, affiliation,
                                                  institution, city, state, comment, country, phone_number, include_me,
                                                  hide_number, hide_email)
        # Save the image under the user's id
        if image is not None:
            save_picture(created_user.id, image)

    except IntegrityError:
        response = {'success': False}

    response = JsonResponse(response)
    response["Access-Control-Allow-Origin"] = "*"
    return response


def save_picture(filename, image):
    path = os.path.join(settings.MEDIA_ROOT, str(filename))
    fd = open(path, 'wb')
    for chunk in image.chunks():
        fd.write(chunk)
    fd.close()


def users(request):
    page_num = int(request.GET.get('page_num', '0'))
    page_size = int(request.GET.get('page_size', '0'))

    start = page_num * page_size
    end = start + page_size

    page = MyUser.objects.all()[start:end]

    response = JsonResponse({'data': list(page.values())})
    response["Access-Control-Allow-Origin"] = "*"

    return response
