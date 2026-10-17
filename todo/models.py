from django.db import models

# Create your models here.
class TaskModel(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    complated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def completed(self):
        return self.complated

    @completed.setter
    def completed(self, value):
        self.complated = value