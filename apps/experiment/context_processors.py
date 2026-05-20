from .experiment import TASKS

TOTAL_TASKS = len(TASKS)


def current_task(request):
    idx = request.session.get("current_task_index", 0)
    task = TASKS[idx] if idx < TOTAL_TASKS else None
    return {"task": task, "total_tasks": TOTAL_TASKS}
