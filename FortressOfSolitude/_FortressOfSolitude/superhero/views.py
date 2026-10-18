"""
DBA 1337_TECH, AUSTIN TEXAS © MAY 2022
Proof of Concept code, No liabilities or warranties expressed or implied.
"""

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import FormView, CreateView

from .forms import DailyPlanetSubscriber


# Create your views here.
class FreeSubscription(CreateView):
    form_class = DailyPlanetSubscriber
    success_url = reverse_lazy('dj-auth:register_success')
    template_name = 'superhero/registration_form.html'


class SubscriptionSuccess(View):
    template_name = 'superhero/registersuccess.html'

    def dispatch(self, request, *args, **kwargs):
        return render(request, 'superhero/registersuccess.html')


# Create your views here.
def my_500_error_view(request, exception=None):
    return render(request, 'superhero/nuh_uh_uh.html')


def my_403_forbidden_view(request, exception=None):
    return render(request, 'superhero/public_should_only_view_this.html')
