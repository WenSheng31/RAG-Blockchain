import logging

from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.views.decorators.http import require_POST

from .experiment import TASKS
from .models import NavigationLog
from .services import ExperimentSession, save_experiment_result

logger = logging.getLogger(__name__)


def task_view(request):
    session = ExperimentSession(request.session)
    idx = session.current_index
    if idx >= len(TASKS):
        return render(request, "knowledge/task_done.html")
    task = TASKS[idx]
    request.session["task_id"] = task["task_id"]

    feedback = request.session.get("last_answer_feedback")
    if feedback:
        del request.session["last_answer_feedback"]

    return render(request, "knowledge/task.html", {
        "task": task,
        "task_number": idx + 1,
        "total_tasks": len(TASKS),
        "feedback": feedback,
    })


@require_POST
def start_task(request):
    is_new = (
        request.session.get("current_task_index", 0) == 0
        and not request.session.get("experiment_start_time")
    )
    if is_new:
        request.session.flush()
    session = ExperimentSession(request.session)
    session.initialize()
    task = TASKS[session.current_index]
    session.start_task(task)
    return redirect("topic_list")


def finish_task(request, keyword_id):
    from apps.knowledge.models import Keyword as KW
    session = ExperimentSession(request.session)
    if not session.is_active:
        return redirect("topic_list")

    idx = session.current_index
    task = TASKS[idx]
    end_time = timezone.now()
    start_time = parse_datetime(session.task_start_time) if session.task_start_time else None
    tot_seconds = (end_time - start_time).total_seconds() if start_time else None

    try:
        kw_row = KW.objects.values("keyword", "keyword_en").get(pk=keyword_id)
        selected_text = kw_row["keyword_en"] or kw_row["keyword"]
    except KW.DoesNotExist:
        selected_text = ""

    is_correct = selected_text in task["correct_keywords"]
    session.add_answer({
        "task_id": task["task_id"],
        "selected_keyword_id": keyword_id,
        "selected_keyword": selected_text,
        "is_correct": is_correct,
        "time_seconds": tot_seconds,
    })
    session.end_task()
    next_idx = session.advance()

    if next_idx >= len(TASKS):
        result = save_experiment_result(
            session_key=request.session.session_key,
            answers=session.answers,
            exp_start_str=session.experiment_start_time,
            end_time=end_time,
        )
        session.reset()
        total_sec = int(result.total_time_seconds or 0)
        minutes, seconds = divmod(total_sec, 60)
        time_str = f"{minutes} 分 {seconds} 秒" if minutes else f"{seconds} 秒"
        return render(request, "knowledge/task_done.html", {
            "correct_count": result.correct_count,
            "total_tasks": len(TASKS),
            "accuracy": round(result.accuracy * 100),
            "time_str": time_str,
        })

    request.session["last_answer_feedback"] = {
        "is_correct": is_correct,
        "selected": selected_text,
        "correct_keywords": task["correct_keywords"],
        "task_number": idx + 1,
    }
    return redirect("task_view")


def restart_task(request):
    ExperimentSession(request.session).reset()
    return redirect("task_view")


@require_POST
def abort_task(request):
    ExperimentSession(request.session).reset()
    return JsonResponse({"status": "aborted"})


@require_POST
def log_keyword_search(request):
    if not request.session.get("task_active"):
        return JsonResponse({"status": "ignored"})
    query = request.POST.get("query", "").strip()
    if not query:
        return JsonResponse({"status": "ignored"})
    if not request.session.session_key:
        request.session.create()
    NavigationLog.objects.create(
        session_key=request.session.session_key,
        task_id=request.session.get("task_id"),
        page_type="search",
        page_id=None,
        page_name=f"搜尋：{query}",
    )
    return JsonResponse({"status": "ok"})


@require_POST
def log_keyword_search_click(request):
    if not request.session.get("task_active"):
        return JsonResponse({"status": "ignored"})
    keyword_id = request.POST.get("keyword_id")
    keyword_name = request.POST.get("keyword_name", "").strip()
    query = request.POST.get("query", "").strip()
    if not request.session.session_key:
        request.session.create()
    NavigationLog.objects.create(
        session_key=request.session.session_key,
        task_id=request.session.get("task_id"),
        page_type="search_click",
        page_id=int(keyword_id) if keyword_id else None,
        page_name=f"搜尋點擊：{keyword_name}（查詢：{query}）",
    )
    return JsonResponse({"status": "ok"})


@require_POST
def log_guided_result_click(request):
    if not request.session.get("task_active"):
        return JsonResponse({"status": "ignored"})
    keyword_id = request.POST.get("keyword_id")
    keyword_name = request.POST.get("keyword_name", "").strip()
    type_choice = request.POST.get("type", "").strip()
    context_choice = request.POST.get("context", "").strip()
    goal_choice = request.POST.get("goal", "").strip()
    if not request.session.session_key:
        request.session.create()
    NavigationLog.objects.create(
        session_key=request.session.session_key,
        task_id=request.session.get("task_id"),
        page_type="search_click",
        page_id=int(keyword_id) if keyword_id else None,
        page_name=f"引導式搜尋點擊：{keyword_name}（{type_choice}/{context_choice}/{goal_choice}）",
    )
    return JsonResponse({"status": "ok"})
