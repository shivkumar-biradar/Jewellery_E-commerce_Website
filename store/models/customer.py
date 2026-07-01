from django.db import models

class Customer(models.Model):
    name = models.CharField(max_length=50)
    mobile = models.CharField(max_length=15)

    def register(self):
        self.save()

    
    
    def isExists(self):
        if Customer.objects.filter(mobile=self.mobile):
            return True
        else:
            return False