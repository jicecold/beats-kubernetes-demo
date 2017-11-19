from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Count

from .models import Question, QuestionVote

def get_session_key(request):
    if not request.session.session_key:
        request.session.save()

    return request.session.session_key

def index(request):
    session_key = get_session_key(request)
    questions = Question.objects.annotate(num_votes=Count('votes')).order_by('-num_votes')[:30]
    votes = QuestionVote.objects.filter(session_key=session_key).values_list('question__id', flat=True)
    context = {
        'questions': questions,
        'votes': votes,
    }
    return render(request, 'questions/index.html', context)

class QuestionCreate(CreateView):
    model = Question
    fields = ['title', 'author']
    success_url = reverse_lazy('questions:index')

def vote(request, question_id):
    session_key = get_session_key(request)
    # Get question
    try:
        question = Question.objects.get(pk=question_id)
    except Question.DoesNotExist:
        messages.add_message(request, messages.ERROR, 'Given question doesn\'t exist')
        return redirect('questions:index')

    try:
        vote = QuestionVote(question=question, session_key=session_key)
        vote.full_clean()
        vote.save()
    except  ValidationError:
        messages.add_message(request, messages.ERROR, 'Error voting question, voted twice?')
    return redirect('questions:index')
