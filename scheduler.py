from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mail import Mail, Message
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Change this to a secure key
app.config['MAIL_SERVER'] = 'smtp.yourmailprovider.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'your_username'
app.config['MAIL_PASSWORD'] = 'your_password'

mail = Mail(app)

tasks = []


def send_email(subject, recipient, body):
    msg = Message(subject, recipients=[recipient], body=body)
    mail.send(msg)


def send_push_notification(token, message):
    # Implement push notification sending logic here
    pass


def schedule_notification(task):
    # You can customize this function to send notifications based on your requirements
    now = datetime.now()
    notification_time = task['datetime'] - timedelta(minutes=15)  # Send notification 15 minutes before the task
    if now < notification_time:
        time_difference = notification_time - now
        seconds_until_notification = time_difference.total_seconds()
        task['notification_timer'] = app.run_once(
            send_notification, seconds_until_notification, task=task
        )


def send_notification(task):
    if task['notification_type'] == 'email':
        send_email(f"Task Reminder: {task['title']}", task['recipient'], task['description'])
    elif task['notification_type'] == 'push':
        send_push_notification(task['push_token'], f"Task Reminder: {task['title']}")


def validate_task_form(form):
    if not form['title'] or not form['datetime'] or not form['notification_type']:
        return False
    return True


@app.route('/')
def index():
    return render_template('index.html', tasks=tasks)


@app.route('/add_task', methods=['POST'])
def add_task():
    form = request.form
    if validate_task_form(form):
        task = {
            'title': form['title'],
            'datetime': datetime.strptime(form['datetime'], '%Y-%m-%dT%H:%M'),
            'description': form['description'],
            'recipient': form['recipient'],
            'notification_type': form['notification_type'],
            'push_token': form['push_token'] if form['push_token'] else None,
            'notification_timer': None
        }

        tasks.append(task)
        schedule_notification(task)
        flash('Task added successfully', 'success')
    else:
        flash('Invalid task details', 'error')

    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
