from .experiment import ALL_SEARCH_MODES, SEARCH_MODE_LABELS, TASKS

TOTAL_TASKS = len(TASKS)


def current_task(request):
    idx = request.session.get("current_task_index", 0)
    task = TASKS[idx] if idx < TOTAL_TASKS else None

    if task and request.session.get("task_active"):
        allowed_modes = task.get("allowed_search_modes", ALL_SEARCH_MODES)
    else:
        allowed_modes = ALL_SEARCH_MODES

    return {
        "task": task,
        "total_tasks": TOTAL_TASKS,
        "allowed_search_modes": allowed_modes,
        "allowed_search_mode_labels": [SEARCH_MODE_LABELS[m] for m in allowed_modes],
    }
