import boto3
from decimal import Decimal

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
table = dynamodb.Table('panda-employees')

# Merchandise value data from the spreadsheet
merchandise_values = [
    ("Jason", "Daniel", "jasondaniel@pandaexteriors.com", "$135.01"),
    ("Scott", "Tucker", "scotttucker@panda-exteriors.com", "$45.00"),
    ("Cheyne", "Kilbourne", "cheynekilbourne@panda-exteriors.com", "$146.01"),
    ("Dan", "Atias", "danatias@panda-exteriors.com", "$45.00"),
    ("Zachary", "Cecil", "zachcecil507@gmail.com", "$0.00"),
    ("Dani", "Lopes", "ninjadanny617@gmail.com", "$90.01"),
    ("Jason", "Wooten", "drjwoo88@gmail.com", "$90.01"),
    ("Oscar", "Briceno", "oscarbriceno@pandaexteriors.com", "$45.00"),
    ("Valerie", "Liebno", "vliebno@outlook.com", "$45.00"),
    ("Sebastian", "LaRocca", "slarocca@pandaexteriors.com", "$73.50"),
    ("Jimmy", "Coggin", "jimmycoggin.jc@gmail.com", "$72.10"),
    ("Jonathan", "Gonzalez Velasquez", "g.jonathan18@yahoo.com", "$56.00"),
    ("Noah", "Ferguson", "noahf252@gmail.com", "$90.01"),
    ("Jessie", "Vigil", "yesseniavigil@gmail.com", "$45.00"),
    ("Diego", "Loor", "alexanderloor98@gmail.com", "$45.00"),
    ("Sully", "Haschemi", "sullyhaschemi@pandaexteriors.com", "$0.00"),
    ("Idris", "Sesay", "Idrismsesay34@gmail.com", "$45.00"),
    ("Larry", "Walker", "lwalker2552@gmail.com", "$0.00"),
    ("Santi", "Hancock", "Santisanguino222@gmail.com", "$161.00"),
    ("Kyle", "Kohli", "kylekohli83@gmail.com", "$90.01"),
    ("Kingsley", "Jamaho", "murdaks@ymail.com", "$45.00"),
    ("Andreas", "Georgiou", "andreasg418@gmail.com", "$135.01"),
    ("Bryan", "Abel", "Babel462@gmail.com", "$56.00"),
    ("Marc", "Robinson", "", "$0.00"),
    ("Brian", "Ayers", "", "$73.50"),
    ("Luis", "Canda", "LuisCanda@iCloud.com", "$33.60"),
    ("Richard", "Palmer", "rpalmer1050@gmail.com", "$0.00"),
    ("Taj", "Diggs", "DiggsTaj90@gmail.com", "$45.00"),
    ("Matthew", "Coyle", "mcoyle7777@gmail.com", "$45.00"),
    ("Manuel", "Garcia", "m.garcia91340@gmail.com", "$90.01"),
    ("Dakota", "Oyuela", "Dakota.oyuela@yahoo.com", "$0.00"),
    ("Troy", "Knight", "tknight202@gmail.com", "$56.00"),
    ("Sergio", "Muniz III", "Munizs1998@gmail.com", "$33.60"),
    ("Cristel", "Gutierrez", "cristelgutierrez2014@yahoo.com", "$123.20"),
    ("Jerron", "Johnson", "", "$90.01"),
    ("Andrew", "Loughridge", "AndrewL2288@Hotmail.com", "$45.00"),
    ("Chris", "Atkinson", "swaulleto@gmail.com", "$45.00"),
    ("Amedeo", "Citro", "citroamedeo9@gmail.com", "$180.01"),
    ("Joshua", "Konstandinidis", "jkonstandinidis@gmail.com", "$157.50"),
    ("Blair", "Shepherd", "blairashepherd@gmail.com", "$117.60"),
    ("Pluto", "Snow", "Dantedjs0119@gmail.com", "$146.01"),
    ("Colin", "Yost", "colin.yoster@gmail.com", "$90.01"),
    ("Victor", "Marquina JR", "victorvm0503@gmail.com", "$45.00"),
    ("Edward", "Whelan", "Edwardfwhelan5@gmail.com", "$0.00"),
    ("Madeleine", "Ferrerosa", "madeleinefduenas@gmail.com", "$0.00"),
    ("Chad", "Matthew", "chadgmatthew@gmail.com", "$90.01"),
    ("Scott", "Rayner Jr", "srayner15@gmail.com", "$45.00"),
    ("Danielle", "Withee", "danielle_withee@yahoo.com", "$90.01"),
    ("Nand", "Patel", "nand794@gmail.com", "$112.00"),
    ("Julian", "Todd", "jm.todd818@gmail.com", "$89.60"),
    ("Michael", "Detharidge", "detharidge86@gmail.com", "$101.00"),
    ("Sheena", "Kurian", "sheenakurian1206@gmail.com", "$56.00"),
    ("Nicholas", "Gessler", "nick.gessler@gmail.com", "$0.00"),
    ("Marshall", "Brown", "Marshallbrownjr2426@gmail.com", "$90.01"),
    ("Todd", "Sandberg", "sandberg.todd.d@gmail.com", "$101.00"),
    ("Ethan", "Edmond", "ethan2edmond04@gmail.com", "$90.01"),
    ("Bryan", "Ridinger", "bryanridinger326@gmail.com", "$0.00"),
    ("Antoine", "Wissmann", "Antoine.Wissmann@gmail.com", "$45.00"),
    ("Camila", "Arango", "camiaran358@gmail.com", "$45.00"),
    ("Daniel", "Awobaikun", "dawobaikun@yahoo.com", "$90.01"),
    ("Zak", "Driver", "zacharyndriver@gmail.com", "$90.01"),
    ("Dominic", "Gusler", "dominic.gusler@gmail.com", "$90.01"),
    ("Cameron", "McKeehan", "Cameron.mckeehan16@gmail.com", "$33.60"),
    ("David", "McGinnis", "jrmcginnis@me.com", "$45.00"),
    ("Caroline", "Gosse", "gossecschool@gmail.com", "$101.00"),
    ("Eric", "Kibler", "gatorraiders.edk@gmail.com", "$45.00"),
    ("Ryan", "Damalouji", "damalouji@yahoo.com", "$90.01"),
    ("James", "Kolf", "Jkolf123@gmail.com", "$112.00"),
    ("Pratik", "Patel", "pratikpatel1119@gmail.com", "$90.01"),
    ("Roland", "Doe", "doeroland80@gmail.com", "$90.01"),
    ("Orenthal", "Stumps", "olstumps23@yahoo.com", "$0.00"),
    ("Jacob", "Jett", "jaaacob228@gmail.com", "$56.00"),
    ("Phil", "Spurry", "phil13spurry@gmail.com", "$56.00"),
    ("Jake", "Dorman", "jake.dormantci@gmail.com", "$45.00"),
    ("Jared", "Queen", "jaredqueen123@gmail.com", "$89.60"),
    ("Rob", "Winters", "robwinters@pandaexteriors.com", "$90.01"),
    ("Ryan", "Dunlap", "ryan.juaquine.dunlap@gmail.com", ""),
    ("Tim", "Canty", "tcanty212@gmail.com", ""),
    ("Brendan", "Hamblin-Jeddry", "Hjbrendan@gmail.com", ""),
    ("Brian", "Clark", "bclark98@me.com", ""),
    ("Randi", "Kowalski", "kowalskirandi@gmail.com", ""),
    ("Yoel", "Rodriguez", "yoelr7875@gmail.com", ""),
    ("Ronald", "Wood", "skycam82@gmail.com", ""),
    ("Eddie", "Moore", "eddiemoore094@gmail.com", ""),
    ("Renee", "Scott", "reneescott@pandaexteriors.com", "")
]

