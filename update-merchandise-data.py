import boto3
from decimal import Decimal

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
table = dynamodb.Table('panda-employees')

# Merchandise data from the spreadsheet
merchandise_data = [
    ("Jason", "Daniel", "jasondaniel@pandaexteriors.com", "GAF 2025 Polo - Black - Mens, GAF 2025 Polo - Green - Mens, GAF 2025 Polo - Navy Blue - Mens"),
    ("Scott", "Tucker", "scotttucker@panda-exteriors.com", "GAF 2025 Polo - Royal Blue - Mens"),
    ("Cheyne", "Kilbourne", "cheynekilbourne@panda-exteriors.com", "Adidas Quarter Zip Pullover - Mens - Red, GAF 2025 Polo - Green - Mens, GAF 2025 Polo - Orange - Mens"),
    ("Christian", "Curry", "cjcurry2@gmail.com", ""),
    ("Dan", "Atias", "danatias@panda-exteriors.com", "GAF 2025 Polo - Black - Mens"),
    ("Anthony", "Samanoglu", "tsamanoglu@yahoo.com", ""),
    ("Thomas", "Hallwig", "tommyhallwig@pandaexteriors.com", ""),
    ("Matthew", "Sanborn", "matthewpsanborn@gmail.com", ""),
    ("Zachary", "Cecil", "zachcecil507@gmail.com", "Baseball Hat - Charcoal"),
    ("Dani", "Lopes", "ninjadanny617@gmail.com", "GAF 2025 Polo - Black - Mens, GAF 2025 Polo - Navy Blue - Mens"),
    ("Jason", "Wooten", "drjwoo88@gmail.com", "GAF 2025 Polo - Navy Blue - Mens, GAF 2025 Polo - Periwinkle Blue - Mens"),
    ("Jason", "San Martin-Torres", "jsanmartin88@live.com", ""),
    ("Trevor", "Johnson", "Trev2024@gmail.com", ""),
    ("Kyle", "Springsteen", "kspringteen15@gmail.com", ""),
    ("Josh", "Greer", "jgreer0505@yahoo.com", ""),
    ("Nick", "Hopkins", "Nickhopkins1@gmail.com", ""),
    ("Oscar", "Briceno", "oscarbriceno@pandaexteriors.com", "GAF 2025 Polo - Black - Mens"),
    ("Valerie", "Liebno", "vliebno@outlook.com", "GAF 2025 Polo - Black - Womens"),
    ("Sebastian", "LaRocca", "slarocca@pandaexteriors.com", "Panda Core Hoodie - Black, Contractor Hoodie - Asphalt"),
    ("Daniel", "Hoover", "DanHoover1387@gmail.com", ""),
    ("Christopher", "Ayala Lovo", "cayala171@outlook.com", ""),
    ("Jimmy", "Coggin", "jimmycoggin.jc@gmail.com", "Premium Mens Hoodie - Coal, Label Beanie - Black"),
    ("Jonathan", "Gonzalez Velasquez", "g.jonathan18@yahoo.com", "Adidas Quarter Zip Pullover - Mens - Black"),
    ("Dalton", "Dawson", "so.drohi@icloud.com", ""),
    ("Noah", "Ferguson", "noahf252@gmail.com", "GAF 2025 Polo - Black - Mens, GAF 2025 Polo - Black - Mens"),
    ("Jessie", "Vigil", "yesseniavigil@gmail.com", "GAF 2025 Polo - Black - Womens"),
    ("KJ", "Mitchell", "Kjmitchell434@gmail.com", ""),
    ("Austin", "Boyle", "austinboyle0@gmail.com", ""),
    ("J.", "Arpan", "Jarpan@pandaexteriors.com", ""),
    ("Matt", "Markey", "mattmarkey@pandaexteriors.com", ""),
    ("Diego", "Loor", "alexanderloor98@gmail.com", "GAF 2025 Polo - Black - Mens"),
    ("Raymond", "Denisco", "raydenisco1245@gmail.com", ""),
    ("Sully", "Haschemi", "sullyhaschemi@pandaexteriors.com", "GAF Exterior Polo - Black, GAF Exterior Polo - Charcoal"),
    ("Fredy", "Constanza", "fredyconstanza03@gmail.com", ""),
    ("Idris", "Sesay", "Idrismsesay34@gmail.com", "GAF 2025 Polo - Black - Mens"),
    ("Larry", "Walker", "lwalker2552@gmail.com", "Adidas 1/4 Zip Pullover - Gray - XL"),
    ("Mike", "Stuart", "Michaelstuart12@gmail.com", ""),
    ("Santi", "Hancock", "Santisanguino222@gmail.com", "Premium Mens Hoodie - Coal, GAF Exterior Jacket - Black, Premium Mens Hoodie - Petrol"),
    ("Kyle", "Kohli", "kylekohli83@gmail.com", "GAF 2025 Polo - Black - Mens, GAF 2025 Polo - Navy Blue - Mens"),
    ("Sutton", "Gasper", "suttongasper@gmail.com", ""),
    ("Joe", "LaRose Jr", "joe.larose55@gmail.com", ""),
    ("Kingsley", "Jamaho", "murdaks@ymail.com", "GAF 2025 Polo - Black - Mens"),
    ("Kaleb", "Lemaire", "kaleblemaire5@gmail.com", ""),
    ("Andreas", "Georgiou", "andreasg418@gmail.com", "GAF 2025 Polo - Black - Mens, GAF 2025 Polo - Periwinkle Blue - Mens, GAF 2025 Polo - Red - Mens"),
    ("Bryan", "Abel", "Babel462@gmail.com", "Adidas Quarter Zip Pullover - Womens - Heather Royal Blue"),
    ("Kevin", "James", "Doleysunami@gmail.com", ""),
    ("Samuel", "Smith", "Samuelwsmith94@gmail.com", ""),
    ("Joseph", "Cistulli", "joe.cistulli93@gmail.com", ""),
    ("Luis", "Canda", "LuisCanda@iCloud.com", "GAF Exterior Polo - Navy, GAF Exterior Polo - Burgundy"),
    ("Alyssa", "Provinzano", "amprovinzano@gmail.com", ""),
    ("Richard", "Palmer", "rpalmer1050@gmail.com", "Adidas - 1/4 Zip Pullover - Light Gray - Size XL"),
    ("Taj", "Diggs", "DiggsTaj90@gmail.com", "GAF 2025 Polo - Black - Mens"),
    ("William", "Milburn", "wtmilburn@gmail.com", ""),
    ("Bryon", "Holmes", "bholmes8812678129@gmail.com", ""),
    ("Aliaksandra", "Yuralevich", "yaliaksandra@yahoo.com", ""),
    ("Matthew", "Coyle", "mcoyle7777@gmail.com", "GAF 2025 Polo - Black - Mens"),
    ("Alix", "Cadet", "jaylion178@gmail.com", ""),
    ("Kevin", "Flores", "kevinflores007@hotmail.com", ""),
    ("Manuel", "Garcia", "m.garcia91340@gmail.com", "GAF 2025 Polo - Royal Blue - Mens, GAF 2025 Polo - Orange - Mens"),
    ("Dakota", "Oyuela", "Dakota.oyuela@yahoo.com", "Tie dye onesies - Infants - 12 months"),
    ("Luciano", "Dibari", "Dibariluciano@yahoo.com", ""),
    ("Cael", "Moyer", "coolcael40@gmail.com", ""),
    ("Eric", "Olson", "eolson1488@gmail.com", ""),
    ("Troy", "Knight", "tknight202@gmail.com", "Adidas Quarter Zip Pullover - Mens - Black"),
    ("Sergio", "Muniz III", "Munizs1998@gmail.com", "GAF Exterior Polo - Burgundy"),
    ("Cristel", "Gutierrez", "cristelgutierrez2014@yahoo.com", "Adidas Quarter Zip Pullover - Mens - Black, GAF Solar Polo - Burgundy, GAF Solar Polo - Mint"),
    ("Miguel", "Duran Diaz", "migueldd1120@gmail.com", ""),
    ("Tommy", "Gooden", "tommygooden9@gmail.com", ""),
    ("Andrew", "Loughridge", "AndrewL2288@Hotmail.com", "GAF 2025 Polo - Black - Mens"),
    ("Chris", "Atkinson", "swaulleto@gmail.com", "GAF 2025 Polo - Navy Blue - Mens"),
    ("Amedeo", "Citro", "citroamedeo9@gmail.com", "GAF 2025 Polo - Black - Mens, GAF 2025 Polo - Black - Mens, GAF 2025 Polo - Navy Blue - Mens, GAF 2025 Polo - Navy Blue - Mens"),
    ("Joshua", "Konstandinidis", "jkonstandinidis@gmail.com", "Premium WOMENS Crewneck - Pink Haze, Premium Mens Hoodie - Walnut, Premium Mens Hoodie - Coal"),
    ("Shaye", "Jones", "shayejones44@gmail.com", ""),
    ("Bryan", "Andrade", "bryan.andrade112502@gmail.com", ""),
    ("Blair", "Shepherd", "blairashepherd@gmail.com", "GAF Exterior Polo - Burgundy, GAF Exterior Polo - Black, Panda Core Hoodie - Black, Panda Core Hoodie - Pink"),
    ("Jessica", "Nurse", "Jesnre23@gmail.com", ""),
    ("Pluto", "Snow", "Dantedjs0119@gmail.com", "Adidas Quarter Zip Pullover - Mens - Black, GAF 2025 Polo - Black - Mens, GAF 2025 Polo - Navy Blue - Mens"),
    ("Colin", "Yost", "colin.yoster@gmail.com", "GAF 2025 Polo - Black - Mens, GAF 2025 Polo - Navy Blue - Mens"),
    ("Victor", "Marquina JR", "victorvm0503@gmail.com", "GAF 2025 Polo - Black - Mens"),
    ("Edward", "Whelan", "Edwardfwhelan5@gmail.com", "GAF Exterior Polo - Charcoal, GAF Exterior Polo - Charcoal"),
    ("Madeleine", "Ferrerosa", "madeleinefduenas@gmail.com", "Adidas - Women's 1/4 Pullover - Heather Gray/Black - Size M"),
    ("Peter", "Coker", "peterdcoker13@gmail.com", ""),
    ("Sheraton", "Gbeen", "sheratongbeen@icloud.com", ""),
    ("Chad", "Matthew", "chadgmatthew@gmail.com", "GAF 2025 Polo - Black - Mens, GAF 2025 Polo - Navy Blue - Mens"),
    ("Scott", "Rayner Jr", "srayner15@gmail.com", "GAF 2025 Polo - Periwinkle Blue - Mens"),
    ("Danielle", "Withee", "danielle_withee@yahoo.com", "GAF 2025 Polo - Black - Womens, GAF 2025 Polo - Navy Blue - Womens"),
    ("Christopher", "Hatcher", "chris@topadjuster.com", ""),
    ("David", "McCorkle Jr", "djstump1205@yahoo.com", ""),
    ("Nand", "Patel", "nand794@gmail.com", "Adidas Quarter Zip Pullover - Mens - Black, Adidas Quarter Zip Pullover - Mens - Navy Blue"),
    ("Julian", "Todd", "jm.todd818@gmail.com", "Adidas Quarter Zip Pullover - Mens - Navy Blue, GAF Solar Polo - Charcoal"),
    ("Michael", "Detharidge", "detharidge86@gmail.com", "Adidas Quarter Zip Pullover - Mens - Black, GAF 2025 Polo - Navy Blue - Mens"),
    ("Sheena", "Kurian", "sheenakurian1206@gmail.com", "Adidas Quarter Zip Pullover - Womens - Heather Charcoal"),
    ("Nicholas", "Gessler", "nick.gessler@gmail.com", "GAF 2025 Polo - Black - Men"),
    ("Marshall", "Brown", "Marshallbrownjr2426@gmail.com", "GAF 2025 Polo - Black - Mens, GAF 2025 Polo - Navy Blue - Mens"),
    ("Todd", "Sandberg", "sandberg.todd.d@gmail.com", "GAF 2025 Polo - Navy Blue - Mens, Adidas Quarter Zip Pullover - Mens - Navy Blue"),
    ("Ethan", "Edmond", "ethan2edmond04@gmail.com", "GAF 2025 Polo - Black - Mens, GAF 2025 Polo - Navy Blue - Mens"),
    ("Bryan", "Ridinger", "bryanridinger326@gmail.com", "GAF 2025 Polo - Black - Men"),
    ("Antoine", "Wissmann", "Antoine.Wissmann@gmail.com", "GAF 2025 Polo - Navy Blue - Mens"),
    ("Mark", "Rogers", "Mrogers21521@gmail.com", ""),
    ("Camila", "Arango", "camiaran358@gmail.com", "GAF 2025 Polo - Navy Blue - Womens"),
    ("Rob", "Winters", "robwinters@pandaexteriors.com", "GAF 2025 Polo - Black - Mens,GAF 2025 Polo - Navy Blue - Mens"),
    ("Ryan", "Dunlap", "ryan.juaquine.dunlap@gmail.com", "GAF 2025 Polo - Black - Mens, GAF 2025 Polo - Navy - Mens"),
    ("Tim", "Canty", "tcanty212@gmail.com", "GAF 2025 Polo - Black - Mens, GAF 2025 Polo - Blue - Mens"),
    ("Brendan", "Hamblin-Jeddry", "Hjbrendan@gmail.com", "GAF 2025 Polo - Black - Mens, GAF 2025 Polo - Blue - Mens, GAF 2025 Polo - Black - Mens, GAF 2025 Polo - Blue - Mens"),
    ("Brian", "Clark", "bclark98@me.com", "GAF 2025 Polo - Black - Mens"),
    ("Randi", "Kowalski", "kowalskirandi@gmail.com", "GAF 2025 Polo - Navy Blue - Womens"),
    ("Yoel", "Rodriguez", "yoelr7875@gmail.com", "GAF 2025 Polo - Black - Mens, GAF 2025 Polo - Blue - Mens, GAF 2025 Polo - Black - Mens, GAF 2025 Polo - Blue - Mens"),
    ("Ronald", "Wood", "skycam82@gmail.com", "GAF 2025 Polo - Black - Mens"),
    ("Eddie", "Moore", "eddiemoore094@gmail.com", "GAF 2025 Polo - Black - Mens"),
    ("Renee", "Scott", "reneescott@pandaexteriors.com", "GAF 2025 Polo - Navy Blue - Womens")
]

