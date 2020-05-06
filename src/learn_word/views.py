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


from learn_word import forms
from learn_word import models
import logging
logger = logging.getLogger("app")


class WordList(LoginRequiredMixin, APIView):

    renderer_classes = [TemplateHTMLRenderer]

    def get(self, request):

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


class AnswerWord(LoginRequiredMixin, APIView):

    def post(self, request):
        user = request.user
        logger.info(request.user.id)
        word_log_id = request.data.get('word_log_id')
        is_unknown = request.data.get('is_unknown')
        logger.debug(f'word_log_id:{word_log_id} is_unknown: {is_unknown}')
        word_log = models.WordLog.objects.filter(pk=word_log_id, user_id=user.id).first()

        if word_log is None:
            logger.exception("わからない単語登録失敗:一致するデータがありません")
            return Response(data={'error_message': "一致するデータがありません"}, status=status.HTTP_400_BAD_REQUEST)

        if is_unknown:
            word_log.mark_unknown()
        else:
            word_log.mark_known()

        return Response(status=status.HTTP_200_OK)

class Setting(LoginRequiredMixin, APIView):

    renderer_classes = [TemplateHTMLRenderer]

    def get(self, request):
        user = request.user
        setting = models.WordLearnSetting.find_by_user_id(user.id)
        form = forms.SettingForm(setting.__dict__)
        data = {
            'form': form,
        }
        return Response(data=data, template_name='word/setting.html')

    def post(self, request):
        user = request.user
        setting = models.WordLearnSetting.find_by_user_id(user.id)
        logger.debug(request.POST)
        form = forms.SettingForm(request.POST, instance=setting)

        data = {
            'form': form,
        }
        if not form.is_valid():
            logger.debug(f'validate error: {form}')
            return Response(data=data, template_name='word/setting.html')

        form.save()

        return redirect('/account/dashboard')

@login_required
def category(request):
    category_id = request.GET.get('category_id')
    path = '/'
    if category_id:
        this_category = models.WordCategory.objects.get(pk=category_id)
        path = f'{this_category.path}{this_category.id}/'
    else:
        this_category = models.WordCategory(name='All categories')

    categories = models.WordCategory.get_category(path=path)
    for category in categories:
        category.visible = category.has_word_relations()

    data = {'categories': categories, 'this_category': this_category}
    return render(request, template_name='word/category.html', context=data)

@login_required
def learn(request):
    index = request.GET.get("index", 0)
    category_id = request.GET.get("category_id", 'None')
    visible_checked = request.GET.get("visible_checked", 0)
    if visible_checked:
        visible_checked = 1
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

    key = f'study_words_user_{user.id}_checked_{visible_checked}_category_{category_id}'
    if index == 0:
        cache.delete(key)

    study_words = cache.get(key)
    if(not study_words):
        study_words = models.show_study_words(
            user_id=user.id,
            category_id=category_id,
            limit=limit,
            is_checked=visible_checked
        )
        study_words = list(study_words)
        cache.set(key, study_words, timeout=60*60*3)
        logger.info("get study_words")

    word_count = len(study_words)
    if(word_count < index+1):
        cache.delete(key)
        url = f'/word/learn/result?limit={word_count}'
        if category_id:
            url += f'&category_id={category_id}'
        if visible_checked:
            url += f'&visible_checked={visible_checked}'
        return redirect(url)

    study_word = study_words[index]
    word_log = models.WordLog.create(user_id=user.id, english_word_id=study_word.id)
    word_summary = word_log.get_word_summary()
    synonyms = models.Synonyms.objects.filter(synonym_word_id=study_word.id)
    logger.debug(f"synonyms:{synonyms}")

    data = {
        'study_word': study_word,
        "word_summary": word_summary,
        "word_log": word_log,
        "index": index,
        "category_id": category_id,
        "word_count": word_count,
        "visible_checked": visible_checked,
        "synonyms": synonyms,
    }
    return render(request, template_name='word/learn.html', context=data)

@login_required
def learn_result(request):
    user = request.user
    # setting = models.WordLearnSetting.find_by_user_id(user.id)

    limit = request.GET.get("limit", 0)
    limit = int(limit)
    word_logs = models.WordLog.get_learn_result(user_id=user.id, limit=limit)

    rate = len([l for l in word_logs if l.is_unknown is False]) / len(word_logs) * 100
    for word in word_logs:
        english_word = word.english_word
        word_summary = models.WordSummary.find_one(
            user_id=user.id,
            english_word_id=english_word.id
        )
        word.display_count = word_summary.display_count
        word.display_order = word_summary.order

    category_id = request.GET.get("category_id", 'None')
    visible_checked = request.GET.get("visible_checked", 0)
    learn_url = f'/word/learn?continue=1'
    if(category_id != 'None'):
        learn_url += f'&category_id={category_id}'
    if visible_checked:
        learn_url += f'&visible_checked={visible_checked}'

    data = {
        'category_id': category_id,
        'learn_url': learn_url,
        'word_logs': word_logs,
        'rate': rate,
    }

    return render(request, template_name='word/learn_result.html', context=data)
