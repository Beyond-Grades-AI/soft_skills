# web/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_screen, name='login_screen'),
    path('login_screen/', views.login_screen, name='login_screen'),
    path('main_screen/', views.main_screen, name='main_screen'),
    path('tests_screen/', views.tests_screen, name='tests_screen'),
    path('teacher_screen/', views.create_questions, name='create_questions'),
    path('generate_link/', views.generate_link, name='generate_link'),  
    path('test_page/<int:test_id>/', views.test_page, name='test_page'),
    path('submit_answers/', views.submit_answers, name='submit_answers'),
    path('submitted/', views.submitted, name='submitted'),
    path('tests_screen/', views.tests_screen, name='tests_screen'),
    path('review_test/<int:test_id>/<str:first_name>', views.review_test, name='review_test'),
    path('failure_url/', views.failure_url, name='failure_url'),
]