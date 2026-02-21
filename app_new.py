import json
import codecs
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from sqlalchemy.exc import OperationalError
from sqlalchemy import text
import pandas as pd
import io    

app = Flask(__name__)
app.secret_key = "secret_key_1"

dbname = 'postgres'
user = 'Prowentech'
password = 'Prowentech*1712'
host = 'hotel-analytics-us.ctqoeusy8cuj.us-east-1.rds.amazonaws.com'
port = '5432'

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{user}:{password}@{host}:{port}/{dbname}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

try:
    with app.app_context():
        db.session.execute(text("SELECT 1"))
        print("✅ Database connection successful!")
except OperationalError as e:
    print("❌ Database connection failed!")
    print(e)

ACCESS_TOKEN = 'EAAOiBKgZB5skBQ1yHjoRhWvs2tXOWRlB2pZCph5x8CQ3VZAOCkHWZCWmc6QdCB2AmJwI88Nz5i0XhyeHa2RLUp62N15t1XeitBvmjb7PX9bugPV4qvTHDBFLLu94AVDdszoSlW0nvFZAXt5MrXj91FQoqA5nx2PFad9dxMooChatfzqnK7pWXpAzGZC8uZAbMIUaD5oukGzZCSdNHkHfSm3GvPFgafheZAhF6r4Ql0kQZAM1WKiBNWslPtXZCpmqmAGU2n7P37VPnxdjciHLrGYZCW2qqZCas'
PHONE_NUMBER_ID = '987494121114718'
VERIFY_TOKEN = 'prowen_secret_key'
TEMPLATE_NAMES = ['hotel_pricing_insights_trial']

progress_status = {
    "total": 0,
    "sent": 0,
    "completed": False
}

# User model
class User(db.Model):
    __tablename__ = 'users'
    __table_args__ = {'schema':'watzap'}
    uid = db.Column(db.BigInteger, primary_key=True)
    user_name = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)

# Login page
@app.route("/", methods=["GET"])
def login_page():
    return render_template("login.html")

# Login endpoint
@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        print(data)
        user_name = data.get('user_name', '').strip()
        print("user :",user_name)
        password = data.get('password', '').strip()
        print("password :",password)
        user = User.query.filter_by(user_name=user_name).first()
        print("USER :",user)
        # if user and check_password_hash(user.password, password):
        if str(user.password) == password:
            session['user_id'] = user.uid
            return jsonify({"message": "Login successful"}), 200

        return jsonify({"message": "Invalid credentials"}), 401
    except Exception as e:
        print(e)
        print(e.__traceback__.tb_lineno)
        
# WhatsApp form page
@app.route("/form", methods=["GET"])
def form():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template("form.html",template_names=TEMPLATE_NAMES)


import psycopg2
import time
def get_db_connection():
    # Retrieve credentials from environment variables for security
    conn = psycopg2.connect(
        host='hotel-analytics-us.ctqoeusy8cuj.us-east-1.rds.amazonaws.com',
        database='postgres',
        user="Prowentech",
        password="Prowentech*1712"
    )
    return conn

