from flask import Flask, request, render_template, redirect
import sqlite3
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "words.db")


def db():
    conn = sqlite3.connect(DB_PATH)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS words(
        id INTEGER PRIMARY KEY,
        word TEXT UNIQUE,
        meaning TEXT,
        learned INTEGER DEFAULT 0,
        review_count INTEGER DEFAULT 0
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS lessons(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL
    )
    """)

    # تحديث قاعدة البيانات القديمة إذا كانت review_count غير موجودة
    columns = [row[1] for row in conn.execute("PRAGMA table_info(words)")]

    if "review_count" not in columns:
        conn.execute(
            "ALTER TABLE words ADD COLUMN review_count INTEGER DEFAULT 0"
        )

    conn.commit()
    return conn


@app.route("/", methods=["GET", "POST"])
def home():
    conn = db()
    msg = ""

    if request.method == "POST":
        word = request.form["word"].strip().lower()
        meaning = request.form["meaning"].strip()

        try:
            conn.execute(
                "INSERT INTO words(word, meaning) VALUES(?, ?)",
                (word, meaning)
            )
            conn.commit()
            msg = "✅ تم حفظ الكلمة"
        except sqlite3.IntegrityError:
            msg = "⚠️ الكلمة موجودة مسبقاً"

    words = conn.execute(
        "SELECT * FROM words ORDER BY id DESC"
    ).fetchall()

    conn.close()

    return render_template(
        "home.html",
        words=words,
        count=len(words),
        msg=msg
    )


@app.route("/review")
def review():
    conn = db()

    word = conn.execute("""
        SELECT word, meaning
        FROM words
        ORDER BY review_count ASC, RANDOM()
        LIMIT 1
    """).fetchone()

    conn.close()

    if word is None:
        return "لا توجد كلمات محفوظة"

    return render_template(
        "review.html",
        word=word[0],
        meaning=word[1]
    )


@app.route("/know", methods=["POST"])
def know():
    word = request.form["word"]

    conn = db()

    conn.execute(
        "UPDATE words SET learned=1 WHERE word=?",
        (word,)
    )

    conn.commit()
    conn.close()

    return redirect("/review")


@app.route("/again", methods=["POST"])
def again():
    word = request.form["word"]

    conn = db()

    conn.execute(
        "UPDATE words SET review_count = review_count + 1 WHERE word=?",
        (word,)
    )

    conn.commit()
    conn.close()

    return redirect("/review")


@app.route("/stats")
def stats():
    conn = db()

    total = conn.execute(
        "SELECT COUNT(*) FROM words"
    ).fetchone()[0]

    learned = conn.execute(
        "SELECT COUNT(*) FROM words WHERE learned=1"
    ).fetchone()[0]

    need = total - learned

    conn.close()

    return render_template(
        "stats.html",
        total=total,
        learned=learned,
        need=need
    )


@app.route("/search")
def search():
    q = request.args.get("q", "").strip()

    conn = db()

    words = conn.execute(
        "SELECT word, meaning FROM words WHERE word LIKE ?",
        (f"%{q}%",)
    ).fetchall()

    conn.close()

    return render_template(
        "search.html",
        q=q,
        words=words
    )


@app.route("/delete/<word>")
def delete(word):
    conn = db()

    conn.execute(
        "DELETE FROM words WHERE word=?",
        (word,)
    )

    conn.commit()
    conn.close()

    return redirect("/")


@app.route("/edit/<word>")
def edit(word):
    conn = db()

    item = conn.execute(
        "SELECT word, meaning FROM words WHERE word=?",
        (word,)
    ).fetchone()

    conn.close()

    return render_template(
        "edit.html",
        item=item
    )


@app.route("/update", methods=["POST"])
def update():
    old_word = request.form["old_word"]
    word = request.form["word"]
    meaning = request.form["meaning"]

    conn = db()

    conn.execute(
        "UPDATE words SET word=?, meaning=? WHERE word=?",
        (word, meaning, old_word)
    )

    conn.commit()
    conn.close()

    return redirect("/")


@app.route("/lessons")
def lessons():
    conn = db()

    lessons = conn.execute(
        "SELECT id, title FROM lessons ORDER BY id"
    ).fetchall()

    conn.close()

    return render_template(
        "lessons.html",
        lessons=lessons
    )


@app.route("/quiz")
def quiz():
    conn = db()

    word = conn.execute(
        "SELECT word, meaning FROM words ORDER BY RANDOM() LIMIT 1"
    ).fetchone()

    conn.close()

    if word is None:
        return "لا توجد كلمات"

    return render_template(
        "quiz.html",
        word=word[0],
        meaning=word[1]
    )


@app.route("/check", methods=["POST"])
def check():
    answer = request.form["answer"].strip().lower()
    correct = request.form["correct"].strip().lower()

    if answer == correct:
        result = "✅ إجابة صحيحة"
    else:
        result = f"❌ خطأ، الإجابة الصحيحة هي: {correct}"

    return render_template(
        "result.html",
        result=result
    )


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        word = request.form["word"].strip().lower()
        meaning = request.form["meaning"].strip()

        conn = db()

        try:
            conn.execute(
                "INSERT INTO words (word, meaning) VALUES (?, ?)",
                (word, meaning)
            )
            conn.commit()
        except sqlite3.IntegrityError:
            pass

        conn.close()

        return redirect("/")

    return render_template("add.html")

@app.route("/saved")
def saved():

    conn = db()

    words = conn.execute(
        "SELECT * FROM words WHERE learned=1 ORDER BY id DESC"
    ).fetchall()

    conn.close()

    return render_template(
        "saved.html",
        words=words,
        count=len(words)
    )

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
