from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from django.shortcuts import redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.mixins import LoginRequiredMixin

from learn_word import models

# from learn_word.tasks.weblio_scrap import Scraper
import logging
logger = logging.getLogger("app")


class WordList(LoginRequiredMixin, APIView):

    renderer_classes = [TemplateHTMLRenderer]

    def get(self, request):
        # logger.debug("scrap")
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
        return Response({'page_obj': page_obj}, template_name='word/list.html')

    def post(self, request):
        return redirect('/account/dashboard')


class Learn(LoginRequiredMixin, APIView):

    renderer_classes = [TemplateHTMLRenderer]

    def get(self, request):
        user = request.user
        study_words = models.show_study_words(user.id)
        study_word = study_words[0]
        word_summary = models.WordSummary.find_one(user.id, study_word.id)
        word_summary.display_count += 1
        word_summary.save()
        word_log = models.WordLog.find_one(user_id=user.id, english_word_id=study_word.id)

        logger.debug(study_word)
        logger.debug(word_summary)
        return Response({'study_word': study_word, "word_summary": word_summary, "word_log": word_log}, template_name='word/learn.html')


class Star(LoginRequiredMixin, APIView):

    def post(self, request):
        user = request.user
        logger.info(request.user.id)
        is_checked = request.data.get('is_checked')
        word_summary_id = request.data.get('word_summary_id')
        logger.debug(f'word_summary_id:{word_summary_id} is_checked:{is_checked}')
        word_summary = models.WordSummary.objects.filter(pk=word_summary_id, user_id=user.id).first()

        if word_summary is None:
            logger.exception("お気に入り登録失敗:一致するデータがありません")
            return Response(data={'error_message': "一致するデータがありません"}, status=status.HTTP_400_BAD_REQUEST)

        word_summary.is_checked = is_checked
        word_summary.save()

        return Response(data={'is_checked': request.data.get('is_checked')}, status=status.HTTP_200_OK)


class UnknownWord(LoginRequiredMixin, APIView):

    def post(self, request):
        user = request.user
        logger.info(request.user.id)
        word_log_id = request.data.get('word_log_id')
        logger.debug(f'word_log_id:{word_log_id} unknown')
        word_log = models.WordLog.objects.filter(pk=word_log_id, user_id=user.id).first()

        if word_log is None:
            logger.exception("わからない単語登録失敗:一致するデータがありません")
            return Response(data={'error_message': "一致するデータがありません"}, status=status.HTTP_400_BAD_REQUEST)

        word_log.is_unknown = True
        word_log.save()

        return Response(status=status.HTTP_200_OK)
