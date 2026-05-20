from django.urls import path

from . import views

urlpatterns = [
    path("", views.topic_list, name="topic_list"),
    path("topics/<int:group_id>/", views.topic_to_keyword_list, name="topic_to_keyword_list"),
    path("topics/<int:group_id>/categories/<int:category_id>/keywords/", views.keyword_list, name="keyword_list"),
    path("keywords/<int:keyword_id>/", views.question_list, name="question_list"),
    path("api/keyword-summary/", views.get_keyword_summary, name="get_keyword_summary"),
    path("api/page/<int:pk>/", views.gitbookpage_json, name="gitbookpage_json"),
    path("api/keyword-autocomplete/", views.keyword_autocomplete, name="keyword_autocomplete"),
    path("guided-search/", views.guided_search, name="guided_search"),
    path("api/guided-search/", views.guided_search_api, name="guided_search_api"),
    path("api/guided-step2-options/", views.guided_step2_options_api, name="guided_step2_options_api"),
]
