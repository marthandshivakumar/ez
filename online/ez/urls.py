from django.urls import path
from .views import *

urlpatterns = [
    path('login/', UserLoginView.as_view(), name='user_login'),
    path('upload/', OpsUserUploadView.as_view(), name='ops_user_upload'),
    path('signup/', ClientUserSignupView.as_view(), name='client_user_signup'),
    path('verify-email/', ClientUserEmailVerifyView.as_view(), name='client_user_email_verify'),
    path('download-file/<int:file_id>/', ClientUserDownloadFileView.as_view(), name='client_user_download_file'),
    path('list-files/', ClientUserListFilesView.as_view(), name='client_user_list_files'),
    path('download-file/<int:file_id>/<str:username>/', ClientUserSecureDownloadView.as_view(), name='client_user_secure_download'),
]
