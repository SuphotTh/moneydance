# pip install openai
# pip install openai==0.28
# pip install upgrade openai
# pip install openai==1.0.0
import openai
import json
from datetime import datetime, date
from decimal import Decimal
from openai import openai

# transactions = [{"id": 30318, "group": "Income", "category": "Interest Received", "date": "2024-08-01", "description": "TNTV", "account": "Money Market:BBL TNTV", "account_type": "Money Market", "account_name": "BBL TNTV", "account_detail": "null", "memo": "", "amount": "862.27"}, {"id": 30319, "group": "Income", "category": "Interest Received", "date": "2024-08-02", "description": "TNTV", "account": "Money Market:BBL TNTV", "account_type": "Money Market", "account_name": "BBL TNTV", "account_detail": "null", "memo": "", "amount": "970.05"}, {"id": 30320, "group": "Income", "category": "Interest Received", "date": "2024-08-05", "description": "TNTV", "account": "Money Market:BBL TNTV", "account_type": "Money Market", "account_name": "BBL TNTV", "account_detail": "null", "memo": "", "amount": "862.27"}, {"id": 30321, "group": "Income", "category": "Interest Received", "date": "2024-08-06", "description": "TNTV", "account": "Money Market:BBL TNTV", "account_type": "Money Market", "account_name": "BBL TNTV", "account_detail": "null", "memo": "", "amount": "2586.80"}, {"id": 30322, "group": "Income", "category": "Interest Received", "date": "2024-08-08", "description": "K Treasury", "account": "Money Market:K Treasury", "account_type": "Money Market", "account_name": "K Treasury", "account_detail": "null", "memo": "", "amount": "513.94"}, {"id": 30323, "group": "Income", "category": "Interest Received", "date": "2024-08-08", "description": "TNTV", "account": "Money Market:BBL TNTV", "account_type": "Money Market", "account_name": "BBL TNTV", "account_detail": "null", "memo": "", "amount": "1616.75"}, {"id": 30324, "group": "Income", "category": "Interest Received", "date": "2024-08-08", "description": "SFF", "account": "Money Market:SCB SFF ", "account_type": "Money Market", "account_name": "SCB SFF ", "account_detail": "null", "memo": "", "amount": "1776.88"}, {"id": 30325, "group": "Income", "category": "Interest Received", "date": "2024-08-08", "description": "BizCon Solutions", "account": "Loan to BizCon (TCR 001-10014-0)", "account_type": "Loan to BizCon (TCR 001-10014-0)", "account_name": "null", "account_detail": "null", "memo": "", "amount": "25243.15"}, {"id": 30873, "group": "Income", "category": "Elderly Allowance", "date": "2024-08-09", "description": "department of Older Persons", "account": "Saving Account:Kbank:K 081-X-XXX87-7", "account_type": "Saving Account", "account_name": "Kbank", "account_detail": "K 081-X-XXX87-7", "memo": "", "amount": "600.00"}, {"id": 31119, "group": "Expenses", "category": "Service Charges", "date": "2024-08-01", "description": "KBANK", "account": "Saving Account:Kbank:K ATS 081-X-XX278-8", "account_type": "Saving Account", "account_name": "Kbank", "account_detail": "K ATS 081-X-XX278-8", "memo": "", "amount": "8.00"}, {"id": 31367, "group": "Expenses", "category": "Home Maintenance", "date": "2024-08-05", "description": "Gardener ", "account": "Checking:Pocket Money", "account_type": "Checking", "account_name": "Pocket Money", "account_detail": "null", "memo": "\u0e15\u0e31\u0e14\u0e15\u0e49\u0e19\u0e44\u0e21\u0e49\u0e1b\u0e23\u0e30\u0e08\u0e33\u0e1b\u0e35 \u0e04\u0e38\u0e13\u0e15\u0e4b\u0e2d\u0e22 098 898 3224", "amount": "6000.00"}, {"id": 31615, "group": "Expenses", "category": "Home Meal", "date": "2024-08-03", "description": "Summakorn market", "account": "Saving Account:SCB:SCB Wireless-X-XX361-7 (Prompt Pay with 0816425646 )", "account_type": "Saving Account", "account_name": "SCB", "account_detail": "SCB Wireless-X-XX361-7 (Prompt Pay with 0816425646 )", "memo": "Chicken Roast", "amount": "220.00"}, {"id": 31616, "group": "Expenses", "category": "Home Meal", "date": "2024-08-03", "description": "Summakorn market", "account": "Saving Account:SCB:SCB Wireless-X-XX361-7 (Prompt Pay with 0816425646 )", "account_type": "Saving Account", "account_name": "SCB", "account_detail": "SCB Wireless-X-XX361-7 (Prompt Pay with 0816425646 )", "memo": "\u0e1b\u0e25\u0e32\u0e14\u0e38\u0e01\u0e1f\u0e39", "amount": "120.00"}, {"id": 31696, "group": "Expenses", "category": "Home Monthly Varaible Exp", "date": "2024-08-08", "description": "Tai", "account": "Saving Account:BBL:BBL 198-4-XXX28-7 (Pattanakarn S)", "account_type": "Saving Account", "account_name": "BBL", "account_detail": "BBL 198-4-XXX28-7 (Pattanakarn S)", "memo": "", "amount": "30000.00"}, {"id": 31718, "group": "Expenses", "category": "Insurance Automobile", "date": "2024-08-01", "description": "ThaiSri Insurance", "account": "Saving Account:BBL:BBL 198-4-XXX63-6 (Pattanakarn)Promtpay-ID Card", "account_type": "Saving Account", "account_name": "BBL", "account_detail": "BBL 198-4-XXX63-6 (Pattanakarn)Promtpay-ID Card", "memo": "Benz CLS", "amount": "20000.00"}, {"id": 31969, "group": "Expenses", "category": "My Meals", "date": "2024-08-06", "description": "Burapha Phirom", "account": "Saving Account:SCB:SCB Wireless-X-XX361-7 (Prompt Pay with 0816425646 )", "account_type": "Saving Account", "account_name": "SCB", "account_detail": "SCB Wireless-X-XX361-7 (Prompt Pay with 0816425646 )", "memo": "", "amount": "165.00"}, {"id": 31970, "group": "Expenses", "category": "My Meals", "date": "2024-08-06", "description": "Top Supermaket", "account": "Saving Account:SCB:SCB Wireless-X-XX361-7 (Prompt Pay with 0816425646 )", "account_type": "Saving Account", "account_name": "SCB", "account_detail": "SCB Wireless-X-XX361-7 (Prompt Pay with 0816425646 )", "memo": "\u0e01\u0e30\u0e40\u0e1e\u0e32\u0e30\u0e1b\u0e25\u0e32", "amount": "160.00"}, {"id": 31971, "group": "Expenses", "category": "My Meals", "date": "2024-08-06", "description": "Taobin", "account": "Saving Account:SCB:SCB Wireless-X-XX361-7 (Prompt Pay with 0816425646 )", "account_type": "Saving Account", "account_name": "SCB", "account_detail": "SCB Wireless-X-XX361-7 (Prompt Pay with 0816425646 )", "memo": "", "amount": "45.00"}, {"id": 31972, "group": "Expenses", "category": "My Meals", "date": "2024-08-08", "description": "Central Rama 3", "account": "Saving Account:SCB:SCB Wireless-X-XX361-7 (Prompt Pay with 0816425646 )", "account_type": "Saving Account", "account_name": "SCB", "account_detail": "SCB Wireless-X-XX361-7 (Prompt Pay with 0816425646 )", "memo": "", "amount": "165.00"}, {"id": 31973, "group": "Expenses", "category": "My Meals", "date": "2024-08-08", "description": "Central Rama 3", "account": "Saving Account:SCB:SCB Wireless-X-XX361-7 (Prompt Pay with 0816425646 )", "account_type": "Saving Account", "account_name": "SCB", "account_detail": "SCB Wireless-X-XX361-7 (Prompt Pay with 0816425646 )", "memo": "", "amount": "140.00"}, {"id": 32193, "group": "Expenses", "category": "Federal Income Tax", "date": "2024-08-08", "description": "Tax Department", "account": "Loan to BizCon (TCR 001-10014-0)", "account_type": "Loan to BizCon (TCR 001-10014-0)", "account_name": "null", "account_detail": "null", "memo": "", "amount": "3786.47"}, {"id": 32224, "group": "Expenses", "category": "other expenses: Misc", "date": "2024-08-06", "description": "Tai BBL 5217", "account": "Saving Account:BBL:BBL 198-4-XXX63-6 (Pattanakarn)Promtpay-ID Card", "account_type": "Saving Account", "account_name": "BBL", "account_detail": "BBL 198-4-XXX63-6 (Pattanakarn)Promtpay-ID Card", "memo": "", "amount": "60.00"}]
# print (transactions_json)

