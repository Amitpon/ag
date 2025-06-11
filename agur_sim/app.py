import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from collections import defaultdict
import seaborn as sns
from flask import Flask, render_template_string, request
import io
import base64

app = Flask(__name__)

# HTML Templates
form_template = '''
<!DOCTYPE html>
<html>
<head>
    <title>מודל סימולציה עגור</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f8f9fa; /* Very light background */
            color: #343a40; /* Darker text for better readability */
            display: flex;
            justify-content: center;
            align-items: flex-start; /* Align to start for better scrolling with more content */
            min-height: 100vh;
            margin: 0;
            padding: 120px; /* Even significantly larger padding around the body */
            box-sizing: border-box;
            direction: rtl; /* Right-to-left for Hebrew */
            text-align: right; /* Align text to the right */
        }
        .container {
            background-color: #ffffff;
            padding: 80px 100px; /* Increased padding inside the container */
            border-radius: 20px; /* More rounded corners */
            box-shadow: 0 12px 25px rgba(0, 0, 0, 0.2); /* Stronger and softer shadow */
            max-width: 1000px; /* Even wider container */
            width: 100%;
            box-sizing: border-box;
        }
        h2 {
            text-align: center;
            color: #003366; /* Even darker blue */
            margin-bottom: 60px; /* More space below heading */
            font-size: 2.8em; /* Larger main heading */
            font-weight: 600;
        }
        h3 {
            color: #004d99; /* Medium dark blue */
            border-bottom: 3px solid #004d99; /* Thicker border */
            padding-bottom: 12px;
            margin-top: 50px; /* More space above section headings */
            margin-bottom: 35px; /* More space below section headings */
            font-size: 2em;
            font-weight: 500;
        }
        h4 {
            color: #0066cc; /* Lighter blue for sub-headings */
            margin-top: 30px;
            margin-bottom: 20px;
            font-size: 1.5em;
            font-weight: 500;
        }
        .input-group {
            margin-bottom: 30px; /* More space between input groups */
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            justify-content: space-between; /* Distribute items with space in between */
            gap: 15px; /* Gap between items within the flex container */
        }
        .input-group label {
            width: 380px; /* Fixed width for labels */
            font-weight: bold;
            font-size: 1.25em; /* Larger label font */
            text-align: right;
            line-height: 1.5; /* Better line spacing for labels */
            white-space: nowrap; /* Prevent labels from wrapping */
            overflow: hidden; /* Hide overflow if text is too long */
            text-overflow: ellipsis; /* Add ellipsis if text is too long */
        }
        form input[type="text"], form input[type="number"], form select { /* Added form select */
            flex-grow: 1; /* Allow input to grow */
            max-width: 250px; /* Maximum width for input fields */
            padding: 18px; /* Larger input fields */
            border: 1px solid #99ccff; /* Softer blue, more prominent border */
            border-radius: 15px; /* More rounded input fields */
            min-width: 180px; /* Minimum width for input fields */
            font-size: 1.0em; /* Slightly smaller font to better fit placeholders */
            text-align: right;
            box-shadow: inset 0 1px 4px rgba(0, 0, 0, 0.1); /* Inner shadow for depth */
            direction: ltr; /* Ensure numbers and commas are LTR */
        }
        form input[type="submit"] {
            width: 100%;
            padding: 22px 35px; /* Even larger button */
            background-color: #28a745; /* Green */
            color: white;
            border: none;
            border-radius: 15px;
            cursor: pointer;
            font-size: 1.5em;
            margin-top: 60px; /* More space above button */
            transition: background-color 0.3s ease, transform 0.2s ease, box-shadow 0.3s ease;
            box-shadow: 0 5px 10px rgba(0, 0, 0, 0.15);
        }
        form input[type="submit"]:hover {
            background-color: #218838; /* Darker green on hover */
            transform: translateY(-4px); /* More pronounced lift on hover */
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>מודל סימולציית פעילויות עגור</h2>
        <form method="post">
            <div class="input-group">
                <label for="YEARS">שנים לסימולציה:</label>
                <input type="number" name="YEARS" value="3" placeholder="(משך הסימולציה הכולל בשנים)">
            </div>
            <div class="input-group">
                <label for="Drone_OP">רחפן (מבצעי) התחלתי:</label>
                <input type="number" name="Drone_OP" value="15" placeholder="(מספר הרחפנים המבצעיים בהתחלה)">
            </div>
            <div class="input-group">
                <label for="Drone_TR_PRO">רחפני אימון והכשרה התחלתיים:</label>
                <input type="number" name="Drone_TR_PRO" value="10" placeholder="(מספר רחפני אימון/הכשרה/עתודה בהתחלה)">
            </div>
            <div class="input-group">
                <label for="Agur">עגור התחלתי:</label>
                <input type="number" name="Agur" value="5" placeholder="(מספר כלי עגור התחלתיים)">
            </div>
            <div class="input-group">
                <label for="Sting">סטינג התחלתי:</label>
                <input type="number" name="Sting" value="0" placeholder="(מספר כלי סטינג התחלתיים)">
            </div>

            <h3>תוספת מלאי וקצב חידוש</h3>
            <div class="input-group">
                <label for="REPLENISH_Drone_OP">כמות לחידוש רחפן מבצעי:</label>
                <input type="number" name="REPLENISH_Drone_OP" value="2" placeholder="(כמות רחפנים מבצעיים שמתווספים בכל מחזור חידוש)">
            </div>
            <div class="input-group">
                <label for="REPLENISH_EVERY_Drone_OP">מחזור חידוש רחפן מבצעי (ימים):</label>
                <input type="number" name="REPLENISH_EVERY_Drone_OP" value="180" placeholder="(תדירות הוספת רחפנים מבצעיים למלאי, בימים)">
            </div>
            <div class="input-group">
                <label for="REPLENISH_Drone_TR_PRO">כמות לחידוש רחפן אימון והכשרה:</label>
                <input type="number" name="REPLENISH_Drone_TR_PRO" value="1" placeholder="(כמות רחפני אימון/הכשרה שמתווספים בכל מחזור חידוש)">
            </div>
            <div class="input-group">
                <label for="REPLENISH_EVERY_Drone_TR_PRO">מחזור חידוש רחפן אימון והכשרה (ימים):</label>
                <input type="number" name="REPLENISH_EVERY_Drone_TR_PRO" value="180" placeholder="(תדירות הוספת רחפני אימון/הכשרה למלאי, בימים)">
            </div>
            <div class="input-group">
                <label for="REPLENISH_Agur">כמות לחידוש עגור:</label>
                <input type="number" name="REPLENISH_Agur" value="1" placeholder="(כמות כלי עגור שמתווספים בכל מחזור חידוש)">
            </div>
            <div class="input-group">
                <label for="REPLENISH_EVERY_Agur">מחזור חידוש עגור (ימים):</label>
                <input type="number" name="REPLENISH_EVERY_Agur" value="180" placeholder="(תדירות הוספת כלי עגור למלאי, בימים)">
            </div>
            <div class="input-group">
                <label for="REPLENISH_Sting">כמות לחידוש סטינג:</label>
                <input type="number" name="REPLENISH_Sting" value="0" placeholder="(כמות כלי סטינג שמתווספים בכל מחזור חידוש)">
            </div>
            <div class="input-group">
                <label for="REPLENISH_EVERY_Sting">מחזור חידוש סטינג (ימים):</label>
                <input type="number" name="REPLENISH_EVERY_Sting" value="180" placeholder="(תדירות הוספת כלי סטינג למלאי, בימים)">
            </div>

            <h3>עלויות ציוד (ש"ח)</h3>
            <div class="input-group">
                <label for="DRONE_COST">עלות רחפן:</label>
                <input type="number" name="DRONE_COST" value="500000" placeholder="(עלות רחפן בודד בש"ח)">
            </div>
            <div class="input-group">
                <label for="AGUR_COST">עלות עגור:</label>
                <input type="number" name="AGUR_COST" value="500000" placeholder="(עלות כלי עגור בודד בש"ח)">
            </div>
            <div class="input-group">
                <label for="STING_COST">עלות סטינג:</label>
                <input type="number" name="STING_COST" value="500000" placeholder="(עלות כלי סטינג בודד בש"ח)">
            </div>

            <h3>שיעורי כשל (ממוצע ימים בין תקלות)</h3>
            <div class="input-group">
                <label for="FAIL_Agur">עגור:</label>
                <input type="number" name="FAIL_Agur" value="7" placeholder="(ממוצע ימים לפני שעגור חווה תקלה)">
            </div>
            <div class="input-group">
                <label for="FAIL_Drone_OP">רחפן מבצעי:</label>
                <input type="number" name="FAIL_Drone_OP" value="7" placeholder="(ממוצע ימים לפני שרחפן מבצעי חווה תקלה)">
            </div>
            <div class="input-group">
                <label for="FAIL_Drone_TR_PRO">רחפן אימון והכשרה:</label>
                <input type="number" name="FAIL_Drone_TR_PRO" value="21" placeholder="(ממוצע ימים לפני שרחפן אימונים/הכשרה חווה תקלה)">
            </div>
            <div class="input-group">
                <label for="FAIL_Sting">סטינג:</label>
                <input type="number" name="FAIL_Sting" value="90" placeholder="(ממוצע ימים לפני שסטינג חווה תקלה)">
            </div>

            <h3>זמני תיקון (ממוצע וסטיית תקן בימים)</h3>
            <h4>עגור:</h4>
            <div class="input-group">
                <label for="REPAIR_Agur_MEAN">ממוצע תיקון עגור:</label>
                <input type="number" step="0.1" name="REPAIR_Agur_MEAN" value="5" placeholder="(ממוצע ימים לתיקון עגור)">
            </div>
            <div class="input-group">
                <label for="REPAIR_Agur_STD">עגור:</label>
                <input type="number" step="0.1" name="REPAIR_Agur_STD" value="1" placeholder="(סטיית תקן ימים לתיקון עגור)">
            </div>
            <h4>רחפן:</h4>
            <div class="input-group">
                <label for="REPAIR_Drone_MEAN">ממוצע תיקון רחפן:</label>
                <input type="number" step="0.1" name="REPAIR_Drone_MEAN" value="7" placeholder="(ממוצע ימים לתיקון רחפן)">
            </div>
            <div class="input-group">
                <label for="REPAIR_Drone_STD">סטיית תקן תיקון רחפן:</label>
                <input type="number" step="0.1" name="REPAIR_Drone_STD" value="2" placeholder="(סטיית תקן ימים לתיקון רחפן)">
            </div>
            <h4>סטינג:</h4>
            <div class="input-group">
                <label for="REPAIR_Sting_MEAN">ממוצע תיקון סטינג:</label>
                <input type="number" step="0.1" name="REPAIR_Sting_MEAN" value="90" placeholder="(ממוצע ימים לתיקון סטינג)">
            </div>
            <div class="input-group">
                <label for="REPAIR_Sting_STD">סטיית תקן תיקון סטינג:</label>
                <input type="number" step="0.1" name="REPAIR_Sting_STD" value="30" placeholder="(סטיית תקן ימים לתיקון סטינג)">
            </div>

            <h3>פרמטרים נוספים</h3>
            <div class="input-group">
                <label for="CRASH">הסתברות התרסקות (1 מתוך):</label>
                <input type="number" name="CRASH" value="200" placeholder="(ההסתברות להתרסקות היא 1 חלקי מספר זה)">
            </div>
            <div class="input-group">
                <label for="DUAL_DRONE_PROB">הסתברות לפעילות המצריכה רחפן ממסר:</label>
                <input type="number" step="0.01" name="DUAL_DRONE_PROB" value="0.5" placeholder="(הסיכוי שפעילות תכלול רחפן ממסר, בין 0 ל-1)">
            </div>
            <div class="input-group">
                <label for="DRONE_LIFETIME">שעות חיי רחפן:</label>
                <input type="number" name="DRONE_LIFETIME" value="150" placeholder="(מקסימום שעות טיסה לפני הוצאת רחפן משימוש)">
            </div>

            <h3>פרמטרי אימון והכשרה:</h3>
            <div class="input-group">
                <label for="NUM_TRAINEES_ANNUAL">מספר אנשים בהכשרה בשנה:</label>
                <input type="number" name="NUM_TRAINEES_ANNUAL" value="6" placeholder="(כמות מטיסים חדשים שיעברו הכשרה מדי שנה)">
            </div>
            <div class="input-group">
                <label for="TRAINING_FLIGHTS_PER_PILOT_ANNUAL_TRAINEE">מספר הטסות להכשרה למטיס:</label>
                <input type="number" name="TRAINING_FLIGHTS_PER_PILOT_ANNUAL_TRAINEE" value="15" placeholder="(מספר הטסות שנדרש למטיס להכשרה)">
            </div>
            <div class="input-group">
                <label for="NUM_PROFICIENCY_KEEPERS_ANNUAL">מספר שומרי כשירות בשנה:</label>
                <input type="number" name="NUM_PROFICIENCY_KEEPERS_ANNUAL" value="10" placeholder="(כמות מטיסים שישמרו על כשירות מדי שנה)">
            </div>
            <div class="input-group">
                <label for="TRAINING_FLIGHTS_PER_PILOT_ANNUAL_PROFICIENCY">מספר הטסות לכשירות למטיס בשנה:</label>
                <input type="number" name="TRAINING_FLIGHTS_PER_PILOT_ANNUAL_PROFICIENCY" value="30" placeholder="(מספר הטסות שנדרש למטיס כשירות בשנה)">
            </div>
            <div class="input-group">
                <label for="HOURS_PER_FLIGHT_TRAINING">שעות טיסה למפגש אימון/הכשרה בודד:</label>
                <input type="number" step="0.1" name="HOURS_PER_FLIGHT_TRAINING" value="0.5" placeholder="(אורך מפגש אימון/הכשרה בודד בשעות)">
            </div>
            <div class="input-group">
                <label for="FH_Agur">שעות טיסה לפעילות עגור:</label>
                <input type="number" step="0.1" name="FH_Agur" value="2.0" placeholder="(שעות טיסה הנצרכות לפעילות עגור)">
            </div>
            <div class="input-group">
                <label for="FH_Sting">שעות טיסה לפעילות סטינג:</label>
                <input type="number" step="0.1" name="FH_Sting" value="1.5" placeholder="(שעות טיסה הנצרכות לפעילות סטינג)">
            </div>
            <div class="input-group">
                <label for="ACT_PER_DAY">מספר פעילויות ממוצע ליום:</label>
                <input type="number" step="0.1" name="ACT_PER_DAY" value="1.5" placeholder="(מספר משימות/פעילויות מתוכנן ממוצע ליום)">
            </div>

            <h3>קביעת עדיפות:</h3>
            <div class="input-group">
                <label for="MISSION_PARTNER_PRIORITY">עדיפות לכלי ליווי בפעילות מבצעית:</label>
                <select name="MISSION_PARTNER_PRIORITY">
                    <option value="1">סטינג</option>
                    <option value="0">עגור</option>
                    <option value="2">לא משנה (אקראי)</option>
                </select>
            </div>
            <div class="input-group">
                <label for="TRAINING_PARTNER_PRIORITY">עדיפות לכלי ליווי בפעילות אימון/הכשרה:</label>
                <select name="TRAINING_PARTNER_PRIORITY">
                    <option value="0">עגור</option>
                    <option value="1">סטינג</option>
                    <option value="2">לא משנה (אקראי)</option>
                </select>
            </div>

            <input type="submit" value="הפעל סימולציה">
        </form>
    </div>
</body>
</html>
'''

