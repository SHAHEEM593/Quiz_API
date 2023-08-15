import django_filters
from .models import Quiz

class QuizFilter(django_filters.FilterSet):
    class Meta:
        model = Quiz
        fields = {
            'category__name': ['icontains'], 
            'difficulty_level': ['exact'],    
            'created_at': ['date'],           
        }
