"""
DBA 1337_TECH, AUSTIN TEXAS © MAY 2021
Proof of Concept code, No liabilities or warranties expressed or implied.
"""

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from .models import UserKeyPair

User = get_user_model()


@login_required
def public_key_lookup(request):
    """
    Look up a user's public key by email.
    Returns JSON with the PEM-encoded public key, or 404 if not found.
    Does NOT expose user lists — accepts an email, returns key or 404.
    """
    email = request.GET.get('email')
    if not email:
        return JsonResponse(
            {'error': 'email parameter is required'},
            status=400,
        )

    try:
        target_user = User.objects.get(email=email)
        keypair = UserKeyPair.objects.get(user=target_user)
    except (User.DoesNotExist, UserKeyPair.DoesNotExist):
        return JsonResponse(
            {'error': 'not found'},
            status=404,
        )

    return JsonResponse({
        'public_key': keypair.public_key_pem,
        'email': target_user.email,
    })
