from django.db import models
from django.core.exceptions import ValidationError


class KeywordGroup(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="群組名稱")
    description = models.TextField(blank=True, verbose_name="描述")

    class Meta:
        verbose_name = "關鍵字群組"
        verbose_name_plural = "關鍵字群組"

    def __str__(self):
        return self.name


class KeywordCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name="分類名稱")
    group = models.ForeignKey(
        KeywordGroup,
        on_delete=models.CASCADE,
        related_name="categories",
        verbose_name="群組",
    )
    order = models.PositiveIntegerField(default=0, verbose_name="排序")

    class Meta:
        verbose_name = "關鍵字分類"
        verbose_name_plural = "關鍵字分類"
        unique_together = [["group", "name"]]
        ordering = ["order"]

    def __str__(self):
        return f"{self.group.name} / {self.name}"


class Keyword(models.Model):
    keyword = models.CharField(max_length=100, unique=True, verbose_name="關鍵字")
    keyword_zh = models.CharField(max_length=255, blank=True, verbose_name="中文名稱")
    keyword_en = models.CharField(max_length=255, blank=True, verbose_name="英文全名")
    keyword_abbr = models.CharField(max_length=100, blank=True, verbose_name="英文縮寫")
    definition = models.TextField(blank=True, verbose_name="定義")
    category = models.ForeignKey(
        KeywordCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="keywords",
        verbose_name="分類",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")

    class Meta:
        verbose_name = "關鍵字"
        verbose_name_plural = "關鍵字"

    def __str__(self):
        return self.keyword

    @property
    def group(self):
        return self.category.group if self.category_id and self.category else None


class Question(models.Model):
    keywords = models.ManyToManyField(Keyword, blank=True, related_name="questions", verbose_name="關鍵字")
    question = models.TextField(verbose_name="問題")
    answer = models.TextField(verbose_name="答案")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")

    class Meta:
        verbose_name = "問答"
        verbose_name_plural = "問答"

    def __str__(self):
        return self.question[:50]


class ArticleGroup(models.Model):
    LEVEL_CHOICES = [(1, "main"), (2, "sub"), (3, "third")]

    name = models.CharField(max_length=255, verbose_name="名稱")
    level = models.PositiveSmallIntegerField(choices=LEVEL_CHOICES, verbose_name="層級")
    parent = models.ForeignKey(
        "self",
        null=True, blank=True,
        on_delete=models.CASCADE,
        related_name="children",
        verbose_name="上層群組",
    )
    order = models.PositiveIntegerField(default=0, verbose_name="排序")

    class Meta:
        verbose_name = "文章群組"
        verbose_name_plural = "文章群組"
        unique_together = [["parent", "level", "name"]]

    def clean(self):
        if self.level == 1 and self.parent_id:
            raise ValidationError("Main 不可有 parent")
        if self.level == 2 and (not self.parent_id or self.parent.level != 1):
            raise ValidationError("Sub 必須連接 Main")
        if self.level == 3 and (not self.parent_id or self.parent.level != 2):
            raise ValidationError("Third 必須連接 Sub")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Article(models.Model):
    title = models.CharField(max_length=255, verbose_name="標題")
    content = models.TextField(blank=True, verbose_name="內容（Markdown）")
    group = models.ForeignKey(
        ArticleGroup,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="pages",
        verbose_name="文章群組",
    )
    keywords = models.ManyToManyField(Keyword, blank=True, related_name="articles", verbose_name="關鍵字")

    class Meta:
        verbose_name = "文章"
        verbose_name_plural = "文章"

    def __str__(self):
        return self.title


class AISummaryCache(models.Model):
    keyword = models.CharField(max_length=100, unique=True, verbose_name="關鍵字")
    summary = models.TextField(verbose_name="摘要（Markdown）")
    sources = models.JSONField(default=list, verbose_name="來源文章")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")

    class Meta:
        verbose_name = "AI 摘要快取"
        verbose_name_plural = "AI 摘要快取"

    def __str__(self):
        return self.keyword
