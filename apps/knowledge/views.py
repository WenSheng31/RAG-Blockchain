import logging

from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET

from .guided_search_config import GUIDED_SEARCH_STEPS
from .services import (
    build_article_tree,
    get_all_groups,
    get_autocomplete_keywords,
    get_categories,
    get_category,
    get_group,
    get_group_article_count,
    get_group_keyword_count,
    get_guided_search_results,
    get_keyword,
    get_keywords,
    get_learning_path_data,
    get_or_generate_summary,
    get_page,
    get_pages,
    get_questions,
    get_step2_options_data,
)

logger = logging.getLogger(__name__)


def topic_list(request):
    request._nav_page_name = "主題列表"
    return render(request, "knowledge/topic_list.html", {
        "groups": get_all_groups(),
        "guided_steps": GUIDED_SEARCH_STEPS,
    })


def topic_to_keyword_list(request, group_id):
    group = get_group(group_id)
    first = get_categories(group_id).first()
    if not first:
        return redirect("topic_list")
    return redirect("keyword_list", group_id=group.id, category_id=first.id)


def keyword_list(request, group_id, category_id):
    group = get_group(group_id)
    request._nav_page_id = group.id
    request._nav_page_name = group.name
    return render(request, "knowledge/keyword_list.html", {
        "group": group,
        "group_title": group.name,
        "categories": get_categories(group_id),
        "current_category": get_category(group_id, category_id),
        "keywords": get_keywords(group_id, category_id),
        "total_keyword_count": get_group_keyword_count(group_id),
        "total_article_count": get_group_article_count(group_id),
    })


def question_list(request, keyword_id):
    keyword = get_keyword(keyword_id)
    request._nav_page_id = keyword.id
    request._nav_page_name = keyword.keyword
    category = keyword.category
    group = category.group if category else None
    pages = get_pages(keyword_id)
    group_tree, ungrouped = build_article_tree(pages)
    return render(request, "knowledge/question_list.html", {
        "keyword": keyword,
        "group": group,
        "category": category,
        "questions": get_questions(keyword_id),
        "group_tree": group_tree,
        "ungrouped_pages": ungrouped,
        "article_total_count": pages.distinct().count(),
    })


@require_GET
def get_keyword_summary(request):
    keyword = (request.GET.get("keyword") or "").strip()
    if not keyword:
        return JsonResponse({"error": "未提供關鍵字。"}, status=400)
    force = request.GET.get("force") == "1"
    return JsonResponse(get_or_generate_summary(keyword, force=force))


@require_GET
def gitbookpage_json(request, pk):
    page = get_page(pk)
    return JsonResponse({
        "id": page.id,
        "title": page.title,
        "content": page.content or "",
    })


@require_GET
def keyword_autocomplete(request):
    q = (request.GET.get("q") or "").strip()
    if not q:
        return JsonResponse({"results": []})
    results = [
        {
            "id": kw.id,
            "text": kw.keyword,
            "group": kw.group.name if kw.group else "",
            "category": kw.category.name if kw.category else "",
        }
        for kw in get_autocomplete_keywords(q)
    ]
    return JsonResponse({"results": results})


def learning_path(request):
    return render(request, "knowledge/learning_path.html", {
        "topics": get_learning_path_data(),
        "guided_steps": GUIDED_SEARCH_STEPS,
    })


def guided_search(request):
    return render(request, "knowledge/guided_search.html", {"guided_steps": GUIDED_SEARCH_STEPS})


@require_GET
def guided_search_api(request):
    return JsonResponse(get_guided_search_results(
        type_choice=request.GET.get("type", "").strip(),
        context_choice=request.GET.get("context", "").strip(),
        goal_choice=request.GET.get("goal", "").strip(),
    ))


@require_GET
def guided_step2_options_api(request):
    return JsonResponse(get_step2_options_data(request.GET.get("type", "").strip()))
