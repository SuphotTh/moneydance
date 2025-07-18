from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Max, Min
from datetime import datetime, date, timedelta
from ..models import Transaction, Category, MonthlyReport, YearlyReport, Payee, Account_type, Account_name, Account_detail
from django.utils.functional import SimpleLazyObject

from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers import serialize
from django.conf import settings
from decimal import Decimal
import os, csv, re
import json

# ***********OPEN AI************
import openai
from openai import OpenAI

# ***********LANGCHAIN + OPEN AI************

from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import HumanMessage, SystemMessage
from langchain.memory import ConversationBufferMemory

# ***********LANGCHAIN + HUGGING FACES************
# from langchain import HuggingFaceHub
# from langchain_community.llms.HuggingFaceHub import HuggingFaceHub

from langchain_huggingface import HuggingFaceEndpoint
#from langchain.prompts import ChatPromptTemplate
from django.conf import settings
from decimal import Decimal
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline


@login_required
def home(request):
    if request.method == 'POST':
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
                year = data.get('year')
                selected_tier = data.get('tier')
                selected_type = data.get('type')
                selected_group = data.get('group')

                # Call the refactored monthly_report function
                report_data_set = monthly_report(year, selected_tier, selected_type, selected_group)
                # report_table = report_data['report_table']
                # grand_total = report_data['grand_total']
                # total_expenses = sum(item['amount'] for item in transactions if item['group'] == 'Expenses')
                # print ('expenses', total_expenses )
                # print ("GRAND TOTAL : ", grand_total)

                rep_contents = ai_report(report_data_set, selected_type)

                report_data = {
                    'year' : year,
                    'tier' : selected_tier,
                    'type' : selected_type,
                    'group' : selected_group,
                    'rep_contents': rep_contents,
                }

                return JsonResponse(report_data, safe=False)

            except json.JSONDecodeError:
                return JsonResponse({'error': 'Invalid JSON data'})
        else:
            return JsonResponse({'error': 'Invalid content type. Expected application/json'})

    else:
        oldest_date = Transaction.objects.aggregate(oldest_date=Min('date'))['oldest_date']
        oldest_year = oldest_date.year
        current_year = date.today().year
        year_array = []
        for year in range(current_year, oldest_year, -1):
            year_array.append(str(year))

        context = {
            'header': "รายงานวิเคราะห์การเงิน",
            'year_array': year_array,
        }

        return render(request, 'home.html', context)

def ai_report(report_data_set, selected_type):
    # Extract report_table and grand_total from report_data
    report_table = report_data_set['report_table']
    grand_total = report_data_set['grand_total']
    print("GRAND TOTAL:", grand_total)

    # Custom serialization for dates and decimals
    def custom_serializer(obj):
        if isinstance(obj, (date)):
            return obj.isoformat()  # Convert date to string in ISO format
        elif isinstance(obj, Decimal):
            return str(obj)  # Convert Decimal to string
        raise TypeError(f"Type {type(obj)} not serializable")

    # Convert list of dictionaries to JSON string
    json_transactions = json.dumps(report_table, default=custom_serializer)
    
    # Ensure grand_total is safely converted to a string in the prompt
    grand_total_str = str(grand_total)

    # Create the prompt with placeholders for variables
    prompt_template = """
    You are an expert financial coach. Given the following {json_transactions} in JSON format, total of {selected_type} is {grand_total_str}, 
    analyze the {selected_type}, identify any patterns, highlight the most valuable {selected_type}, 
    and write a comprehensive report with recommendations for financial management. 
    Please format the financial report with appropriate HTML tags. Headers should not be bigger than <h4>, and no need for an HTML skeleton.
    """

    # Initialize the ChatOpenAI model from LangChain
    chat_model = ChatOpenAI(
        model_name="gpt-4-turbo",
        openai_api_key=settings.OPENAI_API_KEY,  # Assuming you have the key stored in Django settings
        max_tokens=2000  # Adjust token limit based on your requirements
    )

    # Initialize memory to manage conversation context (optional for multi-step prompts)
    memory = ConversationBufferMemory()

    # Create a ChatPromptTemplate to fill the prompt with actual data
    prompt = ChatPromptTemplate.from_template(prompt_template)

    # Format the prompt with actual values, now correctly passing grand_total_str
    final_prompt = prompt.format(
        selected_type=selected_type,
        json_transactions=json_transactions,
        grand_total_str=grand_total_str  # Use grand_total_str here
    )

    # Execute the model to get the response
    response = chat_model([SystemMessage(content="You are a financial assistant."), HumanMessage(content=final_prompt)])
    
    # Extract the generated report content
    report = response.content
    print(report)

    return report

