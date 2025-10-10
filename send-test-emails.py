#!/usr/bin/env python3
"""
Send test emails from mypandapoints.com and pandaadmin.com systems
"""

import boto3
from datetime import datetime

# Initialize SES
ses = boto3.client('ses', region_name='us-east-2')

def send_test_points_notification():
    """Test email for mypandapoints.com - Points Award Notification"""

    try:
        response = ses.send_email(
            Source='noreply@pandaexteriors.com',
            Destination={
                'ToAddresses': ['robwinters@pandaexteriors.com']
            },
            Message={
                'Subject': {
                    'Data': '🎉 TEST: You\'ve Earned Panda Points!',
                    'Charset': 'UTF-8'
                },
                'Body': {
                    'Html': {
                        'Data': f'''
                        <html>
                        <head>
                            <style>
                                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                                .header {{ background: linear-gradient(135deg, #ffc107 0%, #ff9800 100%);
                                          color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                                .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }}
                                .points-box {{ background: white; padding: 20px; border-radius: 8px;
                                              text-align: center; margin: 20px 0; border: 2px solid #ffc107; }}
                                .points-number {{ font-size: 48px; font-weight: bold; color: #ffc107; }}
                                .button {{ display: inline-block; background: #ffc107; color: white;
                                          padding: 12px 30px; text-decoration: none; border-radius: 5px;
                                          font-weight: bold; margin: 20px 0; }}
                            </style>
                        </head>
                        <body>
                            <div class="container">
                                <div class="header">
                                    <h1>🎉 TEST EMAIL - Panda Points Awarded!</h1>
                                </div>
                                <div class="content">
                                    <p>Hi Test User,</p>

                                    <p>This is a <strong>TEST EMAIL</strong> from the mypandapoints.com system.</p>

                                    <div class="points-box">
                                        <div class="points-number">+50</div>
                                        <p style="margin: 0; color: #666;">Panda Points</p>
                                    </div>

                                    <p><strong>Awarded by:</strong> System Administrator</p>
                                    <p><strong>Reason:</strong> Email system test</p>
                                    <p><strong>Date:</strong> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>

                                    <center>
                                        <a href="https://mypandapoints.com" class="button">
                                            View Your Points Dashboard →
                                        </a>
                                    </center>

                                    <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">

                                    <p style="font-size: 12px; color: #666;">
                                        This is a test email from My Panda Points employee recognition system.<br>
                                        Questions? Contact your supervisor or HR department.
                                    </p>
                                </div>
                            </div>
                        </body>
                        </html>
                        ''',
                        'Charset': 'UTF-8'
                    }
                }
            }
        )
        print("✅ TEST: Points notification email sent successfully!")
        print(f"   Message ID: {response['MessageId']}")
        return True
    except Exception as e:
        print(f"❌ Failed to send points notification email: {e}")
        return False


def send_test_termination_refund_email():
    """Test email for pandaadmin.com - Termination Refund Notification"""

    recipients = [
        'robwinters@pandaexteriors.com',
        'valerieliebno@pandaexteriors.com',
        'madeleineferrerosa@pandaexteriors.com',
        'sheenakurian@pandaexteriors.com'
    ]

    try:
        response = ses.send_email(
            Source='noreply@pandaexteriors.com',
            Destination={
                'ToAddresses': recipients
            },
            Message={
                'Subject': {
                    'Data': '🔔 TEST: Employee Termination - Merchandise Refund Required',
                    'Charset': 'UTF-8'
                },
                'Body': {
                    'Html': {
                        'Data': f'''
                        <html>
                        <head>
                            <style>
                                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                                .header {{ background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
                                          color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                                .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }}
                                .alert-box {{ background: #fff3cd; border-left: 4px solid #ffc107;
                                             padding: 15px; margin: 20px 0; border-radius: 4px; }}
                                .info-row {{ margin: 10px 0; padding: 8px; background: white; border-radius: 4px; }}
                            </style>
                        </head>
                        <body>
                            <div class="container">
                                <div class="header">
                                    <h1>🔔 TEST EMAIL - Termination Refund Notice</h1>
                                </div>
                                <div class="content">
                                    <p>Hi Rob,</p>

                                    <p>This is a <strong>TEST EMAIL</strong> from the pandaadmin.com employee management system.</p>

                                    <div class="alert-box">
                                        <strong>⚠️ Action Required:</strong> Employee terminated within 90 days with outstanding merchandise
                                    </div>

                                    <h3>Employee Details:</h3>
                                    <div class="info-row">
                                        <strong>Name:</strong> Test Employee
                                    </div>
                                    <div class="info-row">
                                        <strong>Employee ID:</strong> TEST-001
                                    </div>
                                    <div class="info-row">
                                        <strong>Hire Date:</strong> {datetime.now().strftime('%B %d, %Y')}
                                    </div>
                                    <div class="info-row">
                                        <strong>Termination Date:</strong> {datetime.now().strftime('%B %d, %Y')}
                                    </div>
                                    <div class="info-row">
                                        <strong>Days Employed:</strong> 45 days
                                    </div>
                                    <div class="info-row">
                                        <strong>Merchandise Value:</strong> $250.00
                                    </div>

                                    <p style="margin-top: 20px;">
                                        <strong>Next Steps:</strong><br>
                                        Per company policy, employees terminated within 90 days must refund the value of their merchandise.
                                        Please coordinate with payroll to process the merchandise refund.
                                    </p>

                                    <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">

                                    <p style="font-size: 12px; color: #666;">
                                        This is a test email from Panda Admin employee management system.<br>
                                        Sent: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
                                    </p>
                                </div>
                            </div>
                        </body>
                        </html>
                        ''',
                        'Charset': 'UTF-8'
                    }
                }
            }
        )
        print("✅ TEST: Termination refund email sent successfully!")
        print(f"   Message ID: {response['MessageId']}")
        return True
    except Exception as e:
        print(f"❌ Failed to send termination refund email: {e}")
        return False


