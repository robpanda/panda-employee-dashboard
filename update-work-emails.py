import boto3
from decimal import Decimal

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
table = dynamodb.Table('panda-employees')

# Contact data with work emails
contacts = [
    ("Jason", "Daniel", "jasondaniel@pandaexteriors.com"),
    ("Scott", "Tucker", "scotttucker@panda-exteriors.com"),
    ("Cheyne", "Kilbourne", "cheynekilbourne@panda-exteriors.com"),
    ("Christian", "Curry", "cjcurry2@gmail.com"),
    ("Dan", "Atias", "danatias@panda-exteriors.com"),
    ("Anthony", "Samanoglu", "tsamanoglu@yahoo.com"),
    ("Thomas", "Hallwig", "tommyhallwig@pandaexteriors.com"),
    ("Matthew", "Sanborn", "matthewpsanborn@gmail.com"),
    ("Zachary", "Cecil", "zachcecil507@gmail.com"),
    ("Dani", "Lopes", "ninjadanny617@gmail.com"),
    ("Jason", "Wooten", "drjwoo88@gmail.com"),
    ("Jason", "San Martin-Torres", "jsanmartin88@live.com"),
    ("Trevor", "Johnson", "Trev2024@gmail.com"),
    ("Kyle", "Springsteen", "kspringteen15@gmail.com"),
    ("Josh", "Greer", "jgreer0505@yahoo.com"),
    ("Nick", "Hopkins", "Nickhopkins1@gmail.com"),
    ("Oscar", "Briceno", "oscarbriceno@pandaexteriors.com"),
    ("Valerie", "Liebno", "vliebno@outlook.com"),
    ("Sebastian", "LaRocca", "slarocca@pandaexteriors.com"),
    ("Daniel", "Hoover", "DanHoover1387@gmail.com"),
    ("Christopher", "Ayala Lovo", "cayala171@outlook.com"),
    ("Jimmy", "Coggin", "jimmycoggin.jc@gmail.com"),
    ("Jonathan", "Gonzalez Velasquez", "g.jonathan18@yahoo.com"),
    ("Dalton", "Dawson", "so.drohi@icloud.com"),
    ("Noah", "Ferguson", "noahf252@gmail.com"),
    ("Jessie", "Vigil", "yesseniavigil@gmail.com"),
    ("KJ", "Mitchell", "Kjmitchell434@gmail.com"),
    ("Austin", "Boyle", "austinboyle0@gmail.com"),
    ("J.", "Arpan", "Jarpan@pandaexteriors.com"),
    ("Matt", "Markey", "mattmarkey@pandaexteriors.com"),
    ("Diego", "Loor", "alexanderloor98@gmail.com"),
    ("Raymond", "Denisco", "raydenisco1245@gmail.com"),
    ("Sully", "Haschemi", "sullyhaschemi@pandaexteriors.com"),
    ("Fredy", "Constanza", "fredyconstanza03@gmail.com"),
    ("Idris", "Sesay", "Idrismsesay34@gmail.com"),
    ("Larry", "Walker", "lwalker2552@gmail.com"),
    ("Mike", "Stuart", "Michaelstuart12@gmail.com"),
    ("Santi", "Hancock", "Santisanguino222@gmail.com"),
    ("Kyle", "Kohli", "kylekohli83@gmail.com"),
    ("Sutton", "Gasper", "suttongasper@gmail.com"),
    ("Joe", "LaRose Jr", "joe.larose55@gmail.com"),
    ("Kingsley", "Jamaho", "murdaks@ymail.com"),
    ("Kaleb", "Lemaire", "kaleblemaire5@gmail.com"),
    ("Andreas", "Georgiou", "andreasg418@gmail.com"),
    ("Bryan", "Abel", "Babel462@gmail.com"),
    ("Kevin", "James", "Doleysunami@gmail.com"),
    ("Samuel", "Smith", "Samuelwsmith94@gmail.com"),
    ("Joseph", "Cistulli", "joe.cistulli93@gmail.com"),
    ("Luis", "Canda", "LuisCanda@iCloud.com"),
    ("Alyssa", "Provinzano", "amprovinzano@gmail.com"),
    ("Richard", "Palmer", "rpalmer1050@gmail.com"),
    ("Taj", "Diggs", "DiggsTaj90@gmail.com"),
    ("William", "Milburn", "wtmilburn@gmail.com"),
    ("Bryon", "Holmes", "bholmes8812678129@gmail.com"),
    ("Aliaksandra", "Yuralevich", "yaliaksandra@yahoo.com"),
    ("Matthew", "Coyle", "mcoyle7777@gmail.com"),
    ("Alix", "Cadet", "jaylion178@gmail.com"),
    ("Kevin", "Flores", "kevinflores007@hotmail.com"),
    ("Manuel", "Garcia", "m.garcia91340@gmail.com"),
    ("Dakota", "Oyuela", "Dakota.oyuela@yahoo.com"),
    ("Luciano", "Dibari", "Dibariluciano@yahoo.com"),
    ("Cael", "Moyer", "coolcael40@gmail.com"),
    ("Eric", "Olson", "eolson1488@gmail.com"),
    ("Troy", "Knight", "tknight202@gmail.com"),
    ("Sergio", "Muniz III", "Munizs1998@gmail.com"),
    ("Cristel", "Gutierrez", "cristelgutierrez2014@yahoo.com"),
    ("Miguel", "Duran Diaz", "migueldd1120@gmail.com"),
    ("Tommy", "Gooden", "tommygooden9@gmail.com"),
    ("Andrew", "Loughridge", "AndrewL2288@Hotmail.com"),
    ("Chris", "Atkinson", "swaulleto@gmail.com"),
    ("Amedeo", "Citro", "citroamedeo9@gmail.com"),
    ("Joshua", "Konstandinidis", "jkonstandinidis@gmail.com"),
    ("Shaye", "Jones", "shayejones44@gmail.com"),
    ("Bryan", "Andrade", "bryan.andrade112502@gmail.com"),
    ("Blair", "Shepherd", "blairashepherd@gmail.com"),
    ("Jessica", "Nurse", "Jesnre23@gmail.com"),
    ("Pluto", "Snow", "Dantedjs0119@gmail.com"),
    ("Colin", "Yost", "colin.yoster@gmail.com"),
    ("Victor", "Marquina JR", "victorvm0503@gmail.com"),
    ("Edward", "Whelan", "Edwardfwhelan5@gmail.com"),
    ("Madeleine", "Ferrerosa", "madeleinefduenas@gmail.com"),
    ("Peter", "Coker", "peterdcoker13@gmail.com"),
    ("Sheraton", "Gbeen", "sheratongbeen@icloud.com"),
    ("Chad", "Matthew", "chadgmatthew@gmail.com"),
    ("Scott", "Rayner Jr", "srayner15@gmail.com"),
    ("Danielle", "Withee", "danielle_withee@yahoo.com"),
    ("Christopher", "Hatcher", "chris@topadjuster.com"),
    ("David", "McCorkle Jr", "djstump1205@yahoo.com"),
    ("Nand", "Patel", "nand794@gmail.com"),
    ("Julian", "Todd", "jm.todd818@gmail.com"),
    ("Michael", "Detharidge", "detharidge86@gmail.com"),
    ("Sheena", "Kurian", "sheenakurian1206@gmail.com"),
    ("Nicholas", "Gessler", "nick.gessler@gmail.com"),
    ("Marshall", "Brown", "Marshallbrownjr2426@gmail.com"),
    ("Todd", "Sandberg", "sandberg.todd.d@gmail.com"),
    ("Ethan", "Edmond", "ethan2edmond04@gmail.com"),
    ("Bryan", "Ridinger", "bryanridinger326@gmail.com"),
    ("Antoine", "Wissmann", "Antoine.Wissmann@gmail.com"),
    ("Mark", "Rogers", "Mrogers21521@gmail.com"),
    ("Camila", "Arango", "camiaran358@gmail.com"),
    ("Rob", "Winters", "robwinters@pandaexteriors.com"),
    ("Jasmine", "Bannister", "jasminebannister@pandaexteriors.com"),
    ("Jared", "Queen", "jaredqueen@pandaexteriors.com"),
    ("Joshua", "Littleton", "joshualittleton@pandaexteriors.com"),
    ("KJ", "Mitchell", "kjmitchell@pandaexteriors.com"),
    ("Matt", "Faus", "mattfaus@pandaexteriors.com"),
    ("Hunter", "Lee", "hunterlee@pandaexteriors.com"),
    ("Renee", "Scott", "reneescott@pandaexteriors.com"),
    ("Ryan", "Dunlap", "ryandunlap@pandaexteriors.com"),
    ("Spencer", "Auletto", "spencerauletto@pandaexteriors.com"),
    ("Brenden", "Porter", "brendenporter@pandaexteriors.com")
]

