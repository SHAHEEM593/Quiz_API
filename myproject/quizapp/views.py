from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.contrib.auth import authenticate, login
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Quiz, QuizAttempt, User,SelectedChoice,Question
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.generics import ListAPIView
from rest_framework import serializers
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView,ListAPIView,RetrieveAPIView
from django.core.exceptions import ObjectDoesNotExist
from .serializers import QuizViewSerializer
from .filters import QuizFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg, Max, Min, Count
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    QuizSerializer,
    QuizAttemptSerializer,
    QuizAnalyticsSerializer,
    QuizPerformanceMetricsSerializer,
    QuestionStatisticsSerializer,
    QuizAttemptResultSerializer,
    UserProfileSerializer,
    CombinedStatisticsSerializer,
)

class UserListView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [IsAdminUser]

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        return Response('created', status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        return serializer.save()


class LoginView(generics.CreateAPIView):
    serializer_class = UserLoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            refresh = RefreshToken.for_user(user)
            return Response({'refresh': str(refresh), 'access': str(refresh.access_token)}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class QuizListCreateView(generics.ListCreateAPIView):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [permissions.IsAuthenticated]

class QuizListView(generics.ListAPIView):
    queryset = Quiz.objects.all()
    serializer_class = QuizViewSerializer
    filterset_class = QuizFilter
    filter_backends = [DjangoFilterBackend]
    permission_classes = [permissions.IsAuthenticated]
    


class QuizRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [permissions.IsAuthenticated]


class QuizAttemptCreateView(generics.CreateAPIView):
    serializer_class = QuizAttemptSerializer
    permission_classes = [permissions.IsAuthenticated]

class QuizAttemptListView(generics.ListAPIView):
    serializer_class = QuizAttemptSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return QuizAttempt.objects.filter(user=self.request.user)

class QuizAttemptListView(generics.ListAPIView):
    serializer_class = QuizAttemptSerializer
    permission_classes = [permissions.IsAuthenticated]


    def get_queryset(self):
        return QuizAttempt.objects.filter(user=self.request.user)

class QuizOverviewAPIView(generics.ListAPIView):
    serializer_class = QuizAnalyticsSerializer
    permission_classes = [permissions.IsAuthenticated]


    def get_queryset(self):
        total_quizzes = Quiz.objects.count()
        total_quiz_takers = QuizAttempt.objects.values('user').distinct().count()
        average_quiz_score = QuizAttempt.objects.aggregate(Avg('score'))['score__avg']

        return {
            'total_quizzes': total_quizzes,
            'total_quiz_takers': total_quiz_takers,
            'average_quiz_score': average_quiz_score,
        }

class QuizPerformanceMetricsAPIView(generics.ListAPIView):
    serializer_class = QuizPerformanceMetricsSerializer
    permission_classes = [permissions.IsAuthenticated]


    def get_queryset(self):
        return Quiz.objects.annotate(
            average_score=Avg('quizattempt__score'),
            highest_score=Max('quizattempt__score'),
            lowest_score=Min('quizattempt__score'),
        )

class QuestionStatisticsAPIView(generics.ListAPIView):
    serializer_class = QuestionStatisticsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Question.objects.annotate(total_answers=Count('choices__selectedchoice')).order_by('-total_answers')

class UserProfileView(generics.RetrieveAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

class ResultView(generics.RetrieveAPIView):
    queryset = QuizAttempt.objects.all()
    serializer_class = QuizAttemptResultSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)
class UserListView(ListAPIView):
    queryset = User.objects.all()
    serializer_class =   UserRegistrationSerializer
    permission_classes = [IsAdminUser] 

class UserListCreateView(ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class =   UserRegistrationSerializer
    permission_classes = [IsAdminUser]  

class UserRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class =   UserRegistrationSerializer
    permission_classes = [IsAdminUser]

class CombinedStatisticsAPIView(generics.ListAPIView):
    serializer_class = CombinedStatisticsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        total_quizzes = Quiz.objects.count()
        total_quiz_takers = QuizAttempt.objects.values('user').distinct().count()
        average_quiz_score = QuizAttempt.objects.aggregate(Avg('score'))['score__avg']

        quiz_performance_metrics = Quiz.objects.annotate(
            average_score=Avg('quizattempt__score'),
            highest_score=Max('quizattempt__score'),
            lowest_score=Min('quizattempt__score'),
        )

        question_statistics = Question.objects.annotate(total_answers=Count('choices__selectedchoice'))

        return [
            {
                'total_quizzes': total_quizzes,
                'total_quiz_takers': total_quiz_takers,
                'average_quiz_score': average_quiz_score,
                'quiz_performance_metrics': [
                    {
                        'id': quiz.id,
                        'title': quiz.title,
                        'average_score': quiz.average_score,
                        'highest_score': quiz.highest_score,
                        'lowest_score': quiz.lowest_score,
                    }
                    for quiz in quiz_performance_metrics
                ],
                'question_statistics': [
                    {
                        'id': question.id,
                        'content': question.content,
                        'total_answers': question.total_answers,
                    }
                    for question in question_statistics
                ]
            }
        ]