@login_required
def inc_exp_report(request):
    user_name = str(request.user).capitalize()
    rep_contents = []

    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        report_type = request.POST.get('report_type')

        # Base query filter for date range
        date_filter = Q(date__range=[start_date, end_date])

        if report_type == "All":
            rep_contents = Transaction.objects.filter(date_filter)
        elif report_type in ["Income", "Expenses"]:
            rep_contents = Transaction.objects.filter(date_filter & Q(group=report_type))

        # Format dates for display
        rep_contents = list(rep_contents)  # Evaluate QuerySet
        for r in rep_contents:
            r.date = r.date.strftime("%Y-%m-%d")

        print(f"Query results: {len(rep_contents)} transactions found")
    else:
        today = date.today()
        start_date = today.replace(day=1).strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")
        report_type = "all"

    context = {
        'rep_contents': rep_contents,
        'start_date': start_date,
        'end_date': end_date,
        'report_type': report_type,
        'header': user_name
    }

    return render(request, 'inc_exp_report.html', context)

# report by range
@login_required
def report_by_range(request):
    if request.method == 'POST':
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
                date_selection = data.get('date_selection')
                selected_tier = data.get('selected_tier')

                if (date_selection == "custom_date"):
                    start_date = data.get('start_date')
                    end_date = data.get('end_date')
                else:
                    date_range = date_range_function(date_selection)
                    start_date = date_range[0]
                    end_date = date_range[1]
                    print ("date range : ", date_range)
                    print ("date range.start : ", start_date)
                    print ("date range.end : ", end_date)

                print ("Date selection : ", date_selection)
                print ("Tier : ", selected_tier)

                def create_report_data(group, selected_tier) :
                    category = Category.objects.filter(tier__lte=selected_tier, group=group).values().distinct()
                    report_data = []
                    # print ("*********category*******")
                    for c in category:
                        category_name = c['category']
                        tier_number = c['tier']
                        # print (f'category_name {category_name} tier_number {tier_number}')
                        rows = Transaction.objects.filter(group=group, 
                                                    category=category_name,
                                                    date__range = [start_date, end_date]).values()
                        for row in rows:
                            row['tier_number'] = tier_number
                            report_data.append(row)
                    return report_data

                income_data = create_report_data ("Income", selected_tier)
                expenses_data = create_report_data ("Expenses", selected_tier)

                date_info = {
                    'start_date': start_date,
                    'end_date': end_date
                }
                print("date info : ",type(date_info))
                # Combining data and additional parameters

                # for data in income_data:
                #     print (data)

                report_data = {
                    'income_data': income_data,
                    'expenses_data': expenses_data,
                    'date_info': date_info
                }

                return JsonResponse(report_data, safe=False)

            except json.JSONDecodeError:
                return JsonResponse({'error': 'Invalid JSON data'})
        else:
            return JsonResponse({'error': 'Invalid content type. Expected application/json'})
    else:
        # Custom dates
        end_date = date.today()
        start_date = end_date.replace(day=1)
        print ("*****start_date*****", start_date)
        start_date = start_date.strftime("%Y-%m-%d")
        end_date = end_date.strftime("%Y-%m-%d")
        custom_date = []
        custom_date.append(start_date)
        custom_date.append(end_date)                

        return render(request, 'report_by_range.html', {'header' : "Income&Expenses ",
                                                        'custom_date' : custom_date })

def date_range_function (date_selection):
    # today
    today = datetime.today().date()
    if (date_selection == 'last_month'):
        #last month
        end_of_last_month = today.replace(day=1) - timedelta(days=1)
        start_date = (end_of_last_month.replace(day=1)).strftime("%Y-%m-%d")
        end_date = (today.replace(day=1) - timedelta(days=1)).strftime("%Y-%m-%d")
    elif (date_selection == 'last_3months'):
        #last 3 months
        start_date = ((today - timedelta(days=88)).replace(day=1)).strftime("%Y-%m-%d")
        end_of_last_month = (today.replace(day=1) - timedelta(days=1)).strftime("%Y-%m-%d")
        end_date = end_of_last_month
    elif (date_selection == 'last_12months'):
        # Last 12 months
        start_date = ((today - timedelta(days=365)).replace(day=1)).strftime("%Y-%m-%d")
        end_of_last_month = (today.replace(day=1) - timedelta(days=1)).strftime("%Y-%m-%d")
        end_date = end_of_last_month
    elif (date_selection == 'last_year'):
        # Last year
        start_date = (datetime(today.year - 1, 1, 1).date()).strftime("%Y-%m-%d")
        end_date = (datetime(today.year - 1, 12, 31).date()).strftime("%Y-%m-%d")
    elif (date_selection == 'ytd'):
        # YTD
        start_date = (today.replace(month=1, day=1)).strftime("%Y-%m-%d")
        end_date = (today).strftime("%Y-%m-%d")

    date_range = []
    date_range.append(start_date)
    date_range.append(end_date)

    return (date_range)

# monthly report
@csrf_exempt
@login_required
def monthly_report_view(request):
    if request.method == 'POST':
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
                year = data.get('year')
                selected_tier = data.get('tier')
                selected_type = data.get('type')
                selected_group = data.get('group')

                # Call the refactored monthly_report function
                report_data = monthly_report(year, selected_tier, selected_type, selected_group)

                return JsonResponse(report_data, safe=False)

            except json.JSONDecodeError:
                return JsonResponse({'error': 'Invalid JSON data'})
        else:
            return JsonResponse({'error': 'Invalid content type. Expected application/json'})
    else :
        oldest_date = Transaction.objects.aggregate(oldest_date=Min('date'))['oldest_date']
        oldest_year = oldest_date.year
        current_year = (date.today().year)+1
        year_array = []
        for year in range(current_year, oldest_year, -1):
            year_array.append(str(year))
        return render(request, 'monthly_report.html', {'year_array' : year_array})
        
