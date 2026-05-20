from django.contrib import admin
from django.utils.html import escape
from django.utils.safestring import mark_safe
from .models import NavigationLog, TaskSessionResult


@admin.register(NavigationLog)
class NavigationLogAdmin(admin.ModelAdmin):
    list_display = ("session_key", "task_id", "page_type", "page_name", "timestamp")
    list_filter = ("page_type", "task_id")
    ordering = ("-timestamp",)


@admin.register(TaskSessionResult)
class TaskSessionResultAdmin(admin.ModelAdmin):
    list_display = (
        "session_key",
        "started_at",
        "finished_at",
        "correct_count",
        "accuracy",
        "total_time_seconds",
    )

    ordering = ("-finished_at",)
    readonly_fields = ("answers", "navigation_paths_view")
    fieldsets = (
        ("基本資訊", {
            "fields": (
                "session_key",
                "started_at",
                "finished_at",
                "total_time_seconds",
                "correct_count",
                "accuracy",
            )
        }),
        ("每題作答紀錄（JSON）", {
            "fields": ("answers",),
        }),
        ("瀏覽行為路徑（依題目分組）", {
            "fields": ("navigation_paths_view",),
        }),
    )

    def navigation_paths_view(self, obj):
        logs = (
            NavigationLog.objects
            .filter(session_key=obj.session_key)
            .order_by("timestamp")
        )

        if not logs.exists():
            return "（沒有瀏覽紀錄）"

        paths_by_task = {}
        for log in logs:
            paths_by_task.setdefault(log.task_id, []).append(
                f"[{log.timestamp.strftime('%H:%M:%S')}] "
                f"{log.page_type} - {log.page_name}"
            )

        html = ""
        for task_id, steps in paths_by_task.items():
            html += f"<strong>{escape(str(task_id))}</strong><br>"
            html += "<br>".join(escape(s) for s in steps)
            html += "<hr>"

        return mark_safe(html)

    navigation_paths_view.short_description = "瀏覽路徑（Navigation Paths）"