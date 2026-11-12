from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.login_view, name='home'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('upload/', views.upload_details, name='upload_details'),
    path('history/', views.history, name='history'),
    path('delete/<int:record_id>/', views.delete_record, name='delete_record'),
    path('download_report/', views.download_report, name='download_report'),
]