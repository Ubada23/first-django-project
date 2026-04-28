from django.test import TestCase
import datetime

from django.test import TestCase
from django.utils import timezone

from .models import Question

def create_question(question_text, days):
    """
    Create a question with the given text and number of days offset.
    Negative = past, positive = future
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionModelTests(TestCase):

    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(days=2)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)


    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() returns True for questions whose pub_date
        is within the last day.
        """
        time = timezone.now() - datetime.timedelta(hours=1)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)


class QuestionIndexViewTests(TestCase):

    def test_no_questions(self):
        """
        If no questions exist, show a message
        """
        response = self.client.get("/polls/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")        

    def test_past_question(self):
        """
        Questions with pub_date in the past are displayed on the index page.
        """
        question = create_question(question_text="Past question.", days=-30)
        response = self.client.get("/polls/")
        self.assertContains(response, question.question_text)    

    def test_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        question1 = create_question(question_text="Past question 1.", days=-30)
        question2 = create_question(question_text="Past question 2.", days=-5)

        response = self.client.get("/polls/")

        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question2, question1],
    )    

    def test_past_and_future_questions(self):
        """
        Even if both past and future questions exist,
        only past questions are displayed.
        """
        question = create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)

        response = self.client.get("/polls/")

        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question],
    )

    def test_two_future_questions(self):
        """
        The questions index page shows no questions if all are future.
        """
        create_question(question_text="Future question 1.", days=30)
        create_question(question_text="Future question 2.", days=5)

        response = self.client.get("/polls/")

        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])