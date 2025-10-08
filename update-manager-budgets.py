import boto3
from decimal import Decimal

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
table = dynamodb.Table('panda-employees')

def update_manager_budgets():
    try:
        # List of all managers who should have 500 points quarterly budget
        managers = [
            'Abel, Bryan', 'Arpan, Justin', 'Ayers, Brian', 'Curry, Christian',
            'Daniel, Jason', 'Gasper, Sutton', 'Georgiou, Andrew', 'Gessler, Nicholas',
            'Hallwig, Thomas', 'John Smith', 'Johnson, Trevor', 'Kaswell, Mack',
            'Kilbourne, Cheyne', 'Konstandinidis, Joshua', 'LaRose Jr, Joseph',
            'Liebno, Valerie', 'Markey, Matthew', 'McGinnis, David', 'Palmer, Richard',
            'Provinzano, Alyssa', 'Sandberg, Todd', 'Tucker, Christopher',
            'Whelan, Edward', 'Wooten, Jason', 'Yuralevich, Aliaksandra'
        ]
        
        # Scan all employees to find managers
        response = table.scan()
        employees = response['Items']
        
        updated_count = 0
        
        for employee in employees:
            full_name = f"{employee.get('Last Name', '')}, {employee.get('First Name', '')}"
            
            if full_name in managers:
                # Update quarterly budget to 500 points
                table.update_item(
                    Key={'id': employee['id']},
                    UpdateExpression='SET quarterly_budget = :budget',
                    ExpressionAttributeValues={
                        ':budget': Decimal('500')
                    }
                )
                updated_count += 1
                print(f"Updated {full_name}: 500 points quarterly budget")
        
        print(f"\n✅ Successfully updated {updated_count} managers with 500 points quarterly budget")
        
    except Exception as e:
        print(f"❌ Error updating manager budgets: {str(e)}")

if __name__ == "__main__":
    update_manager_budgets()