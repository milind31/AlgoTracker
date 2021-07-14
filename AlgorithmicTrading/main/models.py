from django.db import models

#email mailing list signups
class Signup(models.Model):
    email = models.EmailField()
    ticker = models.CharField(max_length=5, default = 'VTI')
    STRATEGIES = [
        ('GC', "Golden Cross"),
        ("ATR", "ATR Limit Order")
        ]
    strategy = models.CharField(
        max_length=100,
        choices=STRATEGIES,
        default='GC'
    )

    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email