from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect
from ..models import Transaction, Category, Payee, Account_type, Account_name, Account_detail
from datetime import datetime, date, timedelta
from django.db import transaction
import csv
import re
import io
import json

@login_required
def set_tier(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            # Ensure 'application/json' content type
            if request.content_type == 'application/json':
                # Parse JSON data from the request body
                data = json.loads(request.body)
                
                id_value = data.get('id')
                tier_value = data.get('tier')
                table_name = data.get('table_name')
                backend_table = data.get('backend_table')
                
                print(f'id: {id_value}, tier_value: {tier_value}, set_table: {backend_table}')
                
                row = Category.objects.get(id = id_value)
                row.tier = tier_value
                row.save()
                response = " "+table_name+' updated successfully'

                response_data = {'message': response}
                return JsonResponse(response_data)
            else:
                return JsonResponse({'error': 'Invalid content type. Expected application/json'})
        
        # Handle other cases or methods (GET, etc.) if needed
        return JsonResponse({'error': 'Invalid request'})   
    else:
        return HttpResponseRedirect('main')

@login_required
def set_selection(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            # Ensure 'application/json' content type
            if request.content_type == 'application/json':
                # Parse JSON data from the request body
                data = json.loads(request.body)
                
                # Access the data fields sent from the frontend
                id_value = data.get('id')
                selected_value = data.get('selected')
                table_name = data.get('table_name')
                backend_table = data.get('backend_table')
                
                # Perform operations with the received data
                # For example, print the values and send a JSON response
                print(f'id: {id_value}, selected: {selected_value}, set_table: {backend_table}')
                
                if backend_table == "payee":
                    row = Payee.objects.get(id = id_value)
                    row.selected = selected_value
                    row.save()
                    response = 'Payee updated successfully'
                elif backend_table == "account_type":
                    row = Account_type.objects.get(id = id_value)
                    row.selected = selected_value
                    row.save()
                    response = 'Account type updated successfully'
                elif backend_table == "account_name":
                    row = Account_name.objects.get(id = id_value)
                    row.selected = selected_value
                    row.save()
                    response = 'Account name updated successfully'
                elif backend_table == "category":
                    row = Category.objects.get(id = id_value)
                    row.selected = selected_value
                    row.save()
                    response = " "+table_name+' updated successfully'

                response_data = {'message': response}
                return JsonResponse(response_data)
            else:
                return JsonResponse({'error': 'Invalid content type. Expected application/json'})
        
        # Handle other cases or methods (GET, etc.) if needed
        return JsonResponse({'error': 'Invalid request'}) 
    else:
        return HttpResponseRedirect('main')

@login_required
def get_dataset(request):
    if request.method == 'POST':
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
                backend_table = data.get('backend_table')
                table_name = data.get('table_name')
                print('table', backend_table, 'table_name', table_name)

                if backend_table == 'category':
                    if table_name == 'income':
                        fetched_data = Category.objects.filter(group="Income").order_by('category').values()
                    elif table_name == 'expenses':
                        fetched_data = Category.objects.filter(group="Expenses").order_by('category').values()
                elif backend_table == 'payee':
                    fetched_data = Payee.objects.all().order_by('name').values()
                elif backend_table == 'account_type':
                    fetched_data = Account_type.objects.all().order_by('desc').values()
                elif backend_table == 'account_name':
                    fetched_data = Account_name.objects.all().order_by('desc').values()
                else:
                    return JsonResponse({'error': 'Invalid backend_table'}, status=400)

                return JsonResponse(list(fetched_data), safe=False)
            except json.JSONDecodeError:
                return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        else:
            return JsonResponse({'error': 'Invalid content type. Expected application/json'}, status=400)

    # If it's a GET request, render the settings.html template
    return render(request, 'settings.html')

@login_required
@csrf_exempt
def convert_moneydance(request):
    if request.method == 'GET':
        return render(request, 'convert_moneydance.html', {'header': "Please check and submit"})
        
    elif request.method == 'POST':
        try:
            csv_file = request.FILES.get('csvFile')
            if not csv_file:
                return JsonResponse({'message': 'No file was uploaded.'}, status=400)
        
            if csv_file.name != "Income and Expenses Detailed.csv":
                return JsonResponse({'message': 'Incorrect file. Please upload "Income and Expenses Detailed.csv"'}, status=400)
            
            print (" csv file name =", csv_file) 
            # csv_data = csv_file.read().decode('utf-8')
            # csv_reader = csv.reader(io.StringIO(csv_data))
            # source_file_path = '../md_project/data/Income and Expenses Detailed.csv'
            print ("Start processing----------------------->")
            today = date.today()
            this_year = int(today.strftime("%Y"))
            last_year = this_year - 1
            print ('last year -> ', last_year)
            print ("Start processing_2------------------------------------>")
            csv_data = csv_file.read().decode('utf-8')
            csv_file_like_object = io.StringIO(csv_data)

            csv_reader = csv.reader(csv_file_like_object)
            # with open(csv_file, 'r') as source_file:
            #     csv_reader = csv.reader(source_file)
            print ('***************source file loop******************')
            i = 0
            col0 = ""
            col1 = ""
            rep_contents = []
            for csv_row in csv_reader:
                if (i >=4  and csv_row): 
                    if (csv_row[0]):
                        if (csv_row[0][0:3] == "   "):
                            col1 = (csv_row[0][3:]).strip()
                        else:
                            col0 = csv_row[0]
                    elif not(csv_row[1] and csv_row[2]):
                        print ("***************in csv loop ******************")
                    elif not(csv_row[0]):
                        
                        date_object = datetime.strptime(csv_row[1], '%d/%m/%Y')
                        # Convert the datetime object to a string in the format YYYY-MM-DD
                        formatted_date = date_object.strftime('%Y-%m-%d')
                        
                        year = int(date_object.strftime("%Y"))
                        # select only date from first day of last year until current date
                        # if (year >= 2013) : ********************************** on when first initial data
                        if (year >= last_year) :
                            row = Transaction()
                            row.group = col0
                            row.category = col1
                            row.date = formatted_date
                            row.account = csv_row[2]
                            row.description = csv_row[3]
                            row.memo =  csv_row[4]
                            row.amount = csv_row[5]
                            rep_contents.append(row)  
                            # print(rep_contents)                                
                i = i+1
                    
            current_year = date.today().year
            # Calculate the last year
            last_year = current_year - 1
            # Define the filter condition
            filter_condition = {'date__gte': f'{last_year}-01-01', 'date__lt': f'{current_year}-12-31'}
            # Delete rows only last year-01-01 to current year-12-31 and replace with data in rep_contents
            Transaction.objects.filter(**filter_condition).delete()        
            # Transaction.objects.all().delete()   ************************ON when first initial data                 
            for transaction_data in rep_contents:
            
                account_type = ""
                account_name = ""
                account_detail = ""
                # split_text(transaction_data.account)
                
                t = transaction_data.account
                colon_count = transaction_data.account.count(":")
                if colon_count == 0:
                    account_type = transaction_data.account
                    account_name = "null"
                    account_detail = "null"
                elif colon_count == 1:
                    account_array = re.split(r':', t, maxsplit=1)
                    account_type = account_array[0]
                    account_name = account_array[1]
                    account_detail = "null"
                elif colon_count == 2:
                    account_array = re.split(r':', t, maxsplit=2)
                    account_type = account_array[0]
                    account_name = account_array[1]
                    account_detail = account_array[2]                        
                
                # print (account_type,"  -->   ",account_name,"   --->>    ", account_details)
                
                # Create a Transaction object for each dictionary in rep_content
                transaction = Transaction(
                group=transaction_data.group,
                category=transaction_data.category,
                date=transaction_data.date,
                description=transaction_data.description,
                account=transaction_data.account,
                account_type=account_type,
                account_name=account_name,
                account_detail=account_detail,
                memo=transaction_data.memo,
                amount=transaction_data.amount)
                
                transaction.save()
            print ("transaction table is updated")

            records_to_delete = Category.objects.filter(group='')
            # Delete the filtered records
            records_to_delete.delete()

            transactions = Transaction.objects.values('category', 'group').distinct()
            for t in transactions:
                # Check if the category for this group already exists
                category_exists = Category.objects.filter(group=t['group'], category=t['category']).exists()
                if category_exists:
                    pass
                else:
                    # Create a new Category entry since it doesn't exist
                    Category.objects.create(group=t['group'], category=t['category'])
                    print('Writing data for group =', t['group'], ", category =", t['category'])
            print("Updated category table")

            def update_child_table(parent_column, Child_table, child_column):
                transactions = Transaction.objects.values(parent_column).distinct()
                print ("parent column = ", parent_column)
                print ("child table = ", Child_table)
                for t in transactions:
                    # print (t[parent_column])
                    obj_exists = Child_table.objects.filter(**{child_column: t[parent_column]}).exists()
                    if obj_exists:
                        pass
                    else:
                        Child_table.objects.create(**{child_column: t[parent_column]})
                    # print('object_exist =', obj_exists ,'Writing data for Payee ', child_column, ' = ', t[parent_column])
                        
                print ("updated ",Child_table , "table")

            update_child_table('description', Payee, 'name')
            update_child_table('account_type', Account_type,'desc')
            update_child_table('account_name', Account_name,'desc')
            update_child_table('account_detail', Account_detail,'desc')

            message = "Data update is successful."
            response_data = {'message': message}
            return JsonResponse(response_data)

            message = "Data update is successful."
            
            return JsonResponse({'message': message})

        except json.JSONDecodeError:
            return JsonResponse({'message': "Invalid JSON data"}, status=400)
        
        except Exception as e:
            import traceback
            error_message = f"An error occurred: {str(e)}\n{traceback.format_exc()}"
            print(error_message)  # This will print to your server logs
            return JsonResponse({'message': error_message}, status=500)

    else:
        return JsonResponse({'message': "Invalid request method"}, status=405)


# @login_required
# @csrf_exempt
# def convert_moneydanceXX(request):
#     #for first time entering history data to database;
#     if request.method == 'GET':
#         return render(request, 'convert_moneydance.html', {'header': "Please check and submit"})
        
#     elif request.method == 'POST':
#         try:
#             csv_file = request.FILES.get('csvFile')
#             if not csv_file:
#                 return JsonResponse({'message': 'No file was uploaded.'}, status=400)
        
#             if csv_file.name != "Income and Expenses Detailed.csv":
#                 return JsonResponse({'message': 'Incorrect file. Please upload "Income and Expenses Detailed.csv"'}, status=400)
            
#             print (" csv file name =", csv_file) 
#             # csv_data = csv_file.read().decode('utf-8')
#             # csv_reader = csv.reader(io.StringIO(csv_data))
#             # source_file_path = '../md_project/data/Income and Expenses Detailed.csv'
#             print ("Start processing----------------------->")
#             today = date.today()
#             this_year = int(today.strftime("%Y"))
#             last_year = this_year - 1
#             print ('last year -> ', last_year)
#             print ("Start processing_2------------------------------------>")
#             csv_data = csv_file.read().decode('utf-8')
#             csv_file_like_object = io.StringIO(csv_data)

#             csv_reader = csv.reader(csv_file_like_object)
#             # with open(csv_file, 'r') as source_file:
#             #     csv_reader = csv.reader(source_file)
#             print ('***************source file loop******************')
#             i = 0
#             col0 = ""
#             col1 = ""
#             rep_contents = []
#             for csv_row in csv_reader:
#                 if (i >=4  and csv_row): 
#                     if (csv_row[0]):
#                         if (csv_row[0][0:3] == "   "):
#                             col1 = (csv_row[0][3:]).strip()
#                         else:
#                             col0 = csv_row[0]
#                     elif not(csv_row[1] and csv_row[2]):
#                         print ("***************in csv loop ******************")
#                     elif not(csv_row[0]):
                        
#                         date_object = datetime.strptime(csv_row[1], "%m/%d/%Y")
#                         # for moneydance old version

#                         # date_object = datetime.strptime(csv_row[1], '%d/%m/%Y')
#                         # for moneydance my version

#                         # Convert the datetime object to a string in the format YYYY-MM-DD
#                         formatted_date = date_object.strftime('%Y-%m-%d')
                        
#                         year = int(date_object.strftime("%Y"))
#                         # select only date from first day of last year until current date

#                         if (year >= 2013) : #********************************** on when first initial data
#                         #if (year >= last_year) :
#                             row = Transaction()
#                             row.group = col0
#                             row.category = col1
#                             row.date = formatted_date
#                             row.account = csv_row[2]
#                             row.description = csv_row[3]
#                             row.memo =  csv_row[4]
#                             row.amount = csv_row[5]
#                             rep_contents.append(row)  
#                             # print(rep_contents)                                
#                 i = i+1
                    
#             current_year = date.today().year
#             # Calculate the last year
#             last_year = current_year - 1
#             # Define the filter condition
            
#             filter_condition = {'date__gte': f'{last_year}-01-01', 'date__lt': f'{current_year}-12-31'}
#             # Delete rows only last year-01-01 to current year-12-31 and replace with data in rep_contents
            
#             #Transaction.objects.filter(**filter_condition).delete()        
#             Transaction.objects.all().delete()   #************************ON when first initial data                 
#             for transaction_data in rep_contents:
            
#                 account_type = ""
#                 account_name = ""
#                 account_detail = ""
#                 # split_text(transaction_data.account)
                
#                 t = transaction_data.account
#                 colon_count = transaction_data.account.count(":")
#                 if colon_count == 0:
#                     account_type = transaction_data.account
#                     account_name = "null"
#                     account_detail = "null"
#                 elif colon_count == 1:
#                     account_array = re.split(r':', t, maxsplit=1)
#                     account_type = account_array[0]
#                     account_name = account_array[1]
#                     account_detail = "null"
#                 elif colon_count == 2:
#                     account_array = re.split(r':', t, maxsplit=2)
#                     account_type = account_array[0]
#                     account_name = account_array[1]
#                     account_detail = account_array[2]                        
                
#                 # print (account_type,"  -->   ",account_name,"   --->>    ", account_details)
                
#                 # Create a Transaction object for each dictionary in rep_content
#                 transaction = Transaction(
#                 group=transaction_data.group,
#                 category=transaction_data.category,
#                 date=transaction_data.date,
#                 description=transaction_data.description,
#                 account=transaction_data.account,
#                 account_type=account_type,
#                 account_name=account_name,
#                 account_detail=account_detail,
#                 memo=transaction_data.memo,
#                 amount=transaction_data.amount)
                
#                 transaction.save()
#             print ("transaction table is updated")

#             records_to_delete = Category.objects.filter(group='')
#             # Delete the filtered records
#             records_to_delete.delete()

#             transactions = Transaction.objects.values('category', 'group').distinct()
#             for t in transactions:
#                 # Check if the category for this group already exists
#                 category_exists = Category.objects.filter(group=t['group'], category=t['category']).exists()
#                 if category_exists:
#                     pass
#                 else:
#                     # Create a new Category entry since it doesn't exist
#                     Category.objects.create(group=t['group'], category=t['category'])
#                     print('Writing data for group =', t['group'], ", category =", t['category'])
#             print("Updated category table")

#             def update_child_table(parent_column, Child_table, child_column):

#                 #clear existing rows in "Child_table" 
#                 Child_table.objects.all().delete()
                
#                 transactions = Transaction.objects.values(parent_column).distinct()
#                 print ("parent column = ", parent_column)
#                 print ("child table = ", Child_table)
#                 for t in transactions:
#                     # print (t[parent_column])
#                     obj_exists = Child_table.objects.filter(**{child_column: t[parent_column]}).exists()
#                     if obj_exists:
#                         pass
#                     else:
#                         Child_table.objects.create(**{child_column: t[parent_column]})
#                     # print('object_exist =', obj_exists ,'Writing data for Payee ', child_column, ' = ', t[parent_column])
                        
#                 print ("updated ",Child_table , "table")

#             update_child_table('description', Payee, 'name')
#             update_child_table('account_type', Account_type,'desc')
#             update_child_table('account_name', Account_name,'desc')
#             update_child_table('account_detail', Account_detail,'desc')

#             message = "Data update is successful."
#             response_data = {'message': message}
#             return JsonResponse(response_data)

#             message = "Data update is successful."
            
#             return JsonResponse({'message': message})

#         except json.JSONDecodeError:
#             return JsonResponse({'message': "Invalid JSON data"}, status=400)
        
#         except Exception as e:
#             import traceback
#             error_message = f"An error() occurred: {str(e)}\n{traceback.format_exc()}"
#             print(error_message)  # This will print to your server logs
#             return JsonResponse({'message': error_message}, status=500)

#     else:
#         return JsonResponse({'message': "Invalid request method"}, status=405)

