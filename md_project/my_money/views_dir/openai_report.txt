# ************************ALL IN THIS VIEWS IS JUST MEMO, IT IS NOT USE FOR ANY URLS.PY OR NO FUNCTIONS TO CALL**************************#

# pip install openai
# pip install openai==0.28
# pip install upgrade openai
# pip install openai==1.0.0
from openai import OpenAI

client = OpenAI()
import json
from datetime import datetime, date
from decimal import Decimal
from openai import OpenAI

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


                    def create_report_data(select):
                        # Get the categories based on the selected parameter
                        categories = Category.objects.filter(selected=select).values_list('category', flat=True)
                        report_data = []                        
                        # Loop through each category
                        for category_name in categories:
                            # Get the transactions for the current category and select only the desired fields
                            rows = Transaction.objects.filter(
                                category=category_name,
                                date__range=[start_date, end_date]
                            ).values(
                                'group',
                                'category',
                                'date',
                                'description',  # We will rename this later
                                'account',
                                'memo',
                                'amount'
                            )

                            # Iterate over the transactions and rename the 'description' field to 'payer_payee'
                            for row in rows:
                                row['payer_payee'] = row.pop('description')
                                report_data.append(row)

                        return report_data

                    # Example usage
                    transactions = create_report_data(True)
                    # print(transactions)
                    num_lines = len(transactions)
                    print ("Transaction = ",num_lines)

                    # Custom serializer function
                    def custom_serializer(obj):
                        if isinstance(obj, (date)):
                            return obj.isoformat()  # Convert date to string in ISO format
                        elif isinstance(obj, Decimal):
                            return str(obj)  # Convert Decimal to string
                        raise TypeError(f"Type {type(obj)} not serializable")

                    # Convert list of dictionaries to JSON string
                    json_transactions = json.dumps(transactions, default=custom_serializer)

                    # Analyze the data
                    total_income = sum(item['amount'] for item in json_transactions if item['group'] == 'income')
                    total_expenses = sum(item['amount'] for item in json_transactions if item['group'] == 'expense')
                    net_balance = total_income - total_expenses

                    # Create a prompt for GPT-4-turbo
                    prompt = f"""
                    The total income for the period is ${total_income}.
                    The total expenses are ${total_expenses}, leading to a net balance of ${net_balance}.
                    Please provide a detailed financial report based on these figures.

                    """

                    # Generate the report using OpenAI's GPT-4-turbo
                    response = client.chat.completions.create(model="gpt-4-turbo",
                    messages=[
                        {"role": "system", "content": "You are a financial assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=200  # Adjust based on your needs)

                    # Output the generated report
                    report = response.choices[0].message.content
                    print(report)



@login_required
def home(request):
    if request.method == 'POST':
        if request.content_type == 'application/json':
            if (report_selection == "1")
                try:
                    data = json.loads(request.body)
                    date_selection = data.get('date_selection')
                    toggled_value = data.get('toggled_value')

                    if (date_selection == "mtd"):
                        end_date = date.today()
                        start_date = end_date.replace(day=1)
                    else:
                        date_range = date_range_function(date_selection)
                        start_date = date_range[0]
                        end_date = date_range[1]

                    print (date_selection)
                    # end_date = '2024-08-10'. #for test
                    # print ("END DATE :", end_date)

                    def create_report_data(select):
                        # Get the categories based on the selected parameter
                        categories = Category.objects.filter(selected=select).values_list('category', flat=True)
                        report_data = []                        
                        # Loop through each category
                        for category_name in categories:
                            # Get the transactions for the current category and select only the desired fields
                            rows = Transaction.objects.filter(
                                category=category_name,
                                date__range=[start_date, end_date]
                            ).values(
                                'group',
                                'category',
                                'date',
                                'description',  # We will rename this later
                                'account',
                                'memo',
                                'amount'
                            )

                            # Iterate over the transactions and rename the 'description' field to 'payer_payee'
                            for row in rows:
                                row['payer_payee'] = row.pop('description')
                                report_data.append(row)

                    # Example usage
                    transactions = create_report_data(True)
                    # Analyze the data
                    total_income = sum(item['amount'] for item in transactions if item['group'] == 'Income')
                    total_expenses = sum(item['amount'] for item in transactions if item['group'] == 'Expenses')
                    net_balance = total_income - total_expenses
                    # print(transactions)
                    # num_lines = len(transactions)
                    # print ("Transaction = ",num_lines)

                except json.JSONDecodeError:
                    return JsonResponse({'error': 'Invalid JSON data'})

            else if (report_selection == "2")

                try:
                    data = json.loads(request.body)
                    date_selection = data.get('date_selection')
                    toggled_value = data.get('toggled_value')

                    transactions = monthly_report()

                except json.JSONDecodeError:
                    return JsonResponse({'error': 'Invalid JSON data'})


            def custom_serializer(obj):
                if isinstance(obj, (date)):
                    return obj.isoformat()  # Convert date to string in ISO format
                elif isinstance(obj, Decimal):
                    return str(obj)  # Convert Decimal to string
                raise TypeError(f"Type {type(obj)} not serializable")
                
            # Custom serializer function
            def custom_serializer(obj):
                if isinstance(obj, (date)):
                    return obj.isoformat()  # Convert date to string in ISO format
                elif isinstance(obj, Decimal):
                    return str(obj)  # Convert Decimal to string
                raise TypeError(f"Type {type(obj)} not serializable")

            # Convert list of dictionaries to JSON string
            json_transactions = json.dumps(transactions, default=custom_serializer)
            # print (json_transactions)

            # Create a prompt for GPT-4-turbo
            prompt = f"""
            You are an expert financial coach. Given the following transactions in JSON format, analyze the income and expenses, 
            identify any patterns, and write a complehensive report with recommendations for financial management.
            The total income for the period is ${total_income}.
            The total expenses are ${total_expenses}, leading to a net balance of ${net_balance}.
            Please format that financial report with appropriate HTML tags. no need HTML skeleton.
            Transactions:
            {json_transactions}

            """ 

            client = OpenAI(api_key = "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")

            # Generate the report using OpenAI's GPT-4-turbo
            response = client.chat.completions.create(model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are a financial assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000 )
                # Adjust based on your needs

            # Access the response content
            report = response.choices[0].message.content
            print(report)

            date_info = {
                'start_date': start_date,
                'end_date': end_date
            }
            print("date info : ",type(date_info))

            report_data = {
                'date_info': date_info,
                'rep_contents': response.choices[0].message.content,
            }

            return JsonResponse(report_data, safe=False)

        else:
            return JsonResponse({'error': 'Invalid content type. Expected application/json'})
    else:
        end_date = date.today()
        start_date = end_date.replace(day=1)
        print ("*****start_date*****", start_date)
        start_date = start_date.strftime("%Y-%m-%d")
        end_date = end_date.strftime("%Y-%m-%d")           

        return render(request, 'home.html', {'header' : "รายงานวิเคราะห์" })


def monthly_report (request):
    if request.method == 'POST':
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
                year = data.get('year')
                selected_tier = data.get('tier')
                selected_type = data.get('type')
                selected_group = data.get('group')

                start_date = year+'-01-01'
                end_date = year+'-12-31'

                if (selected_tier == '1'):
                    selected = 2            
                elif (selected_tier == '2'):
                    selected = 3
                elif (selected_tier == '3'):
                    selected = 4
                elif (selected_tier == '4'):
                    selected = 5

                # category = Category.objects.filter(tier__lt=selected).values('category', 'tier')
                # for c in category:
                #     category_name = c['tier']
                #     print (category_name)

                categories = Category.objects.filter(tier__lt=selected).values_list('category', flat=True)
                print('type of category :', type(categories))

                transactions = Transaction.objects.filter(
                                                        Q(group=selected_type) &
                                                        Q(date__range=[start_date, end_date]) &
                                                        Q(category__in=categories)
                                                        ).values()

                # get distinct category from Transactions filter
                if selected_group == 'category':
                    distinct_name = Transaction.objects.filter(
                                                        Q(group=selected_type) &
                                                        Q(date__range=[start_date, end_date]) &
                                                        Q(category__in=categories)
                                                        ).distinct().values_list('category', flat=True)
                    category_and_tier = []
                    for c in distinct_name:
                        tier_query_set = Category.objects.filter(category=c).values_list('tier', flat=True)
                        tier = tier_query_set.first()  # Use first() to get the first (and only) element
                        category_and_tier.append((c, tier))
                        print("distinct category ----->", c, "tier -->", tier)

                elif selected_group == 'payee':
                    distinct_name = Transaction.objects.filter(
                                                        Q(group=selected_type) &
                                                        Q(date__range=[start_date, end_date]) &
                                                        Q(category__in=categories)
                                                        ).distinct().values_list('description', flat=True)
                    category_and_tier = []
                    for c in distinct_name:
                        tier = ''
                        category_and_tier.append((c, tier))
                        print("distinct name ----->", c, "tier -->", tier)

                report_table = create_12_columns_report(selected_group, year, transactions, category_and_tier)

                # for r in report_table:
                #     print(r.year," : ",r.category," : ",r.jan," : ",r.feb," : ",r.mar," : ",r.apr," : "
                #         ,r.may," : ",r.jun," : ",r.jul," : ",r.aug," : ",r.sep," : ",r.oct," : "
                #         ,r.nov," : ",r.dec," : ",r.total)
                    # print (r)
                # report_table = json.dumps(report_table, cls=DjangoJSONEncoder)

                report_table = list(report_table)
                transactions = list(transactions)

                report_data = {
                    'report_table' : report_table,
                    'transactions' : transactions 
                }

                return JsonResponse(report_data, safe=False)

            except json.JSONDecodeError:
                return JsonResponse({'error': 'Invalid JSON data'})
        else:
            return JsonResponse({'error': 'Invalid content type. Expected application/json'})

    else :
        oldest_date = Transaction.objects.aggregate(oldest_date=Min('date'))['oldest_date']
        oldest_year = oldest_date.year
        current_year = date.today().year
        year_array = []
        for year in range(current_year, oldest_year, -1):
            year_array.append(str(year))

        return render(request, 'monthly_report.html', {'year_array' : year_array})

def create_12_columns_report(group, year, transactions, category_and_tier):
    report_data = []

    for c in category_and_tier:
        # c_t = str(c[1]) + ". " + c[0]
        row = MonthlyReport(year=year, category=c[0], tier=c[1], jan=0, feb=0, mar=0, apr=0, may=0, jun=0, jul=0, aug=0, sep=0, oct=0, nov=0, dec=0, total=0)

        for t in transactions:
            if group == 'category':
                name_in_transactions = t['category']
            elif group == 'payee':
                name_in_transactions = t['description']

            if c[0] == name_in_transactions:
                mnt = t['date']
                month = mnt.month

                if month == 1:
                    row.jan += t['amount']
                elif month == 2:
                    row.feb += t['amount']
                elif month == 3:
                    row.mar += t['amount']
                elif month == 4:
                    row.apr += t['amount']
                elif month == 5:
                    row.may += t['amount']
                elif month == 6:
                    row.jun += t['amount']
                elif month == 7:
                    row.jul += t['amount']
                elif month == 8:
                    row.aug += t['amount']
                elif month == 9:
                    row.sep += t['amount']
                elif month == 10:
                    row.oct += t['amount']
                elif month == 11:
                    row.nov += t['amount']
                elif month == 12:
                    row.dec += t['amount']

                row.total += t['amount']

        report_data.append(row.to_dict())

    print (report_data)
    
    return report_data