def monthly_report (year, selected_tier, selected_type, selected_group):
    start_date = f'{year}-01-01'
    end_date = f'{year}-12-31'

    if selected_tier == '1':
        selected = 2            
    elif selected_tier == '2':
        selected = 3
    elif selected_tier == '3':
        selected = 4
    elif selected_tier == '4':
        selected = 5

    # category = Category.objects.filter(tier__lt=selected).values('category', 'tier')
    # for c in category:
    #     category_name = c['tier']
    #     print (category_name)

    categories = Category.objects.filter(tier__lt=selected).values_list('category', flat=True)
    # print('type of category :', type(categories))

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
            # print("distinct category ----->", c, "tier -->", tier)

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
            # print("distinct name ----->", c, "tier -->", tier)

    return_value = create_12_columns_report(selected_group, year, transactions, category_and_tier)

    # for r in report_table:
    #     print(r.year," : ",r.category," : ",r.jan," : ",r.feb," : ",r.mar," : ",r.apr," : "
    #         ,r.may," : ",r.jun," : ",r.jul," : ",r.aug," : ",r.sep," : ",r.oct," : "
    #         ,r.nov," : ",r.dec," : ",r.total)
        # print (r)
    # report_table = json.dumps(report_table, cls=DjangoJSONEncoder)
    grand_total = return_value['grand_total']
    report_table = return_value['report_table']

    report_table = list(report_table)
    transactions = list(transactions)

    report_data = {
        'grand_total' : grand_total,
        'report_table' : report_table,
        'transactions' : transactions 
    }

    return (report_data)

def create_12_columns_report(group, year, transactions, category_and_tier):
    report_table = []
    grand_total = 0

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
                grand_total += t['amount']

        report_table.append(row.to_dict())

    # print ("Grand Total : ", grand_total)
    return_value = {
        'report_table' : report_table,
        'grand_total' : grand_total,
    }

    return return_value

# yearly report
@login_required
def yearly_report (request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            if request.content_type == 'application/json':
                try:
                    data = json.loads(request.body)
                    year = data.get('year')
                    selected_tier = data.get('tier')
                    selected_type = data.get('type')
                    selected_group = data.get('group')
                    year_start_date = str(int(year) - 5)

                    start_date = year_start_date+'-01-01'
                    end_date = year+'-12-31'

                    print ('start date :', start_date)
                    print ('end date :', end_date)

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
                    # print('type of category :', type(categories))

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
                            # print("distinct category ----->", c, "tier -->", tier)

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
                            # print("distinct name ----->", c, "tier -->", tier)

                    report_table = create_6_columns_report(selected_group, year, transactions, category_and_tier)

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
            # oldest_year = oldest_date.year + 5
            current_year = (date.today().year)+1
            year_array = []
            for year in range(current_year, oldest_year, -1):
                year_array.append(str(year))

            return render(request, 'yearly_report.html', {'year_array' : year_array})
    else:
        return HttpResponseRedirect('main')

def create_6_columns_report(group, year, transactions, category_and_tier):
    report_data = []
    oldest_year = int(year) - 5
    print('Year ', year )
    year_array = []
    for x in range(6):
        year_str = str(oldest_year)
        year_array.append(year_str)
        oldest_year += 1

    # for x in range(5):
    #     print('xx', year_array[x])
    print('xx', year_array[0])
    print('xx', year_array[1])
    print('xx', year_array[2])
    print('xx', year_array[3])
    print('xx', year_array[4])

    # for year in year_array:
    #     print ('year array', year)
    #     print ('type year array', type(year))

    for c in category_and_tier:
        row = YearlyReport(year=year, category=c[0], tier=c[1], year6=0, year5=0, year4=0, year3=0, year2=0, year1=0, total=0)

        for t in transactions:
            if group == 'category':
                name_in_transactions = t['category']
            elif group == 'payee':
                name_in_transactions = t['description']

            if c[0] == name_in_transactions:
                y = t['date']
                yr = str(y.year)

                if yr == year_array[0]:
                    row.year6 += t['amount']
                elif yr == year_array[1]:
                    row.year5 += t['amount']
                elif yr == year_array[2]:
                    row.year4 += t['amount']
                elif yr == year_array[3]:
                    row.year3 += t['amount']
                elif yr == year_array[4]:
                    row.year2 += t['amount']
                elif yr == year_array[5]:
                    row.year1 += t['amount']
                # print('YRYRYR', yr, c[0], t['amount'])
                row.total += t['amount']
        # print (row.to_dict())
        report_data.append(row.to_dict())
    # for r in report_data:
    #     print (r)

    return report_data


