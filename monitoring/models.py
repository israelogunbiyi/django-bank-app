from django.db import models

# Create your models here.
class Customer(models.Model):
  name = models.CharField(max_length=150)
  customer_num = models.CharField(max_length=50, unique=True)
  
  def __str__(self):
    return self.name
  
  
class Transaction(models.Model):
  reference = models.CharField(max_length=100, unique=True)
  customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
  amount = models.DecimalField(max_digits=18, decimal_places=2)
  created_at = models.DateTimeField()
  flagged = models.BooleanField(default=False)
  processed = models.BooleanField(default=False)
  
  def __str__(self):
    return self.reference
    