from flask import Flask, render_template, request, redirect, url_for, flash
import json
from jinja2 import Environment

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Custom Jinja2 filter for 'enumerate'
def enumerate_filter(iterable, start=0):
    return enumerate(iterable, start=start)

# Adding the 'enumerate' filter to Jinja2 environment
env = Environment()
env.filters['enumerate'] = enumerate_filter
# Sample user data (You should use a proper database for a real-world application)
users = {
    'user1': {'password': 'password1', 'courses': {}},
    'user2': {'password': 'password2', 'courses': {}}
}

def save_users_data():
    with open('users.json', 'w') as f:
        json.dump(users, f)

def load_users_data():
    try:
        with open('users.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if users.get(username) and users[username]['password'] == password:
            return redirect(url_for('dashboard', username=username))
        else:
            flash('Invalid credentials! Please try again.', 'error')
    return render_template('login.html')

@app.route('/dashboard/<username>', methods=['GET', 'POST'])
def dashboard(username):
    user = users.get(username)
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        course_name = request.form['course_name']
        courses = user.setdefault('courses', {})
        if course_name not in courses:
            courses[course_name] = []

        save_users_data()
        flash(f'Course "{course_name}" created successfully!', 'success')

    return render_template('dashboard.html', username=username, courses=user.get('courses').keys())

# ... (previous code)

# ... (previous code)

@app.route('/course/<username>/<course_name>', methods=['GET', 'POST'])
def course(username, course_name):
    user = users.get(username)
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('login'))

    course = user['courses'].get(course_name)


    if request.method == 'POST':
        unit_name = request.form['unit_name']
        assignments = [value for key, value in request.form.items() if key.startswith('assignments_')]
        final = request.form['final']

        course.append({
            'unit_name': unit_name,
            'assignments': assignments,
            'final': final
        })

        save_users_data()
        flash('Unit added successfully!', 'success')

    return render_template('course.html', username=username, course_name=course_name, units=course)



@app.route('/create_course/<username>', methods=['POST'])
def create_course(username):
    course_name = request.form['course_name']
    user = users.get(username)
    if user:
        courses = user.setdefault('courses', {})
        if course_name not in courses:
            courses[course_name] = []

        save_users_data()
        flash(f'Course "{course_name}" created successfully!', 'success')

    return redirect(url_for('dashboard', username=username))

# ... (previous code)

@app.route('/add_unit/<username>/<course_name>', methods=['POST'])
def add_unit(username, course_name):
    unit_name = request.form['unit_name']
    assignments = [value for key, value in request.form.items() if key.startswith('assignments_')]
    final = request.form['final']

    user = users.get(username)
    if user:
        courses = user['courses']
        if course_name not in courses:
            courses[course_name] = []

        courses[course_name].append({
            'unit_name': unit_name,
            'assignments': assignments,
            'final': final
        })

        save_users_data()
        flash('Unit added successfully!', 'success')

    return redirect(url_for('course', username=username, course_name=course_name))

# ... (previous code)

@app.route('/delete_course/<username>/<course_name>', methods=['POST'])
def delete_course(username, course_name):
    user = users.get(username)
    if user:
        if course_name in user['courses']:
            del user['courses'][course_name]
            save_users_data()
            flash(f'Course "{course_name}" and all its units deleted successfully!', 'success')
    return redirect(url_for('dashboard', username=username))

@app.route('/edit_unit/<username>/<course_name>/<unit_name>', methods=['POST'])
def edit_unit(username, course_name, unit_name):
    user = users.get(username)
    if user:
        course = user['courses'].get(course_name)
        if course:
            for unit in course:
                if unit['unit_name'] == unit_name:
                    unit['unit_name'] = request.form['unit_name']
                    unit['assignments'] = [value for key, value in request.form.items() if key.startswith('assignments_')]
                    unit['final'] = request.form['final']
                    save_users_data()
                    flash('Unit edited successfully!', 'success')
                    break
    return redirect(url_for('course', username=username, course_name=course_name))

@app.route('/delete_unit/<username>/<course_name>/<unit_name>', methods=['POST'])
def delete_unit(username, course_name, unit_name):
    user = users.get(username)
    if user:
        course = user['courses'].get(course_name)
        if course:
            for unit in course:
                if unit['unit_name'] == unit_name:
                    course.remove(unit)
                    save_users_data()
                    flash('Unit deleted successfully!', 'success')
                    break
    return redirect(url_for('course', username=username, course_name=course_name))

if __name__ == '__main__':
    users = load_users_data()
    app.run(debug=True)
