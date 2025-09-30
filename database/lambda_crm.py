import json
import boto3
import pymysql
import os
from datetime import datetime, date
import uuid

# Database connection
def get_db_connection():
    return pymysql.connect(
        host=os.environ['DB_HOST'],
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD'],
        database=os.environ['DB_NAME'],
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

def lambda_handler(event, context):
    method = event['httpMethod']
    path = event['path']
    
    try:
        if path == '/contacts':
            if method == 'GET':
                return get_contacts(event)
            elif method == 'POST':
                return create_contact(event)
        elif path == '/contacts/export':
            return export_contacts()
        elif path == '/collections':
            if method == 'GET':
                return get_collections(event)
            elif method == 'POST':
                return create_collections(event)
        elif path == '/collections/counts':
            return get_collection_counts()
        elif path == '/campaigns':
            if method == 'POST':
                return create_campaign(event)
        
        return {
            'statusCode': 404,
            'body': json.dumps({'error': 'Not found'})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def get_contacts(event):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM contacts ORDER BY created_at DESC")
            contacts = cursor.fetchall()
            
            # Convert datetime objects to strings
            for contact in contacts:
                contact['created_at'] = contact['created_at'].isoformat()
                contact['updated_at'] = contact['updated_at'].isoformat()
                if contact['lists']:
                    contact['lists'] = json.loads(contact['lists'])
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps(contacts)
            }
    finally:
        conn.close()

def create_contact(event):
    data = json.loads(event['body'])
    conn = get_db_connection()
    
    try:
        with conn.cursor() as cursor:
            contact_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO contacts (id, name, email, phone, status, lists)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                contact_id,
                data['name'],
                data['email'],
                data.get('phone'),
                data.get('status', 'active'),
                json.dumps(data.get('lists', []))
            ))
            conn.commit()
            
            return {
                'statusCode': 201,
                'body': json.dumps({'id': contact_id, 'message': 'Contact created'})
            }
    finally:
        conn.close()

def get_collections(event):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM collections ORDER BY created_at DESC")
            collections = cursor.fetchall()
            
            for collection in collections:
                collection['created_at'] = collection['created_at'].isoformat()
                collection['updated_at'] = collection['updated_at'].isoformat()
                collection['install_date'] = collection['install_date'].isoformat()
                collection['amount'] = float(collection['amount'])
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps(collections)
            }
    finally:
        conn.close()

def create_collections(event):
    data = json.loads(event['body'])
    collections = data['collections']
    conn = get_db_connection()
    
    try:
        with conn.cursor() as cursor:
            for collection in collections:
                # Check if contact exists, create if not
                cursor.execute("SELECT id FROM contacts WHERE email = %s", (collection['email'],))
                contact = cursor.fetchone()
                
                if not contact:
                    contact_id = str(uuid.uuid4())
                    cursor.execute("""
                        INSERT INTO contacts (id, name, email, phone, status)
                        VALUES (%s, %s, %s, %s, 'active')
                    """, (contact_id, collection['name'], collection['email'], collection.get('phone')))
                else:
                    contact_id = contact['id']
                
                # Insert collection
                collection_id = str(uuid.uuid4())
                cursor.execute("""
                    INSERT INTO collections (id, contact_id, name, email, phone, amount, install_date, stage, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    collection_id,
                    contact_id,
                    collection['name'],
                    collection['email'],
                    collection.get('phone'),
                    collection['amount'],
                    collection['installDate'],
                    collection['stage'],
                    collection.get('status', 'active')
                ))
            
            conn.commit()
            
            return {
                'statusCode': 201,
                'body': json.dumps({'message': f'{len(collections)} collections created'})
            }
    finally:
        conn.close()

def get_collection_counts():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT stage, COUNT(*) as count 
                FROM collections 
                WHERE status = 'active'
                GROUP BY stage
            """)
            results = cursor.fetchall()
            
            counts = {
                '0-30': 0,
                '31-60': 0,
                '61-90': 0,
                '91-plus': 0,
                'judgment': 0,
                'resolved': 0
            }
            
            for result in results:
                counts[result['stage']] = result['count']
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps(counts)
            }
    finally:
        conn.close()

def create_campaign(event):
    data = json.loads(event['body'])
    conn = get_db_connection()
    
    try:
        with conn.cursor() as cursor:
            campaign_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO campaigns (id, name, type, stage, schedule, status)
                VALUES (%s, %s, %s, %s, %s, 'active')
            """, (
                campaign_id,
                f"{data['type'].title()} Campaign - {data['stage']}",
                data['type'],
                data['stage'],
                json.dumps(data['schedule'])
            ))
            conn.commit()
            
            return {
                'statusCode': 201,
                'body': json.dumps({'id': campaign_id, 'message': 'Campaign created'})
            }
    finally:
        conn.close()

def export_contacts():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT name, email, phone, status FROM contacts")
            contacts = cursor.fetchall()
            
            # Convert to CSV format
            csv_data = "Name,Email,Phone,Status\n"
            for contact in contacts:
                csv_data += f"{contact['name']},{contact['email']},{contact['phone'] or ''},{contact['status']}\n"
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'text/csv',
                    'Content-Disposition': 'attachment; filename=contacts.csv'
                },
                'body': csv_data
            }
    finally:
        conn.close()