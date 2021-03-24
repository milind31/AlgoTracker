from django.db import models

class Signup(models.Model):
    email = models.EmailField()
    ticker = models.CharField(max_length=5, default = 'VTI')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