def send_test_referral_notification():
    """Test email for referral system"""

    try:
        response = ses.send_email(
            Source='noreply@pandaexteriors.com',
            Destination={
                'ToAddresses': ['robwinters@pandaexteriors.com']
            },
            Message={
                'Subject': {
                    'Data': '🎯 TEST: Your Referral Just Earned You Points!',
                    'Charset': 'UTF-8'
                },
                'Body': {
                    'Html': {
                        'Data': f'''
                        <html>
                        <head>
                            <style>
                                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                                .header {{ background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
                                          color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                                .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }}
                                .success-box {{ background: #d4edda; border-left: 4px solid #28a745;
                                               padding: 15px; margin: 20px 0; border-radius: 4px; }}
                                .points-earned {{ font-size: 36px; font-weight: bold; color: #28a745;
                                                 text-align: center; margin: 20px 0; }}
                            </style>
                        </head>
                        <body>
                            <div class="container">
                                <div class="header">
                                    <h1>🎯 TEST EMAIL - Referral Success!</h1>
                                </div>
                                <div class="content">
                                    <p>Hi Test User,</p>

                                    <p>This is a <strong>TEST EMAIL</strong> from the referral rewards system.</p>

                                    <div class="success-box">
                                        <strong>✅ Great news!</strong> Your referral has reached a milestone!
                                    </div>

                                    <p><strong>Candidate:</strong> John Doe</p>
                                    <p><strong>Milestone:</strong> Phone Screening Completed</p>

                                    <div class="points-earned">
                                        +25 Panda Points
                                    </div>

                                    <p style="text-align: center; color: #666;">
                                        Keep referring great candidates to earn more rewards!
                                    </p>

                                    <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">

                                    <p style="font-size: 12px; color: #666;">
                                        This is a test email from the Panda Referral Program.<br>
                                        Sent: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
                                    </p>
                                </div>
                            </div>
                        </body>
                        </html>
                        ''',
                        'Charset': 'UTF-8'
                    }
                }
            }
        )
        print("✅ TEST: Referral notification email sent successfully!")
        print(f"   Message ID: {response['MessageId']}")
        return True
    except Exception as e:
        print(f"❌ Failed to send referral notification email: {e}")
        return False


if __name__ == '__main__':
    print("=" * 60)
    print("SENDING TEST EMAILS")
    print("=" * 60)
    print(f"Recipient: robwinters@pandaexteriors.com")
    print(f"Sender: noreply@pandaexteriors.com")
    print(f"Time: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
    print("=" * 60)
    print()

    # Send all test emails
    print("1. Sending mypandapoints.com Points Award email...")
    send_test_points_notification()
    print()

    print("2. Sending pandaadmin.com Termination Refund email...")
    send_test_termination_refund_email()
    print()

    print("3. Sending Referral Success email...")
    send_test_referral_notification()
    print()

    print("=" * 60)
    print("✅ All test emails sent!")
    print("Check robwinters@pandaexteriors.com inbox")
    print("=" * 60)
