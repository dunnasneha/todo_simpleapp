import datetime
import os
import sqlite3
import uuid

from flask import Flask, g, jsonify, request, send_from_directory

app = Flask(__name__, static_folder='.', static_url_path='')
DATABASE = os.path.join(app.root_path, 'tasks.db')


# ─── Database helpers ──────────────────────────────────────────────────────────

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
        g._database = db
    return db


@app.teardown_appcontext
def close_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def init_db():
    """Create tables if they don't exist yet."""
    with app.app_context():
        db = get_db()
        db.execute(
            '''
            CREATE TABLE IF NOT EXISTS tasks (
                id        TEXT PRIMARY KEY,
                text      TEXT NOT NULL,
                done      INTEGER NOT NULL DEFAULT 0,
                createdAt TEXT NOT NULL
            )
            '''
        )
        db.commit()


def task_to_dict(row):
    return {
        'id':        row['id'],
        'text':      row['text'],
        'done':      bool(row['done']),
        'createdAt': row['createdAt'],
    }


# ─── CORS (handy when the frontend is served on a different port in dev) ───────

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin']  = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response


@app.route('/api/tasks', methods=['OPTIONS'])
@app.route('/api/tasks/<task_id>', methods=['OPTIONS'])
def options_handler(task_id=None):
    return '', 204


# ─── Routes ────────────────────────────────────────────────────────────────────

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    db   = get_db()
    rows = db.execute('SELECT * FROM tasks ORDER BY createdAt DESC').fetchall()
    return jsonify([task_to_dict(row) for row in rows])


@app.route('/api/tasks', methods=['POST'])
def create_task():
    data = request.get_json(silent=True) or {}
    text = data.get('text', '')
    if not isinstance(text, str) or not text.strip():
        return jsonify({'error': 'Task text is required'}), 400

    task_id    = uuid.uuid4().hex
    created_at = datetime.datetime.now(datetime.timezone.utc).isoformat().replace('+00:00', 'Z')
    db         = get_db()
    db.execute(
        'INSERT INTO tasks (id, text, done, createdAt) VALUES (?, ?, 0, ?)',
        (task_id, text.strip(), created_at),
    )
    db.commit()

    return jsonify({
        'id':        task_id,
        'text':      text.strip(),
        'done':      False,
        'createdAt': created_at,
    }), 201


@app.route('/api/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    data    = request.get_json(silent=True) or {}
    updates = []
    params  = []

    if 'text' in data:
        text = data.get('text')
        if not isinstance(text, str) or not text.strip():
            return jsonify({'error': 'Task text must be a non-empty string'}), 400
        updates.append('text = ?')
        params.append(text.strip())

    if 'done' in data:
        done = data.get('done')
        if not isinstance(done, bool):
            return jsonify({'error': 'Done must be true or false'}), 400
        updates.append('done = ?')
        params.append(1 if done else 0)

    if not updates:
        return jsonify({'error': 'No valid task fields provided'}), 400

    params.append(task_id)
    db     = get_db()
    cursor = db.execute(f'UPDATE tasks SET {", ".join(updates)} WHERE id = ?', params)
    db.commit()

    if cursor.rowcount == 0:
        return jsonify({'error': 'Task not found'}), 404

    # Return the full, up-to-date task object (not just the changed fields)
    row = db.execute('SELECT * FROM tasks WHERE id = ?', (task_id,)).fetchone()
    return jsonify(task_to_dict(row))


@app.route('/api/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    db     = get_db()
    cursor = db.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    db.commit()
    if cursor.rowcount == 0:
        return jsonify({'error': 'Task not found'}), 404
    return '', 204


@app.route('/api/tasks', methods=['DELETE'])
def clear_done_tasks():
    if request.args.get('done') != 'true':
        return jsonify({'error': 'Unknown delete action'}), 400
    db = get_db()
    db.execute('DELETE FROM tasks WHERE done = 1')
    db.commit()
    return '', 204


@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')


# ─── Entry point ───────────────────────────────────────────────────────────────

# Initialise the DB here so it works whether you use `python app.py`
# OR a WSGI server (gunicorn, uWSGI, etc.) that never hits __main__.
init_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
