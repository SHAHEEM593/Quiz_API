from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Quiz(models.Model):
    title = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class Question(models.Model):
    content = models.TextField()
    quiz = models.ForeignKey(Quiz, related_name='questions', on_delete=models.CASCADE)

    def __str__(self):
        return self.content

class Choice(models.Model):
    content = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)
    question = models.ForeignKey(Question, related_name='choices', on_delete=models.CASCADE)

    def __str__(self):
        return self.content

class QuizAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    date_attempted = models.DateTimeField(auto_now_add=True)
    score=models.IntegerField()

    def __str__(self):
        return f"{self.user.username} - {self.quiz.title}"

class SelectedChoice(models.Model):
    quiz_attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.quiz_attempt.user.username} - {self.question.content} - {self.choice.content}"

class QuizAnalytics(models.Model):
    quiz_attempt = models.OneToOneField(QuizAttempt, on_delete=models.CASCADE, related_name='analytics')
    total_questions = models.IntegerField()
    total_correct_answers = models.IntegerField()
    percentage_score = models.FloatField()

    def __str__(self):
        return f"{self.quiz_attempt.user.username} - {self.quiz_attempt.quiz.title} - Analytics"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    def __str__(self):
        return self.user.username