def update_merchandise_data():
    try:
        # Get all employees
        response = table.scan()
        employees = response['Items']
        
        updated_count = 0
        matched_count = 0
        
        print(f"Found {len(employees)} employees in database")
        print(f"Processing {len(merchandise_data)} merchandise records...")
        
        for first_name, last_name, email, merchandise in merchandise_data:
            # Find matching employee by email first, then by name
            matched_employee = None
            
            # Try email match first
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
                # Update merchandise field
                try:
                    table.update_item(
                        Key={'id': matched_employee['id']},
                        UpdateExpression='SET merchandise_requested = :merch, #mr = :merch_req, #ms = :merch_sent',
                        ExpressionAttributeNames={
                            '#mr': 'Merch Requested',
                            '#ms': 'Merch Sent'
                        },
                        ExpressionAttributeValues={
                            ':merch': merchandise,
                            ':merch_req': merchandise,
                            ':merch_sent': 'Yes' if merchandise else 'No'
                        }
                    )
                    updated_count += 1
                    if merchandise:
                        print(f"  → Updated merchandise: {merchandise[:50]}{'...' if len(merchandise) > 50 else ''}")
                    else:
                        print(f"  → No merchandise requested")
                except Exception as e:
                    print(f"  ✗ Failed to update {first_name} {last_name}: {e}")
            else:
                print(f"✗ No match found for: {first_name} {last_name} ({email})")
        
        print(f"\n📊 Summary:")
        print(f"   Merchandise records processed: {len(merchandise_data)}")
        print(f"   Employees matched: {matched_count}")
        print(f"   Merchandise data updated: {updated_count}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    update_merchandise_data()