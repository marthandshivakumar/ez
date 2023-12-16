from django.shortcuts import render
from .models import UserProfile ,UploadFile
import json
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.views import View
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils .decorators import method_decorator
import hashlib
import uuid
from django.core.exceptions import PermissionDenied
from django.http import FileResponse
from django.views import View
import mimetypes
import os
from django.views.decorators.csrf import csrf_exempt
# Create your views here.

@method_decorator(csrf_exempt, name='dispatch')
class UserLoginView(View):
    def post(self, request):
        data = json.loads(request.body.decode('utf-8'))
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return JsonResponse({'message': 'Login successful'}, status=200)
            else:
                return JsonResponse({'message': 'Invalid credentials'}, status=401)
        else:
            return JsonResponse({'message': 'Username and password are required'}, status=400)

    def get(self, request):
        return JsonResponse({'message': 'This is the login page. Use POST to log in.'})
    
@method_decorator(csrf_exempt, name='dispatch')
class OpsUserUploadView(View):
    @method_decorator(login_required)
    def post(self, request):
        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            print(f"UserProfile does not exist for user: {request.user}")
            return JsonResponse({'message': 'UserProfile does not exist'}, status=500)

        if request.user.is_authenticated and user_profile.is_ops_user:
            uploaded_file = request.FILES.get('file')

            if uploaded_file:
                allowed_file_types = ['pptx', 'docx', 'xlsx']
                file_extension = uploaded_file.name.split('.')[-1].lower()

                if file_extension in allowed_file_types:
                    UploadFile.objects.create(user=request.user, file=uploaded_file, file_type=file_extension)
                    return JsonResponse({'message': 'File uploaded successfully'}, status=200)
                else:
                    return JsonResponse({'message': 'Invalid file type'}, status=400)
            else:
                return JsonResponse({'message': 'No file provided'}, status=400)
        else:
            return JsonResponse({'message': 'Unauthorized or not an ops user'}, status=401)


@method_decorator(csrf_exempt, name='dispatch')
class ClientUserSignupView(View):
    def post(self, request):
        # Handle form data
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')

        if username and password and email:
            if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
                return JsonResponse({'message': 'Username or email already taken'}, status=400)

            user = User.objects.create_user(username=username, password=password, email=email)


            return JsonResponse({'message': 'Signup successful'}, status=200)
        else:
            return JsonResponse({'message': 'Username, password, and email are required'}, status=400)

    def get(self, request):
        return render(request, 'signup.html')
        


@method_decorator(csrf_exempt, name='dispatch')
class ClientUserEmailVerifyView(View):
    def post(self, request):
        data = json.loads(request.body.decode('utf-8'))

        username = data.get('username')
        verification_code = data.get('verification_code')

        if username and verification_code:
            user = User.objects.get(username=username)
            user_profile = UserProfile.objects.get(user=user)

            if user_profile.url == verification_code:
                user_profile.email_verified = True
                user_profile.save()

                return JsonResponse({'message': 'Email verification successful'}, status=200)
            else:
                return JsonResponse({'message': 'Invalid verification code'}, status=400)
        else:
            return JsonResponse({'message': 'Username and verification code are required'}, status=400)
      
        
@method_decorator(csrf_exempt, name='dispatch')
class ClientUserDownloadFileView(View):
    def get(self, request, file_id):
        client_user = request.user

        if not client_user.is_authenticated:
            raise PermissionDenied
        uploaded_file = get_object_or_404(UploadFile, id=file_id, user=request.user)

        allowed_file_types = ['pptx', 'docx', 'xlsx']
        if uploaded_file.File_type not in allowed_file_types:
            raise PermissionDenied

        download_link = f"/download-file/{file_id}/{client_user.username}/"

        return JsonResponse({'download_link': download_link, 'message': 'success'}, status=200)

@method_decorator(csrf_exempt, name='dispatch')
class ClientUserListFilesView(View):
    def get(self, request):
        client_user = request.user

        if not client_user.is_authenticated:
            raise PermissionDenied

        uploaded_files = UploadFile.objects.filter(user=request.user)

        files_data = [
            {
                'file_id': file.id,
                'file_name': os.path.basename(file.File.name),
                'file_type': file.File_type,
            }
            for file in uploaded_files
        ]

        return JsonResponse({'files': files_data, 'message': 'success'}, status=200)

@method_decorator(csrf_exempt, name='dispatch')
class ClientUserSecureDownloadView(View):
    def get(self, request, file_id, username):
        client_user = request.user

        if not client_user.is_authenticated or client_user.username != username:
            raise PermissionDenied

        uploaded_file = get_object_or_404(UploadFile, id=file_id, user=request.user)

        allowed_file_types = ['pptx', 'docx', 'xlsx']
        if uploaded_file.File_type not in allowed_file_types:
            raise PermissionDenied

        file_path = uploaded_file.File.path
        content_type, _ = mimetypes.guess_type(file_path)
        response = FileResponse(open(file_path, 'rb'), content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'

        return response