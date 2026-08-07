from flask import Flask, request, render_template, redirect
import sqlite3

app = Flask(__name__)


def db():
    conn = sqlite3.connect("words.db")

    conn.execute("""
    CREATE TABLE IF NOT EXISTS words(
        id INTEGER PRIMARY KEY,
        word TEXT UNIQUE,
        meaning TEXT,
        learned INTEGER DEFAULT 0
    )
    """)

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
                "INSERT INTO words(word, meaning) VALUES(?,?)",
                (word, meaning)
            )

            conn.commit()
            msg = "✅ تم حفظ الكلمة"

        except:
            msg = "⚠️ الكلمة موجودة مسبقاً"


    words = conn.execute(
        "SELECT * FROM words ORDER BY id DESC"
    ).fetchall()


    return render_template(
        "home.html",
        words=words,
        count=len(words),
        msg=msg
    )

@app.route("/review")
def review():
    conn = db()

    word = conn.execute(
        "SELECT word, meaning FROM words ORDER BY review_count DESC LIMIT 1"
    ).fetchone()

    if word is None:
        return "لا توجد كلمات"

    conn.close()

    return render_template(
        "review.html",
        word=word[0],
        meaning=word[1]
    )

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


    return render_template(
        "stats.html",
        total=total,
        learned=learned,
        need=need
    )
@app.route("/review")

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

    conn = db()

    word = conn.execute(
        "SELECT id FROM words ORDER BY RANDOM() LIMIT 1"
    ).fetchone()

    if word:
        conn.execute(
            "UPDATE words SET learned=1 WHERE id=?",
            (word[0],)
        )
        conn.commit()

    conn.close()

    return "✅ تم حفظ الكلمة! <br><br><a href='/review'>العودة للمراجعة</a>"

    conn = db()

    word = conn.execute(
        "SELECT id FROM words ORDER BY RANDOM() LIMIT 1"
    ).fetchone()

    if word:
        conn.execute(
            "UPDATE words SET learned=1 WHERE id=?",
            (word[0],)
        )
        conn.commit()

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


@app.route("/search")
def search():
l
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
