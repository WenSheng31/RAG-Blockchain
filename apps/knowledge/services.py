import logging
from collections import defaultdict

from django.db.models import Count, F, Q
from django.shortcuts import get_object_or_404

from .models import AISummaryCache, KeywordCategory, Article, Keyword, KeywordGroup, Question
from .guided_search_config import (
    GUIDED_SEARCH_STEPS,
    apply_goal_sort,
    build_guided_query,
    get_guided_result_message,
    get_step2_options,
)
from .learning_path_config import LEARNING_PATH_TOPICS

logger = logging.getLogger(__name__)


# ── KeywordGroup ──────────────────────────────────────────────────────────────

def get_all_groups():
    return KeywordGroup.objects.all()


def get_group(group_id: int) -> KeywordGroup:
    return get_object_or_404(KeywordGroup, id=group_id)


# ── KeywordCategory ───────────────────────────────────────────────────────────

def get_categories(group_id: int):
    return (
        KeywordCategory.objects
        .filter(group_id=group_id)
        .annotate(
            keyword_count=Count("keywords", distinct=True),
            article_count=Count("keywords__articles", distinct=True),
        )
        .order_by("order")
    )


def get_category(group_id: int, category_id: int) -> KeywordCategory:
    return get_object_or_404(
        KeywordCategory.objects
        .filter(group_id=group_id)
        .annotate(
            keyword_count=Count("keywords", distinct=True),
            article_count=Count("keywords__articles", distinct=True),
        ),
        id=category_id,
    )


# ── Keyword ───────────────────────────────────────────────────────────────────

def get_keywords(group_id: int, category_id: int):
    return (
        Keyword.objects
        .filter(category__group_id=group_id, category_id=category_id)
        .annotate(
            article_count=Count("articles", distinct=True),
            question_count=Count("questions", distinct=True),
            total_count=F("article_count") + F("question_count"),
        )
        .order_by("-total_count", "keyword")
    )


def get_keyword(keyword_id: int) -> Keyword:
    return get_object_or_404(
        Keyword.objects.select_related("category", "category__group"),
        pk=keyword_id,
    )


def get_group_keyword_count(group_id: int) -> int:
    return Keyword.objects.filter(category__group_id=group_id).distinct().count()


def get_group_article_count(group_id: int) -> int:
    return Article.objects.filter(keywords__category__group_id=group_id).distinct().count()


def get_autocomplete_keywords(q: str):
    tokens = q.split()
    if not tokens:
        return Keyword.objects.none()
    combined = Q()
    for token in tokens:
        combined |= (
            Q(keyword__icontains=token)
            | Q(keyword_zh__icontains=token)
            | Q(keyword_en__icontains=token)
            | Q(keyword_abbr__icontains=token)
        )
    return (
        Keyword.objects
        .filter(combined)
        .select_related("category__group")
        .distinct()
        .order_by("keyword")[:20]
    )


# ── Question / Article ────────────────────────────────────────────────────────

def get_questions(keyword_id: int):
    return Question.objects.filter(keywords__id=keyword_id).prefetch_related("keywords")


def get_pages(keyword_id: int):
    return (
        Article.objects
        .filter(keywords__id=keyword_id)
        .select_related("group", "group__parent", "group__parent__parent")
        .prefetch_related("keywords")
    )


def get_page(pk: int) -> Article:
    return get_object_or_404(Article, pk=pk)


def build_article_tree(pages) -> tuple[list, list]:
    """Returns (group_tree, ungrouped)."""
    grouped = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    ungrouped = []

    for page in pages:
        g = page.group
        if not g:
            ungrouped.append(page)
            continue
        if g.level == 3 and g.parent and g.parent.parent:
            main, sub, third = g.parent.parent, g.parent, g
        elif g.level == 2 and g.parent:
            main, sub, third = g.parent, g, None
        else:
            main, sub, third = g, None, None
        grouped[main][sub][third].append(page)

    group_tree = []
    for main_obj, subs in grouped.items():
        sub_nodes = []
        main_total = 0
        for sub_obj, thirds in subs.items():
            third_nodes = []
            sub_total = 0
            for third_obj, pages_list in thirds.items():
                count = len(pages_list)
                sub_total += count
                third_nodes.append({"third": third_obj, "pages": pages_list, "count": count})
            main_total += sub_total
            sub_nodes.append({"sub": sub_obj, "thirds": third_nodes, "count": sub_total})
        group_tree.append({"main": main_obj, "subs": sub_nodes, "count": main_total})

    return group_tree, ungrouped