@app.route("/start_sending", methods=["POST"])
def start_sending():

    data = request.get_json()
    selected_template = data.get("template")
    status = data.get("status")

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT name, mobile 
        FROM watzap.hotel_watzap_input 
        WHERE status_code = %s
    """, (status,))

    rows = cur.fetchall()

    for name, mobile in rows:

        if not mobile.isdigit() or len(mobile) != 10:
            cur.execute(("UPDATE watzap.hotel_watzap_input SET status_code = 500 WHERE mobile = %s"), (mobile,))
            print("in digit condition")
            continue

        json_data = {
            "messaging_product": "whatsapp",
            "to": f"91{mobile}",
            "type": "template",
            "template": {
                "name": selected_template,
                "language": {
                    "code": "en"
                },
                "components": [
                    {
                        "type": "header",
                        "parameters": [
                            {
                                "type": "image",
                                "image": {
                                    "link": "https://mediaprobuzz.s3.us-east-1.amazonaws.com/PHA_promo.png"
                                }
                            }
                        ]
                    },
                    {
                        "type": "body",
                        "parameters": [
                            {
                                "type": "text",
                                "text": name  # {{1}} - recipient name
                            }
                        ]
                    },
                ]
            }
        }

        url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }

        res = requests.post(url, headers=headers, json=json_data)
        print(res)
        print(res.text)
        if res.status_code == 200:
            cur.execute(("UPDATE watzap.hotel_watzap_input SET status_code = 200 WHERE mobile = %s"), (mobile,))
        else:
            cur.execute(("UPDATE watzap.hotel_watzap_input SET status_code = 400 WHERE mobile = %s"), (mobile,))

        conn.commit()

        progress_status["sent"] += 1

    progress_status["completed"] = True
    conn.close()

    return jsonify({"status": "started"})

def send_messages_background(selected_template, status):
    try:
        print("In send messages background")
        conn = get_db_connection()
        cur = conn.cursor()
        print("status :",status)
        cur.execute(
            "SELECT name, mobile FROM watzap.hotel_watzap_input WHERE status_code = %s;",
            (status,)
        )

        data = cur.fetchall()
        # print("data :",data)
        for name, mobile in data:
            print(name,mobile)
            if not mobile.isdigit() or len(mobile) != 10:
                cur.execute(("UPDATE watzap.hotel_watzap_input SET status_code = 500 WHERE mobile = %s"), (mobile,))
                print("in digit condition")
                continue

            json_data = {
                "messaging_product": "whatsapp",
                "to": f"91{mobile}",
                "type": "template",
                "template": {
                    "name": selected_template,
                    "language": {
                        "code": "en"
                    },
                    "components": [
                        {
                            "type": "header",
                            "parameters": [
                                {
                                    "type": "image",
                                    "image": {
                                        "link": "https://mediaprobuzz.s3.us-east-1.amazonaws.com/PHA_promo.png"
                                    }
                                }
                            ]
                        },
                        {
                            "type": "body",
                            "parameters": [
                                {
                                    "type": "text",
                                    "text": name  # {{1}} - recipient name
                                }
                            ]
                        },
                    ]
                }
            }

            url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
            headers = {
                "Authorization": f"Bearer {ACCESS_TOKEN}",
                "Content-Type": "application/json"
            }
            print(url)
            print(headers)

            res = requests.post(url, headers=headers, json=json_data)
            print("response :", res)
            print("res text :", res.text)
            if res.status_code == 200:
                cur.execute(("UPDATE watzap.hotel_watzap_input SET status_code = 200 WHERE mobile = %s"), (mobile,))
            else:
                cur.execute(("UPDATE watzap.hotel_watzap_input SET status_code = 400 WHERE mobile = %s"), (mobile,))

            conn.commit()
            time.sleep(1.5)

        conn.close()
        return "Success"

    except Exception as e:
        print("Error:", e)

@app.route("/progress")
def progress():
    return jsonify(progress_status)

@app.route("/processing", methods=["POST"])
def processing_page():

    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    selected_template = request.form.get("template")
    status = request.form.get("number_count")

    conn = get_db_connection()
    cur = conn.cursor()

    # Count total valid numbers
    cur.execute("""
        SELECT name, mobile 
        FROM watzap.hotel_watzap_input 
        WHERE status_code = %s
    """, (status,))

    data = cur.fetchall()

    valid_data = [
        (name, mobile)
        for name, mobile in data
        if mobile.isdigit() and len(mobile) == 10 and len(name) > 0
    ]

    progress_status["total"] = len(valid_data)
    progress_status["sent"] = 0
    progress_status["completed"] = False

    conn.close()

    return render_template(
        "processing.html",
        template=selected_template,
        status=status,
        total=len(valid_data)
    )


# WhatsApp message sending
@app.route("/send", methods=["POST"])
def send():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    recipient = request.form.get("phone")
    selected_template = request.form.get("template")
    print("number",recipient)
    if not recipient.isdigit() or len(recipient) != 10:
        return jsonify({"error": "Invalid 10-digit number"}), 400

    if selected_template not in TEMPLATE_NAMES:
        return jsonify({"error": "Invalid template selected"}), 400

    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    json_data = {
      "messaging_product": "whatsapp",
      "to": f"91{recipient}",
      "type": "template",
      "template": {
        "name": selected_template,
        "language": {
          "code": "en"
        },
        "components": [
          {
            "type": "header",
            "parameters": [
              {
                "type": "video",
                "video": {
                  "link": "https://mediaprobuzz.s3.us-east-1.amazonaws.com/Prowen+hotel+analytics+video.mp4"
                }
              }
            ]
          },
          {
            "type": "body",
            "parameters": [
              {
                "type": "text",
                "text": "Valued Hotelier"
              }
            ]
          }
        ]
      }
    }

    res = requests.post(url, headers=headers, json=json_data)
    if res.status_code == 200:
        return render_template("success.html", recipient=recipient)
    else:
        return f"<h3>Error {res.status_code}</h3><pre>{res.text}</pre>"

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login_page'))




# Webhook endpoint
@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    try:
        if request.method == "GET":
            mode = request.args.get("hub.mode")
            token = request.args.get("hub.verify_token")
            challenge = request.args.get("hub.challenge")
            print(challenge)
            if mode == "subscribe" and token == VERIFY_TOKEN:
                return challenge, 200
            return "Verification failed", 403

        elif request.method == "POST":
            data = request.get_json()
            print("Webhook received:", data)
            
            conn = get_db_connection()
            cur = conn.cursor()
            try:
                status = data["entry"][0]["changes"][0]["value"]["statuses"][0]["status"]
                number =  data["entry"][0]["changes"][0]["value"]["statuses"][0]["recipient_id"]
                
                cur.execute(("INSERT into watzap.hotel_webhook_insights(data,recipient_number,message_status) Values(%s,%s,%s)"),(json.dumps(data),number[2:],status))
                
                if status == 'sent':
                    cur.execute(("UPDATE watzap.hotel_watzap_input SET message_status = %s WHERE message_status = %s"),(200,number[2:]))
                elif status == 'failed':
                    cur.execute(("UPDATE watzap.hotel_watzap_input SET message_status = %s WHERE message_status = %s"),(400,number[2:]))

            except Exception as E:
                err = {E:E.__traceback__.tb_lineno}
                codecs.open("error_data.txt","w",encoding = "utf-8").write(str(data))
                codecs.open("error_file.txt","w",encoding = "utf-8").write(str(err))
                number =  data["entry"][0]["changes"][0]["value"]["messages"][0]["from"]
                status =  "reply"
                cur.execute(("INSERT into watzap.hotel_webhook_insights(data,recipient_number,message_status) Values(%s,%s,%s)"),(json.dumps(data),number[2:]),status)
                
            conn.commit()
            return "EVENT_RECEIVED", 200
    except Exception as E:
        print(E)
        print(E.__traceback__.tb_lineno)
        error = {E:E.__traceback__.tb_lineno}
        return str(error),400



@app.route("/messages", methods=["GET"])
def show_numbers():
    try:
        print("inside method")
        conn = get_db_connection()
        cur = conn.cursor()
        select = "select recipient_number from watzap.hotel_webhook_insights where recipient_number is NOT NULL"
        cur.execute(select)
        number_data = cur.fetchall()
        num_data = [t[0] for t in number_data]
        num_data = set(num_data)
        num_data = list(num_data)
    
        return render_template(
            "chat.html",
            chat_list=num_data
        )

    except Exception as E:
        print(E)
        print(E.__traceback__.tb_lineno)


        

import re
from datetime import datetime

def get_datetime(item):
    if "timestamp" in item:
        # Unix timestamp
        return datetime.fromtimestamp(item["timestamp"])
    elif "time" in item:
        # ISO formatted string
        return datetime.fromisoformat(item["time"])
    else:
        return datetime.min

def combine_and_sort_messages(client_messages, our_messages):
    try:
        # combined = client_messages + our_messages
        print("------------------------------------------------------")
        print(client_messages)
        print("------------------------------------------------------")
        for item in client_messages:
            epoch = int(item['time'])
            item['time'] = datetime.fromtimestamp(epoch).isoformat()
        combined = our_messages + client_messages
        print("combined---->",combined)
        # combined.sort(key=lambda x: datetime.fromisoformat(str(x["timestamp"])))
        combined.sort(key=get_datetime)
        print(combined)
        return combined
    except Exception as E:
        print(E)
        print(E.__traceback__.tb_lineno)



@app.route("/show_messages", methods=["POST"])
def show_messages():
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        js_data = request.get_json()
        recipient_number = js_data.get("recipient_number")
        print("Recipient:", recipient_number)


        messages = []

        # our_message = [{"text": "Okay! Thank You","time": "2025-05-07T01:38:01.209756","client":False},{"text":"Ok","time": "2025-05-09T03:26:01.209756","client":False}]
        
        query = """
            SELECT data
            FROM watzap.hotel_webhook_insights
            WHERE recipient_number = %s and template_name = 'reply' ORDER BY id
        """
        cur.execute(query, (recipient_number,))
        rows = cur.fetchall()

        for row in rows:
            # print("row ----------",row)
            payload = json.loads(row[0])
            # print("payload --------",payload)
            try:
                try:
                    text = payload["entry"][0]["changes"][0]["value"]["messages"][0]["text"]["body"]
                except:
                    text = ""
                try:
                    time_stamp = payload["entry"][0]["changes"][0]["value"]["messages"][0]["timestamp"]
                except:
                    time_stamp = ""
                messages.append({
                    "text": text,
                    "time":time_stamp,
                    "client":True
                })
            except Exception as E:
                print(E)
                print(E.__traceback__.tb_lineno)
                pass
        # print("Message list ----------",messages)
            
            
            
        query_ours = "SELECT data FROM watzap.test_webhook_insights_prowen WHERE recipient_number = %s ORDER BY id"
        cur.execute(query_ours,(recipient_number,))
        rows_ours = cur.fetchall()
        print("rows_ours :",rows_ours)
        
        our_message = [json.loads(i[0]) for i in rows_ours]
        print("------>",type(rows_ours))
        all_messages  = combine_and_sort_messages(messages, our_message)
        
        print(all_messages)

        return jsonify({
            "messages": all_messages
        })

    except Exception as e:
        print("ERROR:", e)
        print(e.__traceback__.tb_lineno)
        return jsonify({"messages": []}), 500
        
        
        
        
@app.route("/send/reply/messages", methods=["POST"])    
def send_reply_message():
    try:
        data = request.get_json()
        message = data.get("message")
        to_phone = data.get("to_phone")
        
        PHONE_NUMBER_ID = '562935203577701'

        payload = {
                    "messaging_product": "whatsapp",
                    "recipient_type": "individual",
                    "to": to_phone,
                    "type": "text",
                    "text": {
                        "preview_url": False,
                        "body": message
                    }
                }

        url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"

        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }

        res = requests.post(url, headers=headers, json=payload)
        print("response :",res.text)
        if int(res.status_code) == 200:
            data = {"text":message,"time":datetime.now().isoformat(),"client":False}
            conn = get_db_connection()
            cur = conn.cursor()
            query_insert = "INSERT into watzap.test_webhook_insights_prowen(data,recipient_number) VALUES(%s,%s)"
            cur.execute(query_insert,(json.dumps(data),to_phone))
            conn.commit()
            return jsonify({"messages": "success"}), 200
        else:
            jsonify({"error": "something went wrong"}), 400
    except Exception as E:
        print(E)
        print(E.__traceback__.tb_lineno)
        


if __name__ == "__main__":
    # app.run(host="0.0.0.0", port=5000, debug=True)
    app.run(debug=True)