def update_merchandise_values():
    try:
        # Get all employees
        response = table.scan()
        employees = response['Items']
        
        updated_count = 0
        matched_count = 0
        
        print(f"Found {len(employees)} employees in database")
        print(f"Processing {len(merchandise_values)} merchandise value records...")
        
        for first_name, last_name, email, value in merchandise_values:
            # Skip empty values
            if not value or value == "":
                continue
                
            # Clean up value (remove $ and convert to decimal)
            clean_value = value.replace('$', '').replace(',', '')
            try:
                decimal_value = Decimal(clean_value)
            except:
                print(f"⚠️  Invalid value format: {value} for {first_name} {last_name}")
                continue
            
            # Find matching employee by email first, then by name
            matched_employee = None
            
            # Try email match first (if email provided)
            if email:
                for employee in employees:
                    emp_email = (employee.get('Email', '') or employee.get('email', '')).strip().lower()
                    work_email = (employee.get('Work Email', '') or employee.get('work_email', '')).strip().lower()
                    
                    if emp_email == email.lower() or work_email == email.lower():
                        matched_employee = employee
                        matched_count += 1
                        print(f"✓ Email matched: {email} -> {emp_email}")
                        break
            
            # If no email match, try name match
            if not matched_employee:
                for employee in employees:
                    emp_first = (employee.get('First Name', '') or employee.get('first_name', '')).strip()
                    emp_last = (employee.get('Last Name', '') or employee.get('last_name', '')).strip()
                    
                    first_match = (
                        emp_first.lower() == first_name.lower() or
                        first_name.lower() in emp_first.lower() or
                        emp_first.lower() in first_name.lower()
                    )
                    
                    last_match = (
                        emp_last.lower() == last_name.lower() or
                        last_name.lower() in emp_last.lower() or
                        emp_last.lower() in last_name.lower()
                    )
                    
                    if first_match and last_match:
                        matched_employee = employee
                        matched_count += 1
                        print(f"✓ Name matched: {first_name} {last_name} -> {emp_first} {emp_last}")
                        break
            
            if matched_employee:
                # Update merchandise value field
                try:
                    table.update_item(
                        Key={'id': matched_employee['id']},
                        UpdateExpression='SET merchandise_value = :value, #mv = :merch_value',
                        ExpressionAttributeNames={
                            '#mv': 'Merchandise Value'
                        },
                        ExpressionAttributeValues={
                            ':value': decimal_value,
                            ':merch_value': decimal_value
                        }
                    )
                    updated_count += 1
                    print(f"  → Updated merchandise value: ${decimal_value}")
                except Exception as e:
                    print(f"  ✗ Failed to update {first_name} {last_name}: {e}")
            else:
                print(f"✗ No match found for: {first_name} {last_name} ({email})")
        
        print(f"\n📊 Summary:")
        print(f"   Merchandise value records processed: {len([v for v in merchandise_values if v[3]])}")
        print(f"   Employees matched: {matched_count}")
        print(f"   Merchandise values updated: {updated_count}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    update_merchandise_values()