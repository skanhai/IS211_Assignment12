from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3


#http://127.0.0.1:5000/login
#http://127.0.0.1:5000/dashboard
#http://127.0.0.1:5000/student/add
#http://127.0.0.1:5000/quiz/add
#http://127.0.0.1:5000/results/add
#http://127.0.0.1:5000/quiz/1/results/


app = Flask(__name__)
app.secret_key = 'supersecretkey'




def initialize_database():
    conn = sqlite3.connect('hw13.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Students (
            id INTEGER PRIMARY KEY,
            first_name TEXT,
            last_name TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Quizzes (
            id INTEGER PRIMARY KEY,
            subject TEXT,
            num_questions INTEGER,
            quiz_date TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS QuizResults (
            id INTEGER PRIMARY KEY,
            student_id INTEGER,
            quiz_id INTEGER,
            score INTEGER,
            FOREIGN KEY(student_id) REFERENCES Students(id),
            FOREIGN KEY(quiz_id) REFERENCES Quizzes(id)
        )
    ''')

    conn.commit()
    conn.close()


initialize_database()




@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == 'admin' and password == 'password':
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
            return render_template('login.html')
    else:
        return render_template('login.html')




@app.route('/dashboard')
def dashboard():
    conn = sqlite3.connect('hw13.db')
    cursor = conn.cursor()

    cursor.execute('SELECT id, first_name, last_name FROM Students')
    students = cursor.fetchall()

    cursor.execute('SELECT id, subject, num_questions, quiz_date FROM Quizzes')
    quizzes = cursor.fetchall()

    conn.close()

    return render_template('dashboard.html', students=students, quizzes=quizzes)




@app.route('/student/add', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']

        conn = sqlite3.connect('hw13.db')
        cursor = conn.cursor()

        cursor.execute('INSERT INTO Students (first_name, last_name) VALUES (?, ?)', (first_name, last_name))
        conn.commit()

        conn.close()

        flash('Student added successfully', 'success')

        return redirect(url_for('dashboard'))
    else:
        return render_template('add_student.html')



@app.route('/quiz/add', methods=['GET', 'POST'])
def add_quiz():
    if request.method == 'POST':
        subject = request.form['subject']
        num_questions = request.form['num_questions']
        quiz_date = request.form['quiz_date']

        conn = sqlite3.connect('hw13.db')
        cursor = conn.cursor()

        cursor.execute('INSERT INTO Quizzes (subject, num_questions, quiz_date) VALUES (?, ?, ?)',
                       (subject, num_questions, quiz_date))
        conn.commit()

        conn.close()

        flash('Quiz added successfully', 'success')

        return redirect(url_for('dashboard'))
    else:
        return render_template('add_quiz.html')



@app.route('/student/<int:id>')
def view_student_results(id):
    conn = sqlite3.connect('hw13.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT Quizzes.id, Quizzes.subject, Quizzes.quiz_date, QuizResults.score 
        FROM Quizzes 
        JOIN QuizResults ON Quizzes.id = QuizResults.quiz_id 
        WHERE QuizResults.student_id = ?
    ''', (id,))
    quiz_results = cursor.fetchall()

    conn.close()

    if not quiz_results:
        return "No Results"
    else:
        return render_template('student_results.html', quiz_results=quiz_results, logged_in=True)



@app.route('/results/add', methods=['GET', 'POST'])
def add_quiz_result():
    if request.method == 'POST':
        student_id = request.form['student_id']
        quiz_id = request.form['quiz_id']
        score = request.form['score']

        conn = sqlite3.connect('hw13.db')
        cursor = conn.cursor()

        cursor.execute('INSERT INTO QuizResults (student_id, quiz_id, score) VALUES (?, ?, ?)',
                       (student_id, quiz_id, score))
        conn.commit()

        conn.close()

        flash('Quiz result added successfully', 'success')

        return redirect(url_for('dashboard'))
    else:
        conn = sqlite3.connect('hw13.db')
        cursor = conn.cursor()

        cursor.execute('SELECT id, first_name, last_name FROM Students')
        students = cursor.fetchall()

        cursor.execute('SELECT id, subject FROM Quizzes')
        quizzes = cursor.fetchall()

        conn.close()

        return render_template('add_quiz_result.html', students=students, quizzes=quizzes)




@app.route('/student/delete/<int:id>', methods=['POST'])
def delete_student(id):
    if request.method == 'POST':
        try:
            conn = sqlite3.connect('hw13.db')
            cursor = conn.cursor()


            cursor.execute('DELETE FROM QuizResults WHERE student_id = ?', (id,))


            cursor.execute('DELETE FROM Students WHERE id = ?', (id,))

            conn.commit()
            flash('Student and their quiz results deleted successfully', 'success')
        except sqlite3.Error as e:
            print("An error occurred:", e)
            flash('An error occurred while deleting the student and their quiz results', 'error')
            conn.rollback()
        finally:
            conn.close()

        return redirect(url_for('dashboard'))


@app.route('/quiz/delete/<int:id>', methods=['POST'])
def delete_quiz(id):
    if request.method == 'POST':
        conn = sqlite3.connect('hw13.db')
        cursor = conn.cursor()

        cursor.execute('DELETE FROM Quizzes WHERE id = ?', (id,))
        conn.commit()

        conn.close()

        flash('Quiz deleted successfully', 'success')

        return redirect(url_for('dashboard'))


@app.route('/result/delete/<int:id>', methods=['POST'])
def delete_result(id):
    if request.method == 'POST':
        try:
            conn = sqlite3.connect('hw13.db')
            cursor = conn.cursor()

            result_id = request.form.get('result_id_{}'.format(request.form['index']))

            if result_id:
                cursor.execute('DELETE FROM QuizResults WHERE id = ?', (result_id,))
                conn.commit()
                flash('Quiz result deleted successfully', 'success')
            else:
                flash('No result ID found in the form data', 'error')
        except sqlite3.Error as e:
            print("An error occurred:", e)
            flash('An error occurred while deleting the quiz result', 'error')
            conn.rollback()
        finally:
            conn.close()

        return redirect(url_for('dashboard'))



@app.route('/quiz/<int:id>/results/')
def view_quiz_results_anonymous(id):
    conn = sqlite3.connect('hw13.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT student_id, score FROM QuizResults WHERE quiz_id = ?
    ''', (id,))
    quiz_results = cursor.fetchall()

    conn.close()

    return render_template('quiz_results_anonymous.html', quiz_results=quiz_results)



def get_student_name(student_id):
    conn = sqlite3.connect('hw13.db')
    cursor = conn.cursor()

    cursor.execute('SELECT first_name, last_name FROM Students WHERE id = ?', (student_id,))
    student = cursor.fetchone()

    conn.close()

    if student:
        return f"{student[0]} {student[1]}"
    else:
        return "Unknown"


if __name__ == '__main__':
    app.run(debug=True)
