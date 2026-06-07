from django.contrib import admin
from django.utils.html import escape
from django.utils.safestring import mark_safe
from import_export import fields, resources
from import_export.admin import ExportMixin
from .models import NavigationLog, TaskSessionResult


def _build_navigation_paths_text(session_key):
    """將指定 session 的 NavigationLog 依 task_id 分組，組成可匯出的純文字路徑描述。"""
    logs = (
        NavigationLog.objects
        .filter(session_key=session_key)
        .order_by("task_id", "timestamp")
    )

    paths_by_task = {}
    for log in logs:
        paths_by_task.setdefault(log.task_id, []).append(
            f"[{log.timestamp.strftime('%H:%M:%S')}] {log.page_type} - {log.page_name}"
        )

    return "\n".join(
        f"[{task_id}] " + " -> ".join(steps)
        for task_id, steps in paths_by_task.items()
    )


class TaskSessionResultResource(resources.ModelResource):
    navigation_paths = fields.Field(column_name="navigation_paths")

    class Meta:
        model = TaskSessionResult
        fields = (
            "session_key",
            "started_at",
            "finished_at",
            "total_time_seconds",
            "correct_count",
            "accuracy",
            "answers",
            "created_at",
            "navigation_paths",
        )
        export_order = fields

    def dehydrate_navigation_paths(self, obj):
        return _build_navigation_paths_text(obj.session_key)


@admin.register(NavigationLog)
class NavigationLogAdmin(admin.ModelAdmin):
    list_display = ("session_key", "task_id", "page_type", "page_name", "timestamp")
    list_filter = ("page_type", "task_id")
    ordering = ("-timestamp",)


@admin.register(TaskSessionResult)
class TaskSessionResultAdmin(ExportMixin, admin.ModelAdmin):
    resource_classes = [TaskSessionResultResource]

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
        text = _build_navigation_paths_text(obj.session_key)
        if not text:
            return "（沒有瀏覽紀錄）"

        html = ""
        for line in text.split("\n"):
            task_id, steps = line.split("] ", 1)
            html += f"<strong>{escape(task_id + ']')}</strong><br>"
            html += "<br>".join(escape(s) for s in steps.split(" -> "))
            html += "<hr>"

        return mark_safe(html)

    navigation_paths_view.short_description = "瀏覽路徑（Navigation Paths）"