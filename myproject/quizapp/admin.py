from django.contrib import admin
from .models import Quiz, Question, Choice, QuizAttempt, SelectedChoice,Category

# Register your models to appear in the Django admin site
admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(Choice)
admin.site.register(QuizAttempt)
admin.site.register(SelectedChoice)
admin.site.register(Category)