result_template = '''
<!DOCTYPE html>
<html>
<head>
    <title>Simulation Results</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f8f9fa;
            color: #343a40;
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            padding: 120px; /* Significantly larger padding around the body */
            box-sizing: border-box;
            direction: rtl; /* Right-to-left for Hebrew content like paragraphs */
            text-align: right; /* Align text to the right for Hebrew paragraphs */
        }
        .container {
            background-color: #ffffff;
            padding: 80px 100px; /* Increased padding inside the container */
            border-radius: 20px;
            box-shadow: 0 12px 25px rgba(0, 0, 0, 0.2);
            max-width: 1300px; /* Even wider container for graphs */
            width: 100%;
            text-align: center; /* Center images and buttons */
            margin-bottom: 60px; /* More space between containers */
            box-sizing: border-box;
        }
        h2 {
            color: #003366;
            margin-bottom: 40px;
            font-size: 2.8em;
            font-weight: 600;
            text-align: center; /* Keep main heading centered */
        }
        h3 {
            color: #004d99;
            margin-top: 45px;
            margin-bottom: 30px;
            font-size: 2em;
            font-weight: 500;
            text-align: center; /* Center graph headings */
        }
        p {
            font-size: 1.4em; /* Larger text for success rate */
            margin-bottom: 20px; /* Adjusted margin */
            font-weight: bold;
            color: #28a745;
            text-align: center; /* Center success rate text */
        }
        .cost-info {
            font-size: 1.2em; /* Slightly smaller for cost info */
            color: #4CAF50; /* Green for cost */
            margin-top: 10px;
            margin-bottom: 10px;
            text-align: center;
        }
        img {
            max-width: 100%;
            height: auto;
            border: 1px solid #99ccff;
            border-radius: 15px;
            margin-bottom: 40px; /* More space below images */
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15); /* Slightly stronger shadow for graphs */
            display: inline-block; /* Change from block to inline-block */
            /* Remove margin-left: auto; and margin-right: auto; if they are still there for img */
        }
table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 30px;
            margin-bottom: 30px;
            direction: rtl; /* Right-to-left for the table */
            text-align: right;
            margin-left: auto; /* Add this line */
            margin-right: auto; /* Add this line */
            display: block; /* Add this line if table doesn't center as expected */
        }
        th, td {
            border: 1px solid #ddd;
            padding: 12px 15px;
            text-align: right;
            font-size: 1.1em;
        }
        th {
            background-color: #004d99;
            color: white;
            font-weight: bold;
        }
        tr:nth-child(even) {
            background-color: #f2f2f2;
        }
        tr:hover {
            background-color: #e9ecef;
        }
        .average-row {
            font-weight: bold;
            background-color: #d1ecf1 !important; /* Light blue for average row */
            color: #004d99;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>תוצאות הסימולציה</h2>
        {{ results_table | safe }}
    </div>
    <div class="container">
        <h3>Drone Flight Hours and Retirement Causes</h3>
        <img src="data:image/png;base64,{{ graph1 }}" alt="Drone Flight Hours and Retirement Causes"/>
    </div>
    <div class="container">
        <h3>Mission Results Summary</h3>
        <img src="data:image/png;base64,{{ graph2 }}" alt="Mission Results Summary"/>
    </div>
    <div class="container">
        <h3>Number of Available Assets Over Time</h3>
        <img src="data:image/png;base64,{{ graph3 }}" alt="Number of Available Assets Over Time"/>
    </div>
    <div class="container">
        <h3>Annual Flight Hours and Cost Breakdown by Type (Drones)</h3>
        <img src="data:image/png;base64,{{ graph4 }}" alt="Annual Flight Hours and Cost Breakdown by Type"/>
    </div>
    <div class="container">
        <h3>Asset Status Summary at End of Simulation</h3>
        <img src="data:image/png;base64,{{ graph5 }}" alt="Asset Status Summary"/>
    </div>
</body>
</html>
'''


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template_string(form_template)

    # Parse user input
    form = request.form
    YEARS = int(form['YEARS'])
    DAYS = YEARS * 365

    # Updated initial drone types
    INIT = {
        'Drone_OP': int(form['Drone_OP']),
        'Drone_TR_PRO': int(form['Drone_TR_PRO']),  # Renamed in form
        'Agur': int(form['Agur']),
        'Sting': int(form['Sting'])
    }

    # Dynamically read replenishment amounts and cycles
    REPLENISH = {}
    REPLENISH_EVERY = {}
    for item_type_key in ['Drone_OP', 'Drone_TR_PRO', 'Agur', 'Sting']:
        REPLENISH[item_type_key] = int(form.get(f'REPLENISH_{item_type_key}', 0))
        replenish_val = int(form.get(f'REPLENISH_EVERY_{item_type_key}', DAYS + 1))
        REPLENISH_EVERY[item_type_key] = replenish_val if replenish_val > 0 else (DAYS + 1)

    # Read costs
    COSTS = {
        'Drone': int(form.get('DRONE_COST', 500000)),
        'Agur': int(form.get('AGUR_COST', 500000)),
        'Sting': int(form.get('STING_COST', 500000))
    }

    # Corrected FAIL dictionary creation
    FAIL = {}
    for k, v in form.items():
        if k.startswith('FAIL_'):
            fail_key = k[len('FAIL_'):]
            val = float(v)
            # Map 'Drone_TR_PRO' failure rate to 'Training' subtype
            if fail_key == 'Drone_TR_PRO':
                FAIL['Training'] = 1 / val if val != 0 else float('inf')
            elif fail_key == 'Drone_OP':
                FAIL['Operational'] = 1 / val if val != 0 else float('inf')
            else:
                FAIL[fail_key] = 1 / val if val != 0 else float('inf')

    # Parse REPAIR times (mean and std separately)
    REPAIR = {}
    for item_type in ['Agur', 'Drone', 'Sting']:
        mean_key = f'REPAIR_{item_type}_MEAN'
        std_key = f'REPAIR_{item_type}_STD'
        REPAIR[item_type] = (float(form[mean_key]), float(form[std_key]))

    crash_val = float(form['CRASH'])
    CRASH_PROB = 1 / crash_val if crash_val != 0 else 0
    DUAL_DRONE_PROB = float(form.get('DUAL_DRONE_PROB', 0.5))
    DRONE_LIFETIME = float(form['DRONE_LIFETIME'])

    # Calculate operating cost per hour based on drone cost and lifetime
    HOURLY_OPERATING_COST_DRONE = COSTS['Drone'] / DRONE_LIFETIME if DRONE_LIFETIME > 0 else 0

    # New training/proficiency parameters
    NUM_TRAINEES_ANNUAL = int(form.get('NUM_TRAINEES_ANNUAL', 6))
    TRAINING_FLIGHTS_PER_PILOT_ANNUAL_TRAINEE = int(form.get('TRAINING_FLIGHTS_PER_PILOT_ANNUAL_TRAINEE', 15))
    HOURS_PER_FLIGHT_TRAINING = float(form.get('HOURS_PER_FLIGHT_TRAINING', 0.5))
    NUM_PROFICIENCY_KEEPERS_ANNUAL = int(form.get('NUM_PROFICIENCY_KEEPERS_ANNUAL', 10))
    TRAINING_FLIGHTS_PER_PILOT_ANNUAL_PROFICIENCY = int(form.get('TRAINING_FLIGHTS_PER_PILOT_ANNUAL_PROFICIENCY', 20))
    MAX_DAILY_TRAINING_SLOTS = int(form.get('MAX_DAILY_TRAINING_SLOTS', 2))

    FH = {'Agur': float(form['FH_Agur']), 'Sting': float(form['FH_Sting'])}
    ACT_PER_DAY = float(form['ACT_PER_DAY'])

    # Priority settings for drones in missions - Hardcoded as per user request
    PRIORITY = ['Operational', 'Training']

    # Priority for mission partner (Agur/Sting)
    MISSION_PARTNER_PRIORITY = int(form.get('MISSION_PARTNER_PRIORITY', 2))  # 0: Agur, 1: Sting, 2: Any

    # Priority for training partner (Agur/Sting)
    TRAINING_PARTNER_PRIORITY = int(form.get('TRAINING_PARTNER_PRIORITY', 2))  # 0: Agur, 1: Sting, 2: Any

    # Calculate depreciation per hour for crash cost
    DEPRECIATION_PER_HOUR = HOURLY_OPERATING_COST_DRONE

    # Initialize assets
    np.random.seed(42)
    Drone = []
    for i in range(INIT['Drone_OP']):
        Drone.append({'ID': f'Drone_OP_{i}', 'Type': 'Drone', 'Subtype': 'Operational', 'Repair': 0, 'Hours': 0,
                      'Broken_Count': 0, 'Activities': 0, 'Birth_Day': 0, 'Crashed': False, 'Retired_Day': None,
                      'Retired_Reason': None, 'Training_Flights_Accrued': 0, 'Proficiency_Flights_Accrued': 0,
                      'Is_Proficient': True})

    for i in range(INIT['Drone_TR_PRO']):
        Drone.append({'ID': f'Drone_TR_{i}', 'Type': 'Drone', 'Subtype': 'Training', 'Repair': 0, 'Hours': 0,
                      'Broken_Count': 0, 'Activities': 0, 'Birth_Day': 0, 'Crashed': False, 'Retired_Day': None,
                      'Retired_Reason': None, 'Training_Flights_Accrued': 0, 'Proficiency_Flights_Accrued': 0,
                      'Is_Proficient': False})

    Agur = [
        {'ID': f'Agur_{i}', 'Type': 'Agur', 'Repair': 0, 'Hours': 0, 'Broken_Count': 0, 'Activities': 0, 'Birth_Day': 0,
         'Crashed': False, 'Retired_Day': None, 'Retired_Reason': None} for i in range(INIT['Agur'])]
    Sting = [{'ID': f'Sting_{i}', 'Type': 'Sting', 'Repair': 0, 'Hours': 0, 'Broken_Count': 0, 'Activities': 0,
              'Birth_Day': 0, 'Crashed': False, 'Retired_Day': None, 'Retired_Reason': None} for i in
             range(INIT['Sting'])]

    counter = {'Drone': len(Drone), 'Agur': len(Agur), 'Sting': len(Sting)}
    battery_logs = defaultdict(list)
    summary = {'Planned': 0, 'Succeeded': 0, 'Failed': 0}

    # Pilot management for training/proficiency
    pilots = []  # {ID, Type: 'Trainee'/'Proficiency', Flights_Current_Year, Completed_Training}

    # Cost tracking
    crashed_assets_count = defaultdict(int)
    annual_missions_planned = defaultdict(int)
    annual_missions_succeeded = defaultdict(int)
    annual_replenish_cost_by_year = defaultdict(float)
    annual_failures_by_type = defaultdict(lambda: defaultdict(int))
    annual_crashes_by_type = defaultdict(lambda: defaultdict(int))

    new_assets_added = defaultdict(int)
    total_operating_cost = 0

    # Data for new annual cost graph
    annual_flight_hours_by_type = defaultdict(lambda: defaultdict(float))
    annual_crash_costs_by_type = defaultdict(lambda: defaultdict(float))
    annual_operating_costs_by_type = defaultdict(lambda: defaultdict(float))

    available_counts_history = defaultdict(lambda: defaultdict(int))
    crash_markers = defaultdict(lambda: defaultdict(int))
    replenish_markers = defaultdict(lambda: defaultdict(int))

    for day in range(DAYS):
        current_year = day // 365

        # Reset annual proficiency flights for pilots at the start of each year (Day 0 of each year)
        if day % 365 == 0:
            for pilot in pilots:
                if pilot['Type'] == 'Proficiency':
                    pilot['Flights_Current_Year'] = 0

                    # Add new trainees and proficiency keepers at the start of each year
            for i in range(NUM_TRAINEES_ANNUAL):
                pilots.append({'ID': f'Trainee_{len(pilots)}', 'Type': 'Trainee',
                               'Flights_Completed': 0,
                               'Completed_Training': False})

            for i in range(NUM_PROFICIENCY_KEEPERS_ANNUAL):
                pilots.append({'ID': f'Proficiency_{len(pilots)}', 'Type': 'Proficiency',
                               'Flights_Current_Year': 0})

        # Daily maintenance/repair
        for d in Drone + Agur + Sting:
            if d['Repair'] > 0:
                d['Repair'] -= 1

        # Replenishment
        for item_type_key in ['Drone_OP', 'Drone_TR_PRO', 'Agur', 'Sting']:
            replenish_cycle = REPLENISH_EVERY[item_type_key]
            if replenish_cycle > 0 and day % replenish_cycle == 0 and day != 0:
                amount = REPLENISH[item_type_key]
                for _ in range(amount):
                    if item_type_key == 'Drone_OP':
                        Drone.append(
                            {'ID': f'Drone_OP_{counter["Drone"]}', 'Type': 'Drone', 'Subtype': 'Operational',
                             'Repair': 0,
                             'Hours': 0, 'Broken_Count': 0, 'Activities': 0, 'Birth_Day': day, 'Crashed': False,
                             'Retired_Day': None,
                             'Retired_Reason': None, 'Training_Flights_Accrued': 0, 'Proficiency_Flights_Accrued': 0,
                             'Is_Proficient': True})
                        counter['Drone'] += 1
                        new_assets_added['Drone'] += 1
                        annual_replenish_cost_by_year[current_year] += COSTS['Drone']
                        replenish_markers[day]['Drone'] += 1
                    elif item_type_key == 'Drone_TR_PRO':
                        Drone.append(
                            {'ID': f'Drone_TR_{counter["Drone"]}', 'Type': 'Drone', 'Subtype': 'Training', 'Repair': 0,
                             'Hours': 0, 'Broken_Count': 0, 'Activities': 0, 'Birth_Day': day, 'Crashed': False,
                             'Retired_Day': None,
                             'Retired_Reason': None, 'Training_Flights_Accrued': 0, 'Proficiency_Flights_Accrued': 0,
                             'Is_Proficient': False})
                        counter['Drone'] += 1
                        new_assets_added['Drone'] += 1
                        annual_replenish_cost_by_year[current_year] += COSTS['Drone']
                        replenish_markers[day]['Drone'] += 1
                    elif item_type_key == 'Agur':
                        Agur.append({'ID': f'Agur_{counter["Agur"]}', 'Type': 'Agur', 'Repair': 0, 'Hours': 0,
                                     'Broken_Count': 0, 'Activities': 0, 'Birth_Day': day, 'Crashed': False,
                                     'Retired_Day': None, 'Retired_Reason': None})
                        counter['Agur'] += 1
                        new_assets_added['Agur'] += 1
                        annual_replenish_cost_by_year[current_year] += COSTS['Agur']
                        replenish_markers[day]['Agur'] += 1
                    elif item_type_key == 'Sting':
                        Sting.append({'ID': f'Sting_{counter["Sting"]}', 'Type': 'Sting', 'Repair': 0, 'Hours': 0,
                                      'Broken_Count': 0, 'Activities': 0, 'Birth_Day': day, 'Crashed': False,
                                      'Retired_Day': None, 'Retired_Reason': None})
                        counter['Sting'] += 1
                        new_assets_added['Sting'] += 1
                        annual_replenish_cost_by_year[current_year] += COSTS['Sting']
                        replenish_markers[day]['Sting'] += 1

        # Training/Proficiency Activities
        training_slots_today = MAX_DAILY_TRAINING_SLOTS

        # Filter available training drones
        available_training_drones = [d for d in Drone if
                                     d['Subtype'] == 'Training' and d['Repair'] == 0 and not d['Crashed'] and d[
                                         'Retired_Day'] is None]

        # Filter available training partners based on TRAINING_PARTNER_PRIORITY
        eligible_training_partners = []
        if TRAINING_PARTNER_PRIORITY == 1:  # Prefer Sting
            eligible_training_partners.extend(
                [s for s in Sting if s['Repair'] == 0 and not s['Crashed'] and s['Retired_Day'] is None])
            eligible_training_partners.extend(
                [a for a in Agur if a['Repair'] == 0 and not a['Crashed'] and a['Retired_Day'] is None])
        elif TRAINING_PARTNER_PRIORITY == 0:  # Prefer Agur
            eligible_training_partners.extend(
                [a for a in Agur if a['Repair'] == 0 and not a['Crashed'] and a['Retired_Day'] is None])
            eligible_training_partners.extend(
                [s for s in Sting if s['Repair'] == 0 and not s['Crashed'] and s['Retired_Day'] is None])
        else:  # Any (random order)
            eligible_training_partners.extend(
                [a for a in Agur if a['Repair'] == 0 and not a['Crashed'] and a['Retired_Day'] is None])
            eligible_training_partners.extend(
                [s for s in Sting if s['Repair'] == 0 and not s['Crashed'] and s['Retired_Day'] is None])
            np.random.shuffle(eligible_training_partners)

        # Filter pilots who need to train or keep proficiency
        pilots_for_training_today = []
        for pilot in pilots:
            if pilot['Type'] == 'Trainee' and not pilot['Completed_Training']:
                if pilot['Flights_Completed'] < TRAINING_FLIGHTS_PER_PILOT_ANNUAL_TRAINEE:
                    pilots_for_training_today.append(pilot)
            elif pilot['Type'] == 'Proficiency':
                if pilot['Flights_Current_Year'] < TRAINING_FLIGHTS_PER_PILOT_ANNUAL_PROFICIENCY:
                    pilots_for_training_today.append(pilot)

        np.random.shuffle(pilots_for_training_today)

        for pilot in pilots_for_training_today:
            if training_slots_today <= 0:
                break
            if not available_training_drones or not eligible_training_partners:
                break

            drone_for_training = available_training_drones.pop(0)
            partner_for_training = eligible_training_partners.pop(0)

            # Perform training flight
            drone_for_training['Hours'] += HOURS_PER_FLIGHT_TRAINING
            partner_for_training['Hours'] += HOURS_PER_FLIGHT_TRAINING

            annual_flight_hours_by_type[current_year]['Training'] += HOURS_PER_FLIGHT_TRAINING
            total_operating_cost += HOURLY_OPERATING_COST_DRONE * HOURS_PER_FLIGHT_TRAINING
            annual_operating_costs_by_type[current_year][
                'Training'] += HOURLY_OPERATING_COST_DRONE * HOURS_PER_FLIGHT_TRAINING

            # Update pilot's flights
            if pilot['Type'] == 'Trainee':
                pilot['Flights_Completed'] += 1
                if pilot['Flights_Completed'] >= TRAINING_FLIGHTS_PER_PILOT_ANNUAL_TRAINEE:
                    pilot['Completed_Training'] = True
                    drone_for_training['Is_Proficient'] = True
            elif pilot['Type'] == 'Proficiency':
                pilot['Flights_Current_Year'] += 1
                drone_for_training['Is_Proficient'] = True

                # Check for drone retirement after training
            if drone_for_training['Hours'] >= DRONE_LIFETIME and drone_for_training['Retired_Day'] is None:
                drone_for_training['Retired_Day'] = day
                drone_for_training['Retired_Reason'] = 'Lifetime'

            # Check for failure after training for drone
            if drone_for_training['Retired_Day'] is None and FAIL['Training'] != float('inf') and np.random.rand() < \
                    FAIL['Training']:
                drone_for_training['Broken_Count'] += 1
                annual_failures_by_type[current_year][drone_for_training['Type']] += 1
                drone_for_training['Repair'] = max(1, int(np.random.normal(*REPAIR['Drone'])))

            # Check for failure after training for partner
            if partner_for_training['Retired_Day'] is None and FAIL[partner_for_training['Type']] != float(
                    'inf') and np.random.rand() < FAIL[partner_for_training['Type']]:
                partner_for_training['Broken_Count'] += 1
                annual_failures_by_type[current_year][partner_for_training['Type']] += 1
                partner_for_training['Repair'] = max(1, int(np.random.normal(*REPAIR[partner_for_training['Type']])))

            # Crash check for training drone
            if np.random.rand() < CRASH_PROB:
                drone_for_training['Crashed'] = True
                drone_for_training['Retired_Day'] = day
                drone_for_training['Retired_Reason'] = 'Crashed'
                crashed_assets_count['Drone'] += 1
                crash_markers[day]['Drone'] += 1
                annual_crashes_by_type[current_year]['Drone'] += 1
                annual_crash_costs_by_type[current_year][drone_for_training['Subtype']] += (COSTS['Drone'] +
                                                                                            (DRONE_LIFETIME -
                                                                                             drone_for_training[
                                                                                                 'Hours']) * DEPRECIATION_PER_HOUR)

                # Partner also crashes if drone crashes
                partner_for_training['Crashed'] = True
                partner_for_training['Retired_Day'] = day
                partner_for_training['Retired_Reason'] = 'Crashed'
                crashed_assets_count[partner_for_training['Type']] += 1
                crash_markers[day][partner_for_training['Type']] += 1
                annual_crashes_by_type[current_year][partner_for_training['Type']] += 1

            training_slots_today -= 1

        # Mission Activities
        daily_activities = int(ACT_PER_DAY) + (1 if np.random.rand() < ACT_PER_DAY % 1 else 0)
        summary['Planned'] += daily_activities
        annual_missions_planned[current_year] += daily_activities

        # Prepare available drones for mission based on priority
        available_drones_for_mission = []
        for p_type_str in PRIORITY:
            if p_type_str == 'Operational':
                available_drones_for_mission.extend([d for d in Drone if
                                                     d['Subtype'] == 'Operational' and d['Repair'] == 0 and not d[
                                                         'Crashed'] and d['Retired_Day'] is None])
            elif p_type_str == 'Training':
                available_drones_for_mission.extend([d for d in Drone if
                                                     d['Subtype'] == 'Training' and d['Repair'] == 0 and not d[
                                                         'Crashed'] and d['Retired_Day'] is None and d[
                                                         'Is_Proficient']])

        # Remove duplicates from available_drones_for_mission
        seen_drone_ids = set()
        unique_available_drones_for_mission = []
        for d in available_drones_for_mission:
            if d['ID'] not in seen_drone_ids:
                unique_available_drones_for_mission.append(d)
                seen_drone_ids.add(d['ID'])
        available_drones_for_mission = unique_available_drones_for_mission

        # Prepare available partners for missions based on MISSION_PARTNER_PRIORITY
        eligible_mission_partners = []
        if MISSION_PARTNER_PRIORITY == 1:  # Prefer Sting
            eligible_mission_partners.extend(
                [s for s in Sting if s['Repair'] == 0 and not s['Crashed'] and s['Retired_Day'] is None])
            eligible_mission_partners.extend(
                [a for a in Agur if a['Repair'] == 0 and not a['Crashed'] and a['Retired_Day'] is None])
        elif MISSION_PARTNER_PRIORITY == 0:  # Prefer Agur
            eligible_mission_partners.extend(
                [a for a in Agur if a['Repair'] == 0 and not a['Crashed'] and a['Retired_Day'] is None])
            eligible_mission_partners.extend(
                [s for s in Sting if s['Repair'] == 0 and not s['Crashed'] and s['Retired_Day'] is None])
        else:  # Any (random order)
            eligible_mission_partners.extend(
                [a for a in Agur if a['Repair'] == 0 and not a['Crashed'] and a['Retired_Day'] is None])
            eligible_mission_partners.extend(
                [s for s in Sting if s['Repair'] == 0 and not s['Crashed'] and s['Retired_Day'] is None])
            np.random.shuffle(eligible_mission_partners)

        for _ in range(daily_activities):
            chosen_drone = None
            chosen_partner = None
            partner_type = None
            fh = 0

            # Try to find a drone and a partner (Agur/Sting)
            eligible_drones_copy = [d for d in available_drones_for_mission if d['Retired_Day'] is None]
            eligible_partners_copy = [p for p in eligible_mission_partners if p['Retired_Day'] is None]

            if not eligible_drones_copy:
                summary['Failed'] += 1
                continue

            if not eligible_partners_copy:
                summary['Failed'] += 1
                continue

            chosen_drone = eligible_drones_copy.pop(0)
            chosen_partner = eligible_partners_copy.pop(0)

            fh = FH[chosen_partner['Type']]
            partner_type = chosen_partner['Type']

            # Ensure chosen assets are removed from the main pools for the current day's subsequent activities
            if chosen_drone in available_drones_for_mission:
                available_drones_for_mission.remove(chosen_drone)
            if chosen_partner in eligible_mission_partners:
                eligible_mission_partners.remove(chosen_partner)

            relay_drone = None
            # Relay drone logic: only if probability allows AND there's another available drone (not selected for primary)
            if np.random.rand() < DUAL_DRONE_PROB:
                relay_candidates = [d for d in available_drones_for_mission if d['ID'] != chosen_drone['ID']]
                if relay_candidates:
                    relay_drone = relay_candidates.pop(np.random.randint(len(relay_candidates)))
                    if relay_drone in available_drones_for_mission:
                        available_drones_for_mission.remove(relay_drone)

            # Crash check (for main drone)
            if np.random.rand() < CRASH_PROB:
                chosen_drone['Crashed'] = True
                chosen_drone['Retired_Day'] = day
                chosen_drone['Retired_Reason'] = 'Crashed'
                crashed_assets_count['Drone'] += 1
                crash_markers[day]['Drone'] += 1
                annual_crashes_by_type[current_year]['Drone'] += 1
                annual_crash_costs_by_type[current_year][chosen_drone['Subtype']] += (COSTS['Drone'] +
                                                                                      (DRONE_LIFETIME - chosen_drone[
                                                                                          'Hours']) * DEPRECIATION_PER_HOUR)

                # If main drone crashes, partner also crashes
                chosen_partner['Crashed'] = True
                chosen_partner['Retired_Day'] = day
                chosen_partner['Retired_Reason'] = 'Crashed'
                crashed_assets_count[partner_type] += 1
                crash_markers[day][partner_type] += 1
                annual_crashes_by_type[current_year][partner_type] += 1

                # If relay drone was assigned, and main drone crashes, relay drone is also lost if part of the same mission failure
                if relay_drone:
                    relay_drone['Crashed'] = True
                    relay_drone['Retired_Day'] = day
                    relay_drone['Retired_Reason'] = 'Crashed'
                    crashed_assets_count['Drone'] += 1
                    crash_markers[day]['Drone'] += 1
                    annual_crashes_by_type[current_year]['Drone'] += 1
                    annual_crash_costs_by_type[current_year][relay_drone['Subtype']] += (COSTS['Drone'] +
                                                                                         (DRONE_LIFETIME - relay_drone[
                                                                                             'Hours']) * DEPRECIATION_PER_HOUR)
                summary['Failed'] += 1
                continue

            # Crash check (for relay drone only, if main drone didn't crash)
            if relay_drone and np.random.rand() < CRASH_PROB:
                relay_drone['Crashed'] = True
                relay_drone['Retired_Day'] = day
                relay_drone['Retired_Reason'] = 'Crashed'
                crashed_assets_count['Drone'] += 1
                crash_markers[day]['Drone'] += 1
                annual_crashes_by_type[current_year]['Drone'] += 1
                annual_crash_costs_by_type[current_year][relay_drone['Subtype']] += (COSTS['Drone'] +
                                                                                     (DRONE_LIFETIME - relay_drone[
                                                                                         'Hours']) * DEPRECIATION_PER_HOUR)
                # Mission might still succeed if primary assets are fine

            # Activity successful - update hours and activities
            summary['Succeeded'] += 1
            annual_missions_succeeded[current_year] += 1

            # Update main drone
            chosen_drone['Activities'] += 1
            chosen_drone['Hours'] += fh
            annual_flight_hours_by_type[current_year]['Operational'] += fh
            total_operating_cost += HOURLY_OPERATING_COST_DRONE * fh
            annual_operating_costs_by_type[current_year]['Operational'] += HOURLY_OPERATING_COST_DRONE * fh
            if chosen_drone['Hours'] >= DRONE_LIFETIME and chosen_drone['Retired_Day'] is None:
                chosen_drone['Retired_Day'] = day
                chosen_drone['Retired_Reason'] = 'Lifetime'
            # Check for failure after activity for main drone
            if chosen_drone['Retired_Day'] is None and FAIL[chosen_drone['Subtype']] != float(
                    'inf') and np.random.rand() < FAIL[chosen_drone['Subtype']]:
                chosen_drone['Broken_Count'] += 1
                annual_failures_by_type[current_year][chosen_drone['Type']] += 1
                chosen_drone['Repair'] = max(1, int(np.random.normal(*REPAIR['Drone'])))

            # Update partner
            chosen_partner['Activities'] += 1
            chosen_partner['Hours'] += fh
            if chosen_partner['Retired_Day'] is None and FAIL[chosen_partner['Type']] != float(
                    'inf') and np.random.rand() < FAIL[chosen_partner['Type']]:
                chosen_partner['Broken_Count'] += 1
                annual_failures_by_type[current_year][chosen_partner['Type']] += 1
                chosen_partner['Repair'] = max(1, int(np.random.normal(*REPAIR[chosen_partner['Type']])))

            # Update relay drone (if it exists and didn't crash)
            if relay_drone and not relay_drone['Crashed']:
                relay_drone['Activities'] += 1
                relay_drone['Hours'] += fh
                annual_flight_hours_by_type[current_year]['Operational'] += fh
                total_operating_cost += HOURLY_OPERATING_COST_DRONE * fh
                annual_operating_costs_by_type[current_year]['Operational'] += HOURLY_OPERATING_COST_DRONE * fh
                if relay_drone['Hours'] >= DRONE_LIFETIME and relay_drone['Retired_Day'] is None:
                    relay_drone['Retired_Day'] = day
                    relay_drone['Retired_Reason'] = 'Lifetime'
                # Check for failure after activity for relay drone
                if relay_drone['Retired_Day'] is None and FAIL[relay_drone['Subtype']] != float(
                        'inf') and np.random.rand() < FAIL[relay_drone['Subtype']]:
                    relay_drone['Broken_Count'] += 1
                    annual_failures_by_type[current_year][relay_drone['Type']] += 1
                    relay_drone['Repair'] = max(1, int(np.random.normal(*REPAIR['Drone'])))

        # Log battery life for all drones that existed by this day and are not yet retired
        for d in Drone:
            if d['Birth_Day'] <= day and d['Retired_Day'] is None:
                battery_logs[d['ID']].append((day, d['Hours']))
            elif d['Retired_Day'] == day:
                battery_logs[d['ID']].append((day, d['Hours']))

        # Update available counts for the day
        available_counts_history[day]['Drone'] = len(
            [d for d in Drone if
             not d['Crashed'] and d['Repair'] == 0 and d['Hours'] < DRONE_LIFETIME and d['Retired_Day'] is None and d[
                 'Is_Proficient']])
        available_counts_history[day]['Agur'] = len(
            [a for a in Agur if not a['Crashed'] and a['Repair'] == 0 and a['Retired_Day'] is None])
        available_counts_history[day]['Sting'] = len(
            [s for s in Sting if not s['Crashed'] and s['Repair'] == 0 and s['Retired_Day'] is None])

    success_rate = round(100 * summary['Succeeded'] / summary['Planned'], 2) if summary['Planned'] > 0 else 0

    # Prepare data for the annual results table
    annual_results_data = []
    total_percent_executed = 0
    total_replenish_cost = 0
    total_operational_cost_yearly = 0
    total_training_cost_yearly = 0

    total_failures_drone = 0
    total_failures_agur = 0
    total_failures_sting = 0

    total_crashes_drone = 0
    total_crashes_agur = 0
    total_crashes_sting = 0

    for year in range(YEARS):
        missions_planned_yearly = annual_missions_planned[year]
        missions_succeeded_yearly = annual_missions_succeeded[year]

        percent_executed = round(100 * missions_succeeded_yearly / missions_planned_yearly,
                                 2) if missions_planned_yearly > 0 else 0
        replenish_cost = annual_replenish_cost_by_year[year]
        operational_cost = annual_operating_costs_by_type[year].get('Operational', 0) + annual_crash_costs_by_type[
            year].get('Operational', 0)
        training_cost = annual_operating_costs_by_type[year].get('Training', 0) + annual_crash_costs_by_type[year].get(
            'Training', 0)

        failures_drone_yearly = annual_failures_by_type[year].get('Drone', 0)
        failures_agur_yearly = annual_failures_by_type[year].get('Agur', 0)
        failures_sting_yearly = annual_failures_by_type[year].get('Sting', 0)

        crashes_drone_yearly = annual_crashes_by_type[year].get('Drone', 0)
        crashes_agur_yearly = annual_crashes_by_type[year].get('Agur', 0)
        crashes_sting_yearly = annual_crashes_by_type[year].get('Sting', 0)

        annual_results_data.append({
            'שנה': f'שנה {year + 1}',
            'אחוז המשימות שיצאו לפועל': f'{percent_executed:.2f}%',
            'תשלום על ציוד חדש (ש"ח)': f'{replenish_cost:,.2f}',
            'עלות פעילות מבצעית (ש"ח)': f'{operational_cost:,.2f}',
            'עלות אימונים והכשרות (ש"ח)': f'{training_cost:,.2f}',
            'תקלות (רחפן)': failures_drone_yearly,
            'תקלות (עגור)': failures_agur_yearly,
            'תקלות (סטינג)': failures_sting_yearly,
            'התרסקויות (רחפן)': crashes_drone_yearly,
            'התרסקויות (עגור)': crashes_agur_yearly,
            'התרסקויות (סטינג)': crashes_sting_yearly
        })

        total_percent_executed += percent_executed
        total_replenish_cost += replenish_cost
        total_operational_cost_yearly += operational_cost
        total_training_cost_yearly += training_cost

        total_failures_drone += failures_drone_yearly
        total_failures_agur += failures_agur_yearly
        total_failures_sting += failures_sting_yearly

        total_crashes_drone += crashes_drone_yearly
        total_crashes_agur += crashes_agur_yearly
        total_crashes_sting += crashes_sting_yearly

    # Calculate averages
    avg_percent_executed = round(total_percent_executed / YEARS, 2) if YEARS > 0 else 0
    avg_replenish_cost = round(total_replenish_cost / YEARS, 2) if YEARS > 0 else 0
    avg_operational_cost = round(total_operational_cost_yearly / YEARS, 2) if YEARS > 0 else 0
    avg_training_cost = round(total_training_cost_yearly / YEARS, 2) if YEARS > 0 else 0

    avg_failures_drone = round(total_failures_drone / YEARS, 2) if YEARS > 0 else 0
    avg_failures_agur = round(total_failures_agur / YEARS, 2) if YEARS > 0 else 0
    avg_failures_sting = round(total_failures_sting / YEARS, 2) if YEARS > 0 else 0

    avg_crashes_drone = round(total_crashes_drone / YEARS, 2) if YEARS > 0 else 0
    avg_crashes_agur = round(total_crashes_agur / YEARS, 2) if YEARS > 0 else 0
    avg_crashes_sting = round(total_crashes_sting / YEARS, 2) if YEARS > 0 else 0

    annual_results_data.append({
        'שנה': 'ממוצע',
        'אחוז המשימות שיצאו לפועל': f'{avg_percent_executed:.2f}%',
        'תשלום על ציוד חדש (ש"ח)': f'{avg_replenish_cost:,.2f}',
        'עלות פעילות מבצעית (ש"ח)': f'{avg_operational_cost:,.2f}',
        'עלות אימונים והכשרות (ש"ח)': f'{avg_training_cost:,.2f}',
        'תקלות (רחפן)': avg_failures_drone,
        'תקלות (עגור)': avg_failures_agur,
        'תקלות (סטינג)': avg_failures_sting,
        'התרסקויות (רחפן)': avg_crashes_drone,
        'התרסקויות (עגור)': avg_crashes_agur,
        'התרסקויות (סטינג)': avg_crashes_sting
    })

    df_results = pd.DataFrame(annual_results_data)

    # Custom HTML table generation with right-to-left and improved styling

    # Calculate total cost
    total_initial_asset_cost = (INIT['Drone_OP'] + INIT['Drone_TR_PRO']) * COSTS['Drone'] + \
                               INIT['Agur'] * COSTS['Agur'] + INIT['Sting'] * COSTS['Sting']

    # total_replenish_cost = sum(new_assets_added[item_type] * COSTS[item_type] for item_type in new_assets_added) # Now calculated annually

    total_crash_cost = 0
    for year_data in annual_crash_costs_by_type.values():
        total_crash_cost += sum(year_data.values())

    # total_cost = total_crash_cost + total_replenish_cost + total_operating_cost # Recalculate with annual totals
    # annual_cost = total_cost / YEARS if YEARS > 0 else total_cost
    # Calculate new detailed cost summaries
    total_operational_flight_cost = sum(
        sum(annual_operating_costs_by_type[y].get('Operational', 0) for y in annual_operating_costs_by_type.keys()) for
        _ in range(1))
    total_operational_crash_cost = sum(
        sum(annual_crash_costs_by_type[y].get('Operational', 0) for y in annual_crash_costs_by_type.keys()) for _ in
        range(1))
    total_operational_cost = total_operational_flight_cost + total_operational_crash_cost
    # annual_operational_cost = total_operational_cost / YEARS if YEARS > 0 else 0 # Now in table

    total_training_flight_cost = sum(
        sum(annual_operating_costs_by_type[y].get('Training', 0) for y in annual_operating_costs_by_type.keys()) for _
        in range(1))
    total_training_crash_cost = sum(
        sum(annual_crash_costs_by_type[y].get('Training', 0) for y in annual_crash_costs_by_type.keys()) for _ in
        range(1))
    total_training_cost = total_training_flight_cost + total_training_crash_cost

    # annual_training_cost = total_training_cost / YEARS if YEARS > 0 else 0 # Now in table

    # annual_replenish_cost = total_replenish_cost / YEARS if YEARS > 0 else 0 # Now in table

    def plot_battery():
        fig, ax = plt.subplots(figsize=(14, 8))

        # Collect data for all drones
        all_drones_data = []
        for drone_obj in Drone:
            if drone_obj['ID'] in battery_logs:
                all_drones_data.append({
                    'ID': drone_obj['ID'],
                    'Log': battery_logs[drone_obj['ID']],
                    'Retired_Reason': drone_obj['Retired_Reason'],
                    'Retired_Day': drone_obj['Retired_Day']
                })

        # Sort drones by their ID for consistent plotting
        all_drones_data.sort(key=lambda x: x['ID'])

        # Keep track of labels already added to avoid duplicates in legend
        legend_labels = set()

        # Plot each drone's flight hours
        for drone_data in all_drones_data:
            days, hours = zip(*drone_data['Log'])
            ax.plot(days, hours, label=f"Drone {drone_data['ID']}", linewidth=1.5, alpha=0.7)

            # Mark retirement point
            if drone_data['Retired_Day'] is not None and drone_data['Retired_Reason'] is not None:
                retirement_day = drone_data['Retired_Day']
                retirement_hours = next((h for d, h in drone_data['Log'] if d == retirement_day), None)

                if retirement_hours is not None:
                    if drone_data['Retired_Reason'] == 'Crashed':
                        if 'Crashed' not in legend_labels:
                            ax.plot(retirement_day, retirement_hours, 'X', markersize=10, color='red',
                                    markeredgewidth=1.5,
                                    markeredgecolor='black', label='Crashed')
                            legend_labels.add('Crashed')
                        else:
                            ax.plot(retirement_day, retirement_hours, 'X', markersize=10, color='red',
                                    markeredgewidth=1.5,
                                    markeredgecolor='black')
                    elif drone_data['Retired_Reason'] == 'Lifetime':
                        if 'Lifetime Reached' not in legend_labels:
                            ax.plot(retirement_day, retirement_hours, 's', markersize=8, color='purple',
                                    markeredgewidth=1.5,
                                    markeredgecolor='black', label='Lifetime Reached')
                            legend_labels.add('Lifetime Reached')
                        else:
                            ax.plot(retirement_day, retirement_hours, 's', markersize=8, color='purple',
                                    markeredgewidth=1.5,
                                    markeredgecolor='black')

        ax.set_title("Drone Flight Hours and Retirement Causes", fontsize=18, pad=20)
        ax.set_xlabel("Day", fontsize=16)
        ax.set_ylabel("Accumulated Flight Hours", fontsize=16)
        ax.axhline(y=DRONE_LIFETIME, color='gray', linestyle='--', label='Drone Lifetime Limit', alpha=0.8)
        ax.tick_params(axis='both', which='major', labelsize=14)
        # ax.legend(fontsize=12)
        fig.tight_layout()
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=300)
        buf.seek(0)
        plt.close(fig)
        return base64.b64encode(buf.read()).decode('utf-8')

    def plot_summary():
        fig, ax = plt.subplots(figsize=(10, 7))
        bars = ax.bar(['Planned', 'Executed', 'did not occur'],
                      [summary['Planned'], summary['Succeeded'], summary['Failed']],
                      color=['#1f77b4', '#2ca02c', '#d62728'])
        ax.set_title(f"Mission Summary (Executed Rate = {success_rate}%)", fontsize=18, pad=20)
        ax.set_ylabel("Number of Missions", fontsize=16)
        ax.tick_params(axis='both', which='major', labelsize=14)
        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, yval + 0.1, int(yval), ha='center', va='bottom',
                    fontsize=12)
        fig.tight_layout()
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=300)
        buf.seek(0)
        plt.close(fig)
        return base64.b64encode(buf.read()).decode('utf-8')

    def plot_available_devices():
        fig, ax = plt.subplots(figsize=(14, 8))
        device_types = ['Drone', 'Agur', 'Sting']

        days_list = sorted(list(available_counts_history.keys()))
        if not days_list:
            ax.set_title("No Device Availability Data", fontsize=18, pad=20)
            ax.set_xlabel("Day", fontsize=16)
            ax.set_ylabel("Number of Devices", fontsize=16)
            buf = io.BytesIO()
            fig.tight_layout()
            fig.savefig(buf, format='png', dpi=300)
            buf.seek(0)
            plt.close(fig)
            return base64.b64encode(buf.read()).decode('utf-8')

        legend_labels = set()

        for device_type in device_types:
            english_device_type = {
                'Drone': 'Drones (Proficient)',
                'Agur': 'Agur',
                'Sting': 'Sting'
            }.get(device_type, device_type)

            counts = [available_counts_history[day][device_type] for day in days_list]
            ax.plot(days_list, counts, label=f'{english_device_type} Available', linewidth=2.5)

            # Add crash markers
            for day_val in crash_markers:
                if device_type in crash_markers[day_val]:
                    current_count = available_counts_history[day_val].get(device_type, 0)
                    if 'Crash' not in legend_labels:
                        ax.plot(day_val, current_count, 'X', color='red', markersize=8, markeredgewidth=1,
                                markeredgecolor='black', label='Crash')
                        legend_labels.add('Crash')
                    else:
                        ax.plot(day_val, current_count, 'X', color='red', markersize=8, markeredgewidth=1,
                                markeredgecolor='black')

            # Add replenishment markers
            for day_val in replenish_markers:
                if device_type in replenish_markers[day_val]:
                    current_count = available_counts_history[day_val].get(device_type, 0)
                    if 'New Asset' not in legend_labels:
                        ax.plot(day_val, current_count, 'o', color='green', markersize=8, markeredgewidth=1,
                                markeredgecolor='black', label='New Asset')
                        legend_labels.add('New Asset')
                    else:
                        ax.plot(day_val, current_count, 'o', color='green', markersize=8, markeredgewidth=1,
                                markeredgecolor='black')

        ax.set_title("Number of Available Assets Over Time", fontsize=18, pad=20)
        ax.set_xlabel("Day", fontsize=16)
        ax.set_ylabel("Number of Assets", fontsize=16)
        ax.tick_params(axis='both', which='major', labelsize=14)
        ax.legend(fontsize=14)
        ax.grid(True, linestyle='--', alpha=0.7)
        fig.tight_layout()
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=300)
        buf.seek(0)
        plt.close(fig)
        return base64.b64encode(buf.read()).decode('utf-8')

    def plot_asset_status_summary():
        fig, ax = plt.subplots(figsize=(12, 7))

        final_status = defaultdict(lambda: defaultdict(int))

        # Categorize Drones
        for d in Drone:
            if d['Crashed']:
                final_status['Drone']['Crashed'] += 1
            elif d['Retired_Reason'] == 'Lifetime':
                final_status['Drone']['Retired (Lifetime)'] += 1
            else:
                final_status['Drone']['In Stock'] += 1

        # Categorize Agur
        for a in Agur:
            if a['Crashed']:
                final_status['Agur']['Crashed'] += 1
            elif a['Retired_Reason'] == 'Lifetime':
                final_status['Agur']['Retired (Lifetime)'] += 1
            else:
                final_status['Agur']['In Stock'] += 1

        # Categorize Sting
        for s in Sting:
            if s['Crashed']:
                final_status['Sting']['Crashed'] += 1
            elif s['Retired_Reason'] == 'Lifetime':
                final_status['Sting']['Retired (Lifetime)'] += 1
            else:
                final_status['Sting']['In Stock'] += 1

        # Prepare data for plotting
        asset_types = ['Drone', 'Agur', 'Sting']
        status_categories = ['In Stock', 'Crashed', 'Retired (Lifetime)']

        bottoms = np.zeros(len(asset_types))

        colors = {'In Stock': '#2ca02c', 'Crashed': '#d62728', 'Retired (Lifetime)': '#ff7f0e'}

        for category in status_categories:
            counts = [final_status[a_type][category] for a_type in asset_types]
            bars = ax.bar(asset_types, counts, bottom=bottoms, label=category, color=colors[category])
            for i, bar in enumerate(bars):
                height = bar.get_height()
                if height > 0:
                    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_y() + height / 2,
                            f'{int(height)}', ha='center', va='center', color='white', fontsize=12)
            bottoms += np.array(counts)

        ax.set_title("Asset Status Summary at End of Simulation", fontsize=18, pad=20)
        ax.set_xlabel("Asset Type", fontsize=16)
        ax.set_ylabel("Number of Assets", fontsize=16)
        ax.tick_params(axis='both', which='major', labelsize=14)
        ax.legend(fontsize=12, loc='upper left')
        ax.grid(axis='y', linestyle='--', alpha=0.7)

        fig.tight_layout()
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=300)
        buf.seek(0)
        plt.close(fig)
        return base64.b64encode(buf.read()).decode('utf-8')

    def plot_annual_costs_and_hours():
        fig, axs = plt.subplots(2, 1, figsize=(14, 12), sharex=True)

        years = sorted(list(annual_flight_hours_by_type.keys()))
        if not years:
            axs[0].set_title("No Annual Data", fontsize=18, pad=20)
            axs[1].set_xlabel("Year", fontsize=16)
            axs[0].set_ylabel("Hours", fontsize=16)
            axs[1].set_ylabel("Cost (NIS)", fontsize=16)
            buf = io.BytesIO()
            fig.tight_layout()
            fig.savefig(buf, format='png', dpi=300)
            buf.seek(0)
            plt.close(fig)
            return base64.b64encode(buf.read()).decode('utf-8')

        # Plot 1: Annual Flight Hours
        op_hours = [annual_flight_hours_by_type[y].get('Operational', 0) for y in years]
        tr_hours = [annual_flight_hours_by_type[y].get('Training', 0) for y in years]

        bar_width = 0.35
        x = np.arange(len(years))

        axs[0].bar(x - bar_width / 2, op_hours, bar_width, label='Operational Flight Hours', color='skyblue')
        axs[0].bar(x + bar_width / 2, tr_hours, bar_width, label='Training/Proficiency Flight Hours',
                   color='lightcoral')
        axs[0].set_ylabel("Annual Flight Hours (Drones)", fontsize=16)
        axs[0].set_title("Annual Drone Flight Hours by Activity Type", fontsize=18, pad=20)
        axs[0].legend(fontsize=12)
        axs[0].grid(axis='y', linestyle='--', alpha=0.7)
        axs[0].tick_params(axis='y', which='major', labelsize=12)

        # Plot 2: Annual Costs
        op_operating_costs = [annual_operating_costs_by_type[y].get('Operational', 0) for y in years]
        tr_operating_costs = [annual_operating_costs_by_type[y].get('Training', 0) for y in years]
        crash_costs_op = [annual_crash_costs_by_type[y].get('Operational', 0) for y in years]
        crash_costs_tr = [annual_crash_costs_by_type[y].get('Training', 0) for y in years]

        total_op_costs = np.array(op_operating_costs) + np.array(crash_costs_op)
        total_tr_costs = np.array(tr_operating_costs) + np.array(crash_costs_tr)

        axs[1].bar(x - bar_width / 2, op_operating_costs, bar_width, label='Operational Cost (Flight)',
                   color='darkblue')
        axs[1].bar(x - bar_width / 2, crash_costs_op, bar_width, bottom=op_operating_costs,
                   label='Operational Crash Cost', color='red', hatch='/')

        axs[1].bar(x + bar_width / 2, tr_operating_costs, bar_width, label='Training/Proficiency Cost (Flight)',
                   color='darkgreen')
        axs[1].bar(x + bar_width / 2, crash_costs_tr, bar_width, bottom=tr_operating_costs, label='Training Crash Cost',
                   color='maroon', hatch='x')

        axs[1].set_xlabel("Year", fontsize=16)
        axs[1].set_ylabel("Annual Cost (NIS)", fontsize=16)
        axs[1].set_title("Annual Drone Costs by Activity Type and Crashes", fontsize=18, pad=20)
        axs[1].set_xticks(x)
        axs[1].set_xticklabels([f'Year {y + 1}' for y in years], fontsize=14)
        axs[1].legend(fontsize=12, loc='upper left')
        axs[1].grid(axis='y', linestyle='--', alpha=0.7)
        axs[1].tick_params(axis='y', which='major', labelsize=12)
        axs[1].ticklabel_format(style='plain', axis='y')

        fig.tight_layout()
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=300)
        buf.seek(0)
        plt.close(fig)
        return base64.b64encode(buf.read()).decode('utf-8')

    return render_template_string(result_template,
                                  graph1=plot_battery(),
                                  graph2=plot_summary(),
                                  graph3=plot_available_devices(),
                                  graph4=plot_annual_costs_and_hours(),
                                  graph5=plot_asset_status_summary(),
                                  results_table=df_results.to_html(classes='table', index=False, escape=False))


if __name__ == '__main__':
    app.run(debug=True)