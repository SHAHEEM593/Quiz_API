from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Category, Question, Choice, Quiz, QuizAttempt, SelectedChoice
from django.core.exceptions import ObjectDoesNotExist


User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'first_name', 'last_name']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'content', 'is_correct']

class SelectedChoiceSerializer(serializers.ModelSerializer):
    choice = ChoiceSerializer()  

    class Meta:
        model = SelectedChoice
        fields = ['question', 'choice']

    def create(self, validated_data):
        choice_data = validated_data.pop('choice')
        choice = Choice.objects.get(id=choice_data['id'])  
        selected_choice = SelectedChoice.objects.create(choice=choice, **validated_data)
        return selected_choice

class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True)

    class Meta:
        model = Question
        fields = ['id', 'content', 'choices']

    def create(self, validated_data):
        choices_data = validated_data.pop('choices')
        question = Question.objects.create(**validated_data)

        for choice_data in choices_data:
            Choice.objects.create(question=question, **choice_data)

        return question

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'created_at', 'category', 'questions']

    def create(self, validated_data):
        questions_data = validated_data.pop('questions')
        quiz = Quiz.objects.create(**validated_data)

        for question_data in questions_data:
            choices_data = question_data.pop('choices', [])
            question = Question.objects.create(quiz=quiz, **question_data)

            for choice_data in choices_data:
                Choice.objects.create(question=question, **choice_data)

        return quiz

class SelectedChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SelectedChoice
        fields = ['question', 'choice']

class QuizAttemptSerializer(serializers.ModelSerializer):
    selected_choices = SelectedChoiceSerializer(many=True, write_only=True)

    class Meta:
        model = QuizAttempt
        fields = ['id', 'user', 'quiz', 'date_attempted', 'selected_choices']

    def create(self, validated_data):
        selected_choices_data = validated_data.pop('selected_choices', [])
        score = 0

        quiz_attempt = QuizAttempt(**validated_data)

        for selected_choice_data in selected_choices_data:
            question_id = selected_choice_data['question']
            choice_data = selected_choice_data.get('choice') 
            if not choice_data:
                raise serializers.ValidationError("Choice data not provided.")

            choice_id = choice_data.get('id')

            if not choice_id:
                raise serializers.ValidationError("Choice ID not provided.")

            try:
                question = Question.objects.get(pk=question_id)
                choice = Choice.objects.get(pk=choice_id)
            except ObjectDoesNotExist:
                raise serializers.ValidationError("Question or Choice does not exist.")

            selected_choice = SelectedChoice.objects.create(
                quiz_attempt=quiz_attempt, 
                question=question,
                choice=choice
            )

            if selected_choice.choice.is_correct:
                score += 1

        quiz_attempt.score = score

        quiz_attempt.save()

        return quiz_attempt


class QuizAnalyticsSerializer(serializers.Serializer):
    total_quizzes = serializers.IntegerField()
    total_quiz_takers = serializers.IntegerField()
    average_quiz_score = serializers.FloatField()

class QuizPerformanceMetricsSerializer(serializers.ModelSerializer):
    average_score = serializers.FloatField()
    highest_score = serializers.FloatField()
    lowest_score = serializers.FloatField()

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'average_score', 'highest_score', 'lowest_score']

class QuestionStatisticsSerializer(serializers.ModelSerializer):
    total_answers = serializers.IntegerField()

    class Meta:
        model = Question
        fields = ['id', 'content', 'total_answers']

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email']

class QuizAttemptResultSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username')
    quiz = serializers.CharField(source='quiz.title')
    total_questions = serializers.SerializerMethodField()
    score = serializers.FloatField()
    percentage_score = serializers.SerializerMethodField()
    is_passed = serializers.SerializerMethodField()

    class Meta:
        model = QuizAttempt
        fields = ['user', 'quiz', 'total_questions', 'score', 'percentage_score', 'is_passed']

    def get_total_questions(self, obj):
        return obj.quiz.questions.count()

    def get_percentage_score(self, obj):
        total_questions = obj.quiz.questions.count()
        return (obj.score / total_questions) * 100

    def get_is_passed(self, obj):
        passing_threshold = 40 
        percentage_score = self.get_percentage_score(obj)
        return percentage_score >= passing_threshold


class CombinedStatisticsSerializer(serializers.Serializer):
    total_quizzes = serializers.IntegerField()
    total_quiz_takers = serializers.IntegerField()
    average_quiz_score = serializers.FloatField()
    quiz_performance_metrics = serializers.ListField(child=serializers.DictField())
    question_statistics = serializers.ListField(child=serializers.DictField())

