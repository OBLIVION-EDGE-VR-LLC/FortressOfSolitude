"""
DBA 1337_TECH, AUSTIN TEXAS © MAY 2022
Proof of Concept code, No liabilities or warranties expressed or implied.
"""

from django.urls import re_path
from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import AuthenticationForm
from django.views.generic import RedirectView
from _FortressOfSolitude.superhero.views import FreeSubscription, SubscriptionSuccess
from _FortressOfSolitude.superhero.views import my_403_forbidden_view
# TODO: Create a RegisterCreate View


urlpatterns = [
    re_path(r'^$', RedirectView.as_view(pattern_name='dj-auth:login', permanent=False)),
    re_path(r'^logout/$', auth_views.LogoutView.as_view(template_name='superhero/logged_out.html',
                                                    extra_context={'form': AuthenticationForm}),
        name='logout'),
    re_path(r'^login/$', auth_views.LoginView.as_view(template_name='superhero/login.html'), name='login'),
    re_path(r'^register/$', FreeSubscription.as_view(), name='register_create'),
    re_path(r'register/success', SubscriptionSuccess.as_view(), name="register_success")

]

# handler500 = my_500_error_view
handler403 = my_403_forbidden_view

