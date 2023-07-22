from django.urls import path
from . import views
urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('quizzes/', views.QuizListCreateView.as_view(), name='quiz-list-create'),
    path('quizzes/<int:pk>/', views.QuizRetrieveUpdateDeleteView.as_view(), name='quiz-retrieve-update-delete'),
    path('quizattempts/', views.QuizAttemptListView.as_view(), name='quiz-attempt-list'),
    path('quizattempts/<int:pk>/', views.QuizAttemptCreateView.as_view(), name='quiz-attempt-detail'),
    path('results/<int:pk>/', views.ResultView.as_view(), name='quiz-attempt-result'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('users/', views.UserListView.as_view(), name='user-list'),
    path('users/', views.UserListView.as_view(), name='user-list'),  
    path('users/create/', views.UserListCreateView.as_view(), name='user-create'),
    path('users/<int:pk>/', views.UserRetrieveUpdateDestroyView.as_view(), name='user-detail'),
    path('analytics/', views.CombinedStatisticsAPIView.as_view(), name='combined-statistics'),

]
