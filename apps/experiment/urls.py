from django.urls import path

from . import views

urlpatterns = [
    path("task/", views.task_view, name="task_view"),
    path("start-task/", views.start_task, name="start_task"),
    path("finish-task/<int:keyword_id>/", views.finish_task, name="finish_task"),
    path("restart-task/", views.restart_task, name="restart_task"),
    path("task/abort/", views.abort_task, name="abort_task"),
    path("api/log-keyword-search/", views.log_keyword_search, name="log_keyword_search"),
    path("api/log-keyword-search-click/", views.log_keyword_search_click, name="log_keyword_search_click"),
    path("api/log-guided-result-click/", views.log_guided_result_click, name="log_guided_result_click"),
]
