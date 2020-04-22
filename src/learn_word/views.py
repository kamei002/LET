from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from django.shortcuts import redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from learn_word import models

# from learn_word.tasks.weblio_scrap import Scraper
import logging
logger = logging.getLogger("app")


class WordList(APIView):

    renderer_classes = [TemplateHTMLRenderer]

    def get(self, request):
        logger.debug("scrap")
        # s = Scraper()
        # s.begin()

        user = request.user
        word_list = models.EnglishWord.objects.filter(created_by_id=user.id)
        page = request.GET.get('page', 1)

        paginator = Paginator(word_list, 100)
        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
        logger.debug(page_obj)
        return Response({'page_obj': page_obj}, template_name='word/learn.html')

    def post(self, request):
        return redirect('/account/dashboard')
