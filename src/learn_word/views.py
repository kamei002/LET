from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from django.shortcuts import redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.cache import cache

from learn_word import models
from config import tasks

# from learn_word.tasks.weblio_scrape import Scraper
import logging
logger = logging.getLogger("app")


class WordList(LoginRequiredMixin, APIView):

    renderer_classes = [TemplateHTMLRenderer]

    def get(self, request):
        # logger.debug("scrape")
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


@login_required
def category(request):
    category_id = request.GET.get('category_id')
    logger.debug(category_id)
    path = '/'
    if category_id:
        this_category = models.WordCategory.objects.get(pk=category_id)
        path = f'{this_category.path}{this_category.id}/'
        this_category.learn_url = f'/word/learn?category_id={this_category.id}'
    else:
        this_category = models.WordCategory(name='All categories')
        this_category.learn_url = f'/word/learn'

    categories = models.WordCategory.get_category(path=path)
    for category in categories:
        category.visible = category.has_word_relations()

    data = {'categories': categories, 'this_category': this_category}
    return render(request, template_name='word/category.html', context=data)

@login_required
def learn(request):
    index = request.GET.get("index", 0)
    category_id = request.GET.get("category_id", 'None')
    index = int(index)
    try:
        if category_id == 'None':
            category_id = None
        else:
            category_id = int(category_id)

    except Exception:
        logger.error(f"wired category_id:{category_id}")
        category_id = None

    user = request.user
    setting = models.WordLearnSetting.find_by_user_id(user.id)
    limit = setting.learn_num

    key = f'{user.id}_study_words_{category_id}'
    if index == 0:
        cache.delete(key)

    study_words = cache.get(key)
    logger.info(study_words)
    if(not study_words):
        study_words = models.show_study_words(category_id=category_id, limit=limit)
        cache.set(key, study_words, timeout=25)

    word_count = study_words.count()
    if(word_count < index+1):
        cache.delete(key)
        if category_id:
            return redirect(f'/word/learn/result?category_id={category_id}')

        return redirect('/word/learn/result')

    study_word = study_words[index]
    word_summary = models.WordSummary.find_one(user.id, study_word.id)
    word_summary.display_count += 1
    word_summary.save()
    word_log = models.WordLog.get_one(user_id=user.id, english_word_id=study_word.id)

    data = {
        'study_word': study_word,
        "word_summary": word_summary,
        "word_log": word_log,
        "index": index,
        "category_id": category_id,
        "word_count": word_count,
    }
    return render(request, template_name='word/learn.html', context=data)

@login_required
def learn_result(request):
    user = request.user
    setting = models.WordLearnSetting.find_by_user_id(user.id)
    limit = setting.learn_num
    word_logs = models.WordLog.get_learn_result(user_id=user.id, limit=limit)
    for word in word_logs:
        english_word = word.english_word
        word_summary = models.WordSummary.find_one(
            user_id=user.id,
            english_word_id=english_word.id
        )
        word.display_count = word_summary.display_count

    category_id = request.GET.get("category_id", 'None')
    if(category_id == 'None'):
        learn_url = f'/word/learn'
    else:
        learn_url = f'/word/learn?category_id={category_id}'

    data = {
        'category_id': category_id,
        'learn_url': learn_url,
        'word_logs': word_logs,
    }

    return render(request, template_name='word/learn_result.html', context=data)


@login_required
def scrape(request):
    tasks.scrape_weblio.delay()
    return render(request, status=status.HTTP_200_OK)
