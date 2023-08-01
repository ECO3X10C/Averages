from flask import Flask, render_template, request, redirect, url_for, session
import json
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'


def load_user_data():
    if not os.path.exists('users.json'):
        return {}
    with open('users.json', 'r') as file:
        return json.load(file)


def save_user_data(users_data):
    with open('users.json', 'w') as file:
        json.dump(users_data, file)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        first_name = request.form['first_name']

        users_data = load_user_data()
        users_data[username] = {
            'password': password,
            'first_name': first_name,
        }
        save_user_data(users_data)

        return redirect(url_for('login'))

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        users_data = load_user_data()

        if username in users_data and users_data[username]['password'] == password:
            session['username'] = username
            return redirect(url_for('dashboard'))

        return render_template('login.html', error_message='Invalid username or password')

    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    with open('course_data.json', 'r') as file:
        course_data = json.load(file)
    user_courses = course_data.get(session['username'], [])

    return render_template('dashboard.html', courses=user_courses)


@app.route('/course/<course_name>', methods=['GET', 'POST'])
def course(course_name):
    if 'username' not in session:
        return redirect(url_for('login'))

    with open('course_data.json', 'r') as file:
        course_data = json.load(file)
    user_courses = course_data.get(session['username'], [])

    selected_course = None
    for course in user_courses:
        if course['course_name'] == course_name:
            selected_course = course
            break

    if selected_course is None:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        unit_name = request.form['unit_name']
        unit_weight = int(request.form['unit_weight'])
        assignment_types = request.form.getlist('assignment_type[]')
        assignment_marks_achieved = [int(mark) for mark in request.form.getlist('assignment_mark_achieved[]')]
        assignment_max_marks = [int(max_mark) for max_mark in request.form.getlist('assignment_maximum_mark[]')]
        assignment_weights = [int(weight) for weight in request.form.getlist('assignment_weight[]')]

        # Create a list of assignments for the unit
        assignments = []
        for i in range(len(assignment_types)):
            assignments.append({
                'assignment_type': assignment_types[i],
                'assignment_mark_achieved': assignment_marks_achieved[i],
                'assignment_maximum_mark': assignment_max_marks[i],
                'assignment_weight': assignment_weights[i],
            })

        # Create the unit exam data
        unit_exam_mark = int(request.form['unit_exam_mark'])
        unit_exam_mark_achieved = int(request.form['unit_exam_mark_achieved'])
        unit_exam_weight = int(request.form['unit_exam_weight'])

        # Create the unit data
        unit_data = {
            'unit_name': unit_name,
            'unit_weight': unit_weight,
            'unit_exam': {
                'unit_exam_mark': unit_exam_mark,
                'unit_exam_mark_achieved': unit_exam_mark_achieved,
                'unit_exam_weight': unit_exam_weight,
            },
            'assignments': assignments,
        }

        # Append the new unit data to the selected course
        selected_course['units'].append(unit_data)

        # Save the updated course data
        with open('course_data.json', 'w') as file:
            json.dump(course_data, file)

        return redirect(url_for('course', course_name=course_name))

    return render_template('course.html', course=selected_course)

@app.route('/logout')
def logout():
    # Remove the 'username' key from the session to log the user out
    session.pop('username', None)
    return redirect(url_for('home'))


@app.route('/create_course', methods=['GET', 'POST'])
def create_course():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        course_name = request.form['course_name']

        # Load the existing course data for the logged-in user
        with open('course_data.json', 'r') as file:
            course_data = json.load(file)

        # Check if the logged-in user already has courses
        user_courses = course_data.get(session['username'], [])
        for course in user_courses:
            if course['course_name'] == course_name:
                return render_template('create_course.html', error_message='Course name already exists.')

        # If the course name is unique, add the new course
        user_courses.append({'course_name': course_name, 'units': []})
        course_data[session['username']] = user_courses

        # Save the updated course data
        with open('course_data.json', 'w') as file:
            json.dump(course_data, file)

        return redirect(url_for('dashboard'))

    return render_template('create_course.html')

@app.route('/course/<course_name>/edit/<unit_name>', methods=['GET', 'POST'])
def edit_unit(course_name, unit_name):
    if 'username' not in session:
        return redirect(url_for('login'))

    with open('course_data.json', 'r') as file:
        course_data = json.load(file)
    user_courses = course_data.get(session['username'], [])

    selected_course = None
    for course in user_courses:
        if course['course_name'] == course_name:
            selected_course = course
            break

    if selected_course is None:
        return redirect(url_for('dashboard'))

    selected_unit = None
    for unit in selected_course['units']:
        if unit['unit_name'] == unit_name:
            selected_unit = unit
            break

    if selected_unit is None:
        return redirect(url_for('course', course_name=course_name))

    if request.method == 'POST':
        # Update the unit details based on the form submission
        selected_unit['unit_name'] = request.form['unit_name']
        selected_unit['unit_weight'] = int(request.form['unit_weight'])

        # Update the assignment details (if applicable)
        num_assignments = int(request.form['num_assignments'])
        assignments = []
        for i in range(num_assignments):
            assignment_type = request.form[f'assignment_type_{i}']
            assignment_mark_achieved = int(request.form[f'assignment_mark_achieved_{i}'])
            assignment_maximum_mark = int(request.form[f'assignment_maximum_mark_{i}'])
            assignment_weight = int(request.form[f'assignment_weight_{i}'])

            assignments.append({
                'assignment_type': assignment_type,
                'assignment_mark_achieved': assignment_mark_achieved,
                'assignment_maximum_mark': assignment_maximum_mark,
                'assignment_weight': assignment_weight,
            })

        # Update the assignments for the selected unit
        selected_unit['assignments'] = assignments

        # Save the updated course data
        with open('course_data.json', 'w') as file:
            json.dump(course_data, file)

        return redirect(url_for('course', course_name=course_name))

    return render_template('edit_unit.html', course=selected_course, unit=selected_unit)

@app.route('/course/<course_name>/delete/<unit_name>', methods=['POST'])
def delete_unit(course_name, unit_name):
    if 'username' not in session:
        return redirect(url_for('login'))

    with open('course_data.json', 'r') as file:
        course_data = json.load(file)
    user_courses = course_data.get(session['username'], [])

    selected_course = None
    for course in user_courses:
        if course['course_name'] == course_name:
            selected_course = course
            break

    if selected_course is None:
        return redirect(url_for('dashboard'))

    for unit in selected_course['units']:
        if unit['unit_name'] == unit_name:
            selected_course['units'].remove(unit)
            break

    # Save the updated course data
    with open('course_data.json', 'w') as file:
        json.dump(course_data, file)

    return redirect(url_for('course', course_name=course_name))
if __name__ == "__main__":
    app.run(debug=True)















if __name__ == "__main__":
    app.run(debug=True)
