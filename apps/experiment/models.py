from django.db import models


class NavigationLog(models.Model):
    session_key = models.CharField(max_length=100, db_index=True, verbose_name="Session Key")
    task_id = models.CharField(max_length=10, db_index=True, verbose_name="任務編號")
    page_type = models.CharField(
        max_length=20,
        choices=[
            ("topic", "主題頁"),
            ("learning_path", "新手入口"),
            ("keyword", "關鍵詞頁"),
            ("keyword_item", "關鍵字詳細頁"),
            ("search", "關鍵詞搜尋"),
            ("search_click", "搜尋結果點擊"),
        ],
        verbose_name="頁面類型",
    )
    page_id = models.IntegerField(null=True, blank=True, verbose_name="頁面 ID")
    page_name = models.CharField(max_length=200, verbose_name="頁面名稱")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="時間戳記")

    class Meta:
        verbose_name = "導航記錄"
        verbose_name_plural = "導航記錄"
        indexes = [
            models.Index(fields=["session_key", "timestamp"], name="idx_nav_session_ts"),
        ]

    def __str__(self):
        return f"{self.task_id} | {self.page_type} | {self.page_name}"


class TaskSessionResult(models.Model):
    session_key = models.CharField(max_length=40, db_index=True, verbose_name="Session ID")
    started_at = models.DateTimeField(verbose_name="開始時間")
    finished_at = models.DateTimeField(verbose_name="結束時間")
    total_time_seconds = models.FloatField(verbose_name="總花費時間（秒）")
    correct_count = models.PositiveIntegerField(verbose_name="答對題數")
    accuracy = models.FloatField(verbose_name="正確率")
    answers = models.JSONField(verbose_name="作答紀錄")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "實驗結果"
        verbose_name_plural = "實驗結果"
        indexes = [
            models.Index(fields=["-finished_at"], name="idx_session_finished"),
        ]

    def __str__(self):
        return f"Session {self.session_key} | Acc={self.accuracy:.2f}"
