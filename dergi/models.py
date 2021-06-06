from django.db import models

# Create your models here.
class Dergi(models.Model):
    ISSN = models.CharField(max_length=120, primary_key=True, verbose_name="ISSN No")
    dergiAdi = models.CharField(max_length=120)
    citeScore = models.CharField(max_length=120)
    SNIP = models.CharField(max_length=120)
    SJR = models.CharField(max_length=120)
    img_src = models.CharField(max_length=200)
    aimNscope = models.TextField()
    last_year = models.CharField(max_length=4)
    first_score = models.CharField(max_length=10)
    final_score = models.CharField(max_length=10)

    def __str__(self):
        return self.ISSN


class AbstractnIndex(models.Model):
    ISSN = models.ForeignKey(Dergi, null=True, on_delete=models.CASCADE)
    list = models.TextField()

    def __str__(self):
        asd = self.ISSN.ISSN + " nolu dergi"
        return asd


class Editors(models.Model):
    ISSN = models.ForeignKey(Dergi, null=True, on_delete=models.CASCADE)
    Editor = models.TextField()
    EditorInfo = models.TextField()

    def __str__(self):
        asd = self.ISSN.ISSN + " nolu derginin editörü"
        return asd

class ArticlesInPress(models.Model):
    ISSN = models.ForeignKey(Dergi, null=True, on_delete=models.CASCADE)
    ArticleNumber = models.CharField(max_length=100)

    def __str__(self):
        asd = self.ISSN.ISSN + " nolu derginin yayinlanacak olan makale sayilari"
        return asd

class PublishedArticles(models.Model):
    ISSN = models.ForeignKey(Dergi, null=True, on_delete=models.CASCADE)
    Year = models.CharField(max_length=100)
    Number = models.CharField(max_length=100)

    def __str__(self):
        asd = self.ISSN.ISSN + " nolu derginin yayinlanmis olan makale sayilari"
        return asd

class Volume(models.Model):
    ISSN = models.ForeignKey(Dergi, null=True, on_delete=models.CASCADE)
    Year = models.TextField()
    PublicationNumber = models.TextField()

    def __str__(self):
        asd = self.ISSN.ISSN + " nolu derginin makale sayıları"
        return asd