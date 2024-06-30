import logging
import azure.functions as func
import psycopg2
import os
from datetime import datetime
from azure.communication.email import EmailClient

def main(msg: func.ServiceBusMessage):

    notification_id = int(msg.get_body().decode('utf-8'))
    logging.info('Python ServiceBus queue trigger processed message: %s',notification_id)

    conn = psycopg2.connect(user="thachhq",
                                    password="Hqt@2024",
                                    host="thachhqpostgre.postgres.database.azure.com",
                                    port="5432",
                                    database="techconfdb")
    cursor = conn.cursor()

    try:
        # TODO: Get notification message and subject from database using the notification_id
        notification_query = '''SELECT subject, message 
                                FROM notification
                                WHERE id = %s;'''
        cursor.execute(notification_query, (notification_id,))

        # TODO: Get attendees email and name
        notification = cursor.fetchone()
        subject = notification[0]
        message = notification[1]

        # TODO: Loop through each attendee and send an email with a personalized subject
        attendees_query = 'SELECT first_name, email FROM attendee;'
        cursor.execute(attendees_query)
        attendees = cursor.fetchall() 
        for attendee in attendees:
            first_name = attendee[0]
            email = attendee[1]
            send_email(email, subject, message, first_name)

        # TODO: Update the notification table by setting the completed date and updating the status with the total number of attendees notified
        completed_date = datetime.utcnow()
        status = 'Notified {} attendees'.format(len(attendees))
        
        notification_update_query = '''UPDATE notification 
                                SET completed_date = %s, status = %s 
                                WHERE id = %s;'''
        
        cursor.execute(notification_update_query, (completed_date, status, notification_id))
        conn.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error)
        conn.rollback()
    finally:
        if conn:
            cursor.close()
            conn.close()

def send_email(email, subject, body, name):
    client = EmailClient.from_connection_string("endpoint=https://thachhqpro3communicationservice.asiapacific.communication.azure.com/;accesskey=6w0WDrt1ZSIOBQNf8I3fhAvT2QVhLpxtW7lnQB3icj8ruopV9yLaJQQJ99AFACULyCpPDBwgAAAAAZCSE44X")

    sender_address ="DoNotReply@0e70ca2f-308f-453a-a8ae-72da69200d4a.azurecomm.net"
    recipient_address = "thachhq@fpt.com"

    email_message = {
        "subject": subject,
        "plainText": body
    }

    email_to = [{
        "address": recipient_address,
        "displayName": name
    }]

    email_content = {
        "senderAddress": sender_address,
        "recipients": {
            "to": email_to,
        },
        "content": email_message
    }

    try:
        poller = client.begin_send(email_content)
        result = poller.result()
        if result:
            print(f"Email sent with ID: {result['id']}")
        else:
            print("Error sending email: result is None")
    except Exception as ex:
        print(f"Error sending email: {str(ex)}")


