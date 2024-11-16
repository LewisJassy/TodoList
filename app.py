from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from model import Todo, db, LoginForm, SignUpForm
from flask_wtf.csrf import CSRFProtect

def create_app():
    app = Flask(__name__, static_folder='static')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'lewis'
    app.config['WTF_CSRF_TIME_LIMIT'] = 3600  # Set CSRF token expiration to 1 hour
    csrf = CSRFProtect(app)
    db.init_app(app)

    @app.route('/static/<path:filename>')
    def static_files(filename):
        return send_from_directory('static', filename)

    @app.route('/')
    def index():
        if 'user' not in session:
            return redirect(url_for('signup'))
        todo_list = Todo.query.all()
        return render_template('base.html', todo_list=todo_list)

    @app.route('/add', methods=['POST'])
    def add_todo():
        title = request.form.get('title')
        new_todo = Todo(title=title, complete=False)
        db.session.add(new_todo)
        db.session.commit()
        return redirect(url_for('index'))

    @app.route('/update/<int:todo_id>')
    def update_todo(todo_id):
        todo = Todo.query.filter_by(id=todo_id).first()
        todo.complete = not todo.complete
        db.session.commit()
        return redirect(url_for('index'))

    @app.route('/delete/<int:todo_id>', methods=['POST'])
    def delete_todo(todo_id):
        todo = Todo.query.filter_by(id=todo_id).first()
        db.session.delete(todo)
        db.session.commit()
        return redirect(url_for('index'))

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            session['user'] = form.username.data
            flash('Login successful', 'success')
            return redirect(url_for('index'))
        return render_template('login.html', form=form)

    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        form = SignUpForm()
        if form.validate_on_submit():
            session['user'] = form.username.data
            flash('Sign-up successful!', 'success')
            return redirect(url_for('index'))
        return render_template('signup.html', form=form)

    @app.route('/logout')
    def logout():
        session.pop('user', None)
        flash('You have been logged out.', 'success')
        return redirect(url_for('index'))

    with app.app_context():
        db.create_all()

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)