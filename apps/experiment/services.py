import logging

from django.utils import timezone
from django.utils.dateparse import parse_datetime

from .experiment import TASKS
from .models import NavigationLog, TaskSessionResult

logger = logging.getLogger(__name__)


class ExperimentSession:
    """Encapsulates all experiment session state."""

    def __init__(self, session):
        self._s = session

    @property
    def is_active(self) -> bool:
        return self._s.get("task_active", False)

    @property
    def current_index(self) -> int:
        return self._s.get("current_task_index", 0)

    @property
    def answers(self) -> list:
        return self._s.get("answers", [])

    @property
    def experiment_start_time(self):
        return self._s.get("experiment_start_time")

    @property
    def task_start_time(self):
        return self._s.get("task_start_time")

    def initialize(self):
        if "current_task_index" not in self._s:
            self.reset()

    def reset(self):
        self._s["current_task_index"] = 0
        self._s["task_active"] = False
        self._s["task_id"] = None
        self._s["task_start_time"] = None
        self._s["experiment_start_time"] = None
        self._s["answers"] = []

    def start_task(self, task: dict):
        self._s["task_id"] = task["task_id"]
        self._s["task_active"] = True
        self._s["task_start_time"] = timezone.now().isoformat()
        if self.current_index == 0:
            self._s["experiment_start_time"] = timezone.now().isoformat()
            self._s["answers"] = []

    def end_task(self):
        self._s["task_active"] = False
        self._s["task_start_time"] = None

    def add_answer(self, answer: dict):
        answers = self.answers
        answers.append(answer)
        self._s["answers"] = answers

    def advance(self) -> int:
        next_idx = self.current_index + 1
        self._s["current_task_index"] = next_idx
        return next_idx


def save_experiment_result(
    session_key: str,
    answers: list,
    exp_start_str: str | None,
    end_time,
) -> TaskSessionResult:
    exp_start = parse_datetime(exp_start_str) if exp_start_str else None

    correct_count = sum(1 for a in answers if a["is_correct"])
    accuracy = correct_count / len(answers) if answers else 0.0
    total_time = sum(a["time_seconds"] for a in answers if a["time_seconds"] is not None)

    result = TaskSessionResult.objects.create(
        session_key=session_key,
        started_at=exp_start,
        finished_at=end_time,
        total_time_seconds=total_time,
        correct_count=correct_count,
        accuracy=accuracy,
        answers=answers,
    )

    logger.info("Experiment saved: session=%s, accuracy=%.2f", session_key, accuracy)
    return result
