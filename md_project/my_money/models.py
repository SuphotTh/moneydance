from django.contrib.auth.models import AbstractUser
from django.db import migrations, models

class Transaction(models.Model):
    group = models.CharField(max_length=50)
    category = models.CharField(max_length=100)
    date = models.DateField()
    description = models.CharField(max_length=100)
    account = models.CharField(max_length=200) 
    account_type = models.CharField(max_length=100)
    account_name = models.CharField(max_length=100)
    account_detail = models.CharField(max_length=100)
    memo = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'Transaction'
 
class Category(models.Model):
    group = models.CharField(max_length=50)
    category = models.CharField(max_length=100)
    selected = models.BooleanField(default=True)
    tier = models.IntegerField(default=1) 
    
    class Meta:
        db_table = 'Category'

class Account(models.Model):
    type = models.CharField(max_length=50)
    name = models.CharField(max_length=100)
    detail = models.CharField(max_length=100)
    selected = models.BooleanField(default=True)

    class Meta:
        db_table = 'Account'
        
class Account_type(models.Model):
    desc = models.CharField(max_length=100)
    selected = models.BooleanField(default=True)

    class Meta:
        db_table = 'Account_type'

class Account_name(models.Model):
    desc = models.CharField(max_length=100)
    selected = models.BooleanField(default=True)

    class Meta:
        db_table = 'Account_name'
        
class Account_detail(models.Model):
    desc = models.CharField(max_length=100)
    selected = models.BooleanField(default=True)

    class Meta:
        db_table = 'Account_detail'

class Payee(models.Model):
    name = models.CharField(max_length=50)
    selected = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'Payee'
        
class MonthlyReport(models.Model):
    year = models.IntegerField()
    category = models.CharField(max_length=255)
    tier = models.IntegerField()
    jan = models.DecimalField(max_digits=10, decimal_places=2)
    feb = models.DecimalField(max_digits=10, decimal_places=2)
    mar = models.DecimalField(max_digits=10, decimal_places=2)
    apr = models.DecimalField(max_digits=10, decimal_places=2)
    may = models.DecimalField(max_digits=10, decimal_places=2)
    jun = models.DecimalField(max_digits=10, decimal_places=2)
    jul = models.DecimalField(max_digits=10, decimal_places=2)
    aug = models.DecimalField(max_digits=10, decimal_places=2)
    sep = models.DecimalField(max_digits=10, decimal_places=2)
    oct = models.DecimalField(max_digits=10, decimal_places=2)
    nov = models.DecimalField(max_digits=10, decimal_places=2)
    dec = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def to_dict(self):
        return {
            'year': self.year,
            'category': self.category,
            'tier' : self.tier,
            'jan': self.jan,
            'feb': self.feb,
            'mar': self.mar,
            'apr': self.apr,
            'may': self.may,
            'jun': self.jun,
            'jul': self.jul,
            'aug': self.aug,
            'sep': self.sep,
            'oct': self.oct,
            'nov': self.nov,
            'dec': self.dec,
            'total': self.total,
        }
        
class YearlyReport(models.Model):
    year = models.IntegerField()
    category = models.CharField(max_length=255)
    tier = models.IntegerField()
    year6 = models.DecimalField(max_digits=14, decimal_places=2)
    year5 = models.DecimalField(max_digits=14, decimal_places=2)
    year4 = models.DecimalField(max_digits=14, decimal_places=2)
    year3 = models.DecimalField(max_digits=14, decimal_places=2)
    year2 = models.DecimalField(max_digits=14, decimal_places=2)
    year1 = models.DecimalField(max_digits=14, decimal_places=2)
    total = models.DecimalField(max_digits=14, decimal_places=2)

    def to_dict(self):
        return {
            'year': self.year,
            'category': self.category,
            'tier' : self.tier,
            'year6': self.year6,
            'year5': self.year5,
            'year4': self.year4,
            'year3': self.year3,
            'year2': self.year2,
            'year1': self.year1,
            'total': self.total,
        }
# to add: account_type, account_name, account_details
# Create your models here.