def create_report_data(select) :
    category = Category.objects.filter(selected=select).values()
    report_data = []
    # print ("*********category*******")
    for c in category:
        category_name = c['category']
        # print (category_name)
        rows = Transaction.objects.filter(category=category_name, date__range = [start_date, end_date]).values()
        for row in rows:
            report_data.append(row)
    return report_data

transactions = create_report_data(True)

# print ("**********class <list>**********")
# print("Transactions <LIST> : ", transactions)

# Custom serializer function
def custom_serializer(obj):
    if isinstance(obj, (date)):
        return obj.isoformat()  # Convert date to string in ISO format
    elif isinstance(obj, Decimal):
        return str(obj)  # Convert Decimal to string
    raise TypeError(f"Type {type(obj)} not serializable")

# Convert list of dictionaries to JSON string
json_transactions = json.dumps(transactions, default=custom_serializer)

client = OpenAI(api_key = "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")

prompt = f"""
You are an expert financial analyst. Given the following transactions in JSON format, analyze the income and expenses, identify any patterns, and write a comprehensive report with recommendations for financial management.
Please format that financial report with appropriate HTML tags. no need HTML skeleton.
Transactions:
{transactions_json}

Please provide a detailed report.
"""

response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt}
    ]
)

print(response.choices[0].message.content)

rep_contents = response.choices[0].message.content
print(rep_contents)