# ── AI Summary ────────────────────────────────────────────────────────────────

def get_or_generate_summary(keyword: str, force: bool = False) -> dict:
    if not force:
        cached = AISummaryCache.objects.filter(keyword=keyword).first()
        if cached:
            return {"keyword": cached.keyword, "summary": cached.summary, "sources": cached.sources}

    K = 5

    # 優先使用明確標記到此關鍵字的文章
    tagged = list(
        Article.objects
        .filter(keywords__keyword=keyword)
        .only("id", "title", "content")
        .distinct()[:K]
    )
    tagged_ids = {p.id for p in tagged}

    # 不足 K 篇時，用 FAISS 補充（排除已有的）
    pages = [p for p in tagged if p.content]
    if len(pages) < K:
        from apps.integrations.ai import get_rag
        rag = get_rag()
        supplement_ids = rag.retrieve(keyword, k=K * 2)
        need = K - len(pages)
        extra_ids = [pid for pid in supplement_ids if pid not in tagged_ids][:need]
        if extra_ids:
            extra_map = {
                p.id: p
                for p in Article.objects.filter(id__in=extra_ids).only("id", "title", "content")
            }
            pages += [extra_map[pid] for pid in extra_ids if pid in extra_map and extra_map[pid].content]
    else:
        rag = None

    if not pages:
        return {"keyword": keyword, "summary": "找不到與此關鍵字相關的內容。", "sources": []}

    if rag is None:
        from apps.integrations.ai import get_rag
        rag = get_rag()

    summary = rag.generate(keyword, [p.content for p in pages])
    sources = [{"id": p.id, "title": p.title} for p in pages]

    AISummaryCache.objects.update_or_create(
        keyword=keyword,
        defaults={"summary": summary, "sources": sources},
    )

    return {"keyword": keyword, "summary": summary, "sources": sources}


# ── Learning Path ─────────────────────────────────────────────────────────────

def get_learning_path_data() -> list:
    result = []
    for topic in LEARNING_PATH_TOPICS:
        keywords = list(
            Keyword.objects
            .filter(id__in=topic["keyword_ids"])
            .annotate(article_count=Count("articles", distinct=True))
            .order_by("keyword")
        )
        kw_data = [
            {
                "id": kw.id,
                "keyword": kw.keyword,
                "keyword_en": kw.keyword_en,
                "article_count": kw.article_count,
            }
            for kw in keywords
        ]
        result.append({**topic, "keywords": kw_data})
    return result


# ── Guided Search ─────────────────────────────────────────────────────────────

def get_guided_search_results(type_choice: str, context_choice: str, goal_choice: str) -> dict:
    q_filter = build_guided_query(
        type_choice=type_choice,
        context_choice=context_choice,
        goal_choice=goal_choice,
    )
    qs = (
        Keyword.objects
        .select_related("category__group")
        .annotate(
            article_count=Count("articles", distinct=True),
            question_count=Count("questions", distinct=True),
        )
    )
    if q_filter:
        qs = qs.filter(q_filter)
    qs = apply_goal_sort(qs, goal_choice).distinct()[:20]

    results = [
        {
            "id": kw.id,
            "keyword": kw.keyword,
            "group": kw.group.name if kw.group else "",
            "category": kw.category.name if kw.category else "",
            "article_count": kw.article_count,
            "question_count": kw.question_count,
            "url": f"/keywords/{kw.id}/",
        }
        for kw in qs
    ]

    return {
        "results": results,
        "count": len(results),
        "type": type_choice,
        "context": context_choice,
        "goal": goal_choice,
        "message": get_guided_result_message(
            type_choice=type_choice,
            context_choice=context_choice,
            goal_choice=goal_choice,
            count=len(results),
        ),
    }


def get_step2_options_data(type_choice: str) -> dict:
    return {"type": type_choice, "options": get_step2_options(type_choice)}
