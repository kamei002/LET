from account.models.users import User
from account.serializer.user import UserSerializer
from account.forms import LoginForm

from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from django.contrib.auth import login, authenticate, logout
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
import logging
logger = logging.getLogger("app")


class Login(APIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    renderer_classes = [TemplateHTMLRenderer]
    template_name = "account/login.html"

    def get(self, request):
        logger.debug(request.user)
        logger.debug(request.user.is_authenticated)
        if request.user.is_authenticated:
            logger.info(f'Logged in pk: {request.user.pk}')
            return redirect('/account/dashboard')
        login_form = LoginForm
        return Response({'login_form': login_form}, template_name='account/login.html')

    def post(self, request):
        email = request.POST['email']
        password = request.POST['password']
        form = LoginForm(request.POST or None)
        user = authenticate(email=email, password=password)
        if user:
            logger.info(f'Login: {user}')
            login(request, user)
            return redirect('/account/dashboard')
        logger.info(f'Login failed email: {email}, password: {password}')
        return Response({'login_form': form, 'login_failed': True}, template_name='account/login.html')


class Logout(APIView):

    def get(self, request):
        logger.debug(request.user)
        logger.debug('logout')
        logout(request)
        return redirect('/account/login/')


class Dashboard(LoginRequiredMixin, APIView):
    renderer_classes = [TemplateHTMLRenderer]

    def get(self, request):
        logger.debug('Dashboard')
        return Response(template_name='account/dashboard.html')
