#app.py
from flask import Flask, render_template, request, redirect, url_for, flash
import os, csv, time
from werkzeug.utils import secure_filename
from bot.sender import send_all

app = Flask(__name__)
app.secret_key = 'supersecretkey'

BASE_DIR = os.path.dirname(__file__)
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
CSV_FOLDER = os.path.join(UPLOAD_FOLDER, 'csv')
MEDIA_FOLDER = os.path.join(UPLOAD_FOLDER, 'media')

os.makedirs(CSV_FOLDER, exist_ok=True)
os.makedirs(MEDIA_FOLDER, exist_ok=True)

contacts = []
media_file_path = None
report_lines = []

@app.route('/')
def index():
    return render_template('dashboard.html', contacts=contacts, media=media_file_path, report="\n".join(report_lines))

@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    global contacts
    file = request.files.get('csv_file')
    if file and file.filename.endswith('.csv'):
        filename = secure_filename(file.filename)
        filepath = os.path.join(CSV_FOLDER, filename)
        file.save(filepath)

        contacts = []
        with open(filepath, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row.get('name', '').strip()
                number = row.get('number', '').strip()
                if number.startswith('0'):
                    number = '+92' + number[1:]
                elif not number.startswith('+'):
                    number = '+92' + number
                contacts.append({'name': name, 'number': number})
        flash(f"{len(contacts)} contacts loaded.")
    else:
        flash("CSV file is invalid.")
    return redirect(url_for('index'))

@app.route('/upload_media', methods=['POST'])
def upload_media():
    global media_file_path
    file = request.files.get('media_file')
    if file:
        filename = secure_filename(file.filename)
        path = os.path.join(MEDIA_FOLDER, filename)
        file.save(path)
        media_file_path = path
        flash("Media uploaded.")
    return redirect(url_for('index'))

@app.route('/send_messages', methods=['POST'])
def send_messages():
    global report_lines
    message = request.form.get('message')
    keyword = request.form.get('keyword', '').lower()
    selected_numbers = request.form.getlist('selected_contacts')

    filtered_contacts = []
    for c in contacts:
        if keyword and keyword not in c['name'].lower():
            continue
        if c['number'] in selected_numbers:
            filtered_contacts.append(c)

    if not filtered_contacts:
        flash("No contacts matched for sending.")
        return redirect(url_for('index'))

    from bot.driver import setup_browser
    from selenium.webdriver.common.by import By
    driver = setup_browser()

    sent_count = 0
    report_lines = []

    for i, contact in enumerate(filtered_contacts):
        try:
            number = contact['number']
            name = contact['name']
            search_url = f"https://web.whatsapp.com/send?phone={number}&text={message}"
            driver.get(search_url)
            time.sleep(10)
            send_btn = driver.find_element(By.XPATH, '//button[@aria-label="Send"]')
            send_btn.click()
            report_lines.append(f"✅ Sent to {name} ({number})")
        except Exception as e:
            report_lines.append(f"❌ Failed for {contact['number']}: {str(e)}")
        sent_count += 1
        if sent_count % 5 == 0:
            time.sleep(120)
        if sent_count % 250 == 0:
            time.sleep(3600)

    flash(f"{sent_count} messages processed.")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
