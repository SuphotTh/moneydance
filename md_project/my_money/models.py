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
    name = models.CharField(max_length=255)
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

class CryptoPurchase(models.Model):
    sym = models.CharField(max_length=20)  # e.g. 'BTC', 'ETH'
    transaction = models.CharField(max_length=50)
    date = models.DateField()
    time = models.TimeField()
    acc_pre_bal = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    acc_post_bal = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    crypto_pre_bal = models.DecimalField(max_digits=18, decimal_places=8)
    crypto_post_bal = models.DecimalField(max_digits=18, decimal_places=8)
    purchase_amount = models.DecimalField(max_digits=18, decimal_places=2)
    purchase_qty = models.DecimalField(max_digits=18, decimal_places=8)
    purchase_price = models.DecimalField(max_digits=18, decimal_places=2)

    # Spare fields (for future use)
    spare_char1 = models.CharField(max_length=100, blank=True, null=True)
    classification = models.CharField(max_length=100, blank=True, null=True)
    fear_greed = models.DecimalField(max_digits=18, decimal_places=4, blank=True, null=True)
    spare_dec2 = models.DecimalField(max_digits=18, decimal_places=4, blank=True, null=True)

    class Meta:
        db_table = 'CryptoPurchase'  # Explicit table name
        managed = False

    def __str__(self):
        return f"{self.sym} | {self.date} {self.time} | Tx: {self.transaction}"

class StockPurchased(models.Model):
    trade_no = models.CharField(max_length=100, unique=True)
    symbol = models.CharField(max_length=20)
    acc_no = models.CharField(max_length=20)
    order_no = models.CharField(max_length=20)
    side = models.CharField(max_length=10)  # e.g., 'Buy' or 'Sell'
    qty = models.DecimalField(max_digits=12, decimal_places=2)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    time = models.TimeField()
    brokerage_fee = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    trading_fee = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    clearing_fee = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)

    # Spare fields for flexibility / future use
    spare_char1 = models.CharField(max_length=100, blank=True, null=True)
    spare_char3 = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'stock_purchased'
        ordering = ['-date', '-time']

    def __str__(self):
        return f"{self.symbol} ({self.side}) - {self.qty}@{self.price} on {self.date} {self.time}"

# for Binance Transactions
class BinanceTransaction(models.Model):
    sym = models.CharField(max_length=20)  # e.g. 'BTC', 'ETH'
    transaction = models.CharField(max_length=50)
    timestamps = models.CharField(max_length=30, blank=True, null=True)
    date = models.DateField()
    time = models.TimeField()
    side = models.CharField(max_length=20)  # "Buy" or "Sell"
    acc_post_bal = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    crypto_post_bal = models.DecimalField(max_digits=18, decimal_places=8)
    purchase_amount = models.DecimalField(max_digits=18, decimal_places=2)
    purchase_qty = models.DecimalField(max_digits=18, decimal_places=8)
    purchase_price = models.DecimalField(max_digits=18, decimal_places=2)
    classification = models.CharField(max_length=100, blank=True, null=True)
    fear_greed = models.DecimalField(max_digits=18, decimal_places=4, blank=True, null=True)

    # Spare fields
    spare_char1 = models.CharField(max_length=100, blank=True, null=True)
    spare_dec2 = models.DecimalField(max_digits=18, decimal_places=4, blank=True, null=True)

    class Meta:
        db_table = "BinanceTransaction"
        # managed = False

    def __str__(self):
        return f"{self.sym} | {self.date} {self.time} | Tx: {self.transaction}"

class CryptoAccumulatedAmount(models.Model):
    sym = models.CharField(max_length=20)

    accumulated_amount = models.DecimalField(max_digits=18, decimal_places=8, blank=True, null=True)

    timestamp = models.CharField(max_length=30, blank=True, null=True)

    # Spare fields
    spare1 = models.CharField(max_length=100, blank=True, null=True)
    spare2 = models.CharField(max_length=100, blank=True, null=True)
    spare3 = models.DecimalField(max_digits=18, decimal_places=4, blank=True, null=True)
    spare4 = models.DecimalField(max_digits=18, decimal_places=4, blank=True, null=True)

    class Meta:
        db_table = "CryptoAccumulatedAmount"
        # managed = False

    def __str__(self):
        return f"{self.sym} | Acc: {self.accumulated_amount}"

class CryptoSymbolStatus(models.Model):
    sym = models.CharField(max_length=20)

    buy_status = models.BooleanField(default=False)
    sell_status = models.BooleanField(default=False)

    zone_color = models.CharField(max_length=10, blank=True, null=True)
    timestamp = models.CharField(max_length=30, blank=True, null=True)

    # Spare fields
    spare1 = models.CharField(max_length=100, blank=True, null=True)
    spare2 = models.CharField(max_length=100, blank=True, null=True)
    spare3 = models.DecimalField(max_digits=18, decimal_places=4, blank=True, null=True)
    spare4 = models.DecimalField(max_digits=18, decimal_places=4, blank=True, null=True)

    class Meta:
        db_table = "CryptoSymbolStatus"
        # managed = False

    def __str__(self):
        return f"{self.sym} | Buy:{self.buy_status} Sell:{self.sell_status}"


# to add: account_type, account_name, account_details
# Create your models here.