def update_work_emails():
    try:
        # Get all employees
        response = table.scan()
        employees = response['Items']
        
        updated_count = 0
        matched_count = 0
        
        print(f"Found {len(employees)} employees in database")
        print(f"Processing {len(contacts)} contacts...")
        
        for first_name, last_name, work_email in contacts:
            # Find matching employee by name
            matched_employee = None
            
            for employee in employees:
                emp_first = (employee.get('First Name', '') or employee.get('first_name', '')).strip()
                emp_last = (employee.get('Last Name', '') or employee.get('last_name', '')).strip()
                
                # Handle name variations
                first_match = (
                    emp_first.lower() == first_name.lower() or
                    emp_first.lower() == first_name.lower().replace('.', '') or
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
                    print(f"✓ Matched: {first_name} {last_name} -> {emp_first} {emp_last}")
                    break
            
            if matched_employee:
                # Update work email if not already set
                current_work_email = matched_employee.get('Work Email', '') or matched_employee.get('work_email', '')
                
                if not current_work_email:
                    try:
                        table.update_item(
                            Key={'id': matched_employee['id']},
                            UpdateExpression='SET #we = :email, work_email = :email',
                            ExpressionAttributeNames={'#we': 'Work Email'},
                            ExpressionAttributeValues={':email': work_email}
                        )
                        updated_count += 1
                        print(f"  → Updated work email: {work_email}")
                    except Exception as e:
                        print(f"  ✗ Failed to update {first_name} {last_name}: {e}")
                else:
                    print(f"  - Already has work email: {current_work_email}")
            else:
                print(f"✗ No match found for: {first_name} {last_name}")
        
        print(f"\n📊 Summary:")
        print(f"   Contacts processed: {len(contacts)}")
        print(f"   Employees matched: {matched_count}")
        print(f"   Work emails updated: {updated_count}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    update_work_emails()