import threading

from django.contrib import admin
from django.contrib.admin import AdminSite
from django.shortcuts import redirect
from django.urls import path

# ── Admin sidebar ordering ────────────────────────────────────────────────────

_APP_ORDER = {"knowledge": 0, "experiment": 1}
_MODEL_ORDER = {
    "knowledge": {
        "KeywordGroup": 0,
        "KeywordCategory": 1,
        "Keyword": 2,
        "ArticleGroup": 3,
        "Article": 4,
        "Question": 5,
        "AISummaryCache": 6,
    },
    "experiment": {
        "NavigationLog": 0,
        "TaskSessionResult": 1,
    },
}

_orig_get_app_list = AdminSite.get_app_list


def _ordered_get_app_list(self, request, app_label=None):
    app_list = _orig_get_app_list(self, request, app_label)
    app_list.sort(key=lambda a: _APP_ORDER.get(a["app_label"], 99))
    for app in app_list:
        order = _MODEL_ORDER.get(app["app_label"], {})
        app["models"].sort(key=lambda m: order.get(m["object_name"], 99))
    return app_list


AdminSite.get_app_list = _ordered_get_app_list

from import_export.admin import ImportExportModelAdmin

from .models import KeywordGroup, KeywordCategory, ArticleGroup, Keyword, Question, Article


@admin.register(KeywordGroup)
class KeywordGroupAdmin(ImportExportModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    fields = ('name', 'description')


@admin.register(KeywordCategory)
class KeywordCategoryAdmin(ImportExportModelAdmin):
    list_display = ("name", "group", "order")
    list_filter = ("group",)
    search_fields = ("name",)
    ordering = ("group", "order", "name")


@admin.register(ArticleGroup)
class ArticleGroupAdmin(ImportExportModelAdmin):
    list_display = ("id", "name", "level", "parent", "order")
    search_fields = ("name",)
    list_filter = ("level",)
    ordering = ("level", "order", "id")


@admin.register(Keyword)
class KeywordAdmin(ImportExportModelAdmin):
    list_display = ('id', 'keyword', 'category', 'created_at', 'updated_at')
    list_filter = ('category__group', 'category')
    search_fields = ('keyword',)
    ordering = ("category__group", "category__order", "keyword")


@admin.register(Question)
class QuestionAdmin(ImportExportModelAdmin):
    list_display = ('id', 'question', 'get_keywords', 'answer', 'created_at', 'updated_at')
    search_fields = ('question', 'answer')
    filter_horizontal = ('keywords',)

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("keywords")

    def get_keywords(self, obj):
        return ", ".join([k.keyword for k in obj.keywords.all()])
    get_keywords.short_description = "關鍵字"


@admin.register(Article)
class ArticleAdmin(ImportExportModelAdmin):
    list_display = ('id', 'title', 'group', 'show_keywords')
    list_filter = ('group',)
    search_fields = ('title', 'content')
    filter_horizontal = ('keywords',)
    change_list_template = "admin/knowledge/article/change_list.html"
    fieldsets = (
        ('基本資料', {'fields': ('title', 'group')}),
        ('內容', {'fields': ('content',)}),
        ('關鍵字設定', {'fields': ('keywords',)}),
    )

    def get_urls(self):
        custom = [
            path("rebuild-faiss/", self.admin_site.admin_view(self.rebuild_faiss_view), name="rebuild_faiss"),
            path("restart-server/", self.admin_site.admin_view(self.restart_server_view), name="restart_server"),
            path("rebuild-and-restart/", self.admin_site.admin_view(self.rebuild_and_restart_view), name="rebuild_and_restart"),
        ]
        return custom + super().get_urls()

    def rebuild_faiss_view(self, request):
        from django.core.management import call_command
        from apps.integrations.ai import reset

        def _rebuild():
            call_command("build_faiss_index")
            reset()

        threading.Thread(target=_rebuild, daemon=True).start()
        self.message_user(request, "FAISS 索引重建中，約需 1-2 分鐘，完成後自動載入新索引（無需重啟）。")
        return redirect("..")

    def restart_server_view(self, request):
        import signal
        from pathlib import Path
        from django.conf import settings

        pid_path = Path(settings.BASE_DIR) / "gunicorn.pid"
        try:
            pid = int(pid_path.read_text().strip())
            import os
            os.kill(pid, signal.SIGHUP)
            self.message_user(request, f"伺服器重啟中（graceful reload，PID {pid}），約 10 秒後生效。")
        except FileNotFoundError:
            self.message_user(request, "找不到 gunicorn.pid，請確認是否以 gunicorn 啟動。", level="WARNING")
        except Exception as exc:
            self.message_user(request, f"重啟失敗：{exc}", level="ERROR")
        return redirect("..")

    def rebuild_and_restart_view(self, request):
        import signal
        import os
        from django.core.management import call_command
        from django.conf import settings
        from pathlib import Path
        from apps.integrations.ai import reset

        pid_path = Path(settings.BASE_DIR) / "gunicorn.pid"

        def _rebuild_then_restart():
            call_command("build_faiss_index")
            reset()
            try:
                pid = int(pid_path.read_text().strip())
                os.kill(pid, signal.SIGHUP)
            except Exception as exc:
                import logging
                logging.getLogger(__name__).warning("Auto-restart failed: %s", exc)

        threading.Thread(target=_rebuild_then_restart, daemon=True).start()
        self.message_user(request, "索引重建中，完成後自動重啟伺服器（約 1-2 分鐘）。")
        return redirect("..")

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("keywords")

    def show_keywords(self, obj):
        if obj.keywords.exists():
            return ", ".join([kw.keyword for kw in obj.keywords.all()])
        return "（無關鍵字）"
    show_keywords.short_description = "相關關鍵字"
