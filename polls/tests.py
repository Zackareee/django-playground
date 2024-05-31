from django.test import TestCase
import datetime

from django.utils import timezone
from django.urls import reverse

from .models import Question

def create_question(question_text, days):
    time=timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)

class DetailModelTests(TestCase):
    def test_future_question(self):
        question = create_question(question_text="Future question.", days=15)
        response = self.client.get(reverse("polls:detail", args=(question.id)))
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        question = create_question(question_text="Past question.", days=-15)
        response = self.client.get(reverse("polls:detail", args=(question.id)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, question.question_text)

class QuestionModelTests(TestCase):
    def test_no_questions(self):
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])
    
    def test_past_question(self):
        question = create_question(question_text="Past question.", days=-15)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],[question]
            )
        
    def test_future_question(self):
        question = create_question(question_text="Future question.", days=15)
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])\
            

    def test_future_question_and_past_question(self):
        past_question = create_question(question_text="Past question.", days=-15)
        future_question = create_question(question_text="Future question.", days=15)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(response.context["latest_question_list"], [past_question])

    def two_past_questions(self):
        older_question = create_question(question_text="Past question.", days=-15)
        old_question = create_question(question_text="Not so old question.", days=-10)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(response.context["latest_question_list"], [older_question, old_question])

    def test_was_published_recently_with_future_question(self):
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)
    
    def test_was_published_recently_with_recent_question(self):
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), True)
    

        