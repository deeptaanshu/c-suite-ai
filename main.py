from flask import Flask, render_template_string, request, session, redirect, url_for
import json
import openai
import tweepy

import sqlite3
import openai
import json

app = Flask(__name__)
app.secret_key = "replace_with_a_strong_random_secret"

# ─── Shared Templates ───────────────────────────────────────────────────────────
INDEX_TEMPLATE = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Deep Lithium's C-Suite AI Agent</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.4.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
      body { background-color: #f5f5f5; }
      .container { max-width: 480px; margin: 3rem auto; }
      h1 { text-align: center; margin-bottom: 1.5rem; }
      .btn-agent { width: 100%; padding: .75rem; font-size: 1.125rem; margin-bottom: 1rem; text-align: left; }
    </style>
  </head>
  <body>
    <div class="container bg-white p-4 rounded shadow-sm">
      <h1>Deep Lithium's C-Suite AI Agent</h1>
      <form action="{{ url_for('run_action') }}" method="post">
        {% for key, label, color in buttons %}
        <button
          type="submit"
          name="action"
          value="{{ key }}"
          class="btn btn-{{ color }} btn-agent">
          {{ label }}
        </button>
        {% endfor %}
      </form>
    </div>
  </body>
</html>
"""

CHAT_TEMPLATE = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{{ agent_label }} Chat</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.4.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
      body { background-color: #eef2f5; }
      .chat-container { max-width: 600px; margin: 2rem auto; }
      .message { padding: .5rem 1rem; margin-bottom: .5rem; border-radius: .5rem; }
      .from-user  { background: #d1e7dd; text-align: right; }
      .from-agent{ background: #fff; }
      .chat-box  { height: 400px; overflow-y: auto; padding: 1rem; background: #fff; border: 1px solid #ccc; border-radius: .5rem; }
      .input-row { margin-top: 1rem; }
    </style>
  </head>
  <body>
    <div class="chat-container">
      <h3 class="text-center mb-4">{{ agent_label }}</h3>
      <div class="chat-box" id="chat-box">
        {% for msg in history %}
        <div class="message {% if msg.sender=='user' %}from-user{% else %}from-agent{% endif %}">
          {{ msg.message }}
        </div>
        {% endfor %}
      </div>
      <form action="" method="post" class="input-row">
        <div class="input-group">
          <input type="text" name="user_input" class="form-control" placeholder="Type your message…" autocomplete="off" required>
          <button class="btn btn-primary" type="submit">Send</button>
        </div>
      </form>
      <div class="text-center mt-3">
        <a href="{{ url_for('index') }}" class="btn btn-link">← Back to Suite</a>
      </div>
    </div>
    <script>
      const box = document.getElementById('chat-box');
      box.scrollTop = box.scrollHeight;
    </script>
  </body>
</html>
"""

# ─── Configuration ─────────────────────────────────────────────────────────────
BUTTONS = [
    ("accounting", "Accounting AI Agent",                    "primary"),
    ("legal",      "Legal AI Agent",                         "secondary"),
    ("marketing",  "Marketing AI Agent",                     "success"),
    ("bizdev",     "Sales / Business Dev. AI Agent",         "info"),
    ("hr",         "HR / Sourcing AI Agent",                 "warning"),
]

# ─── Entry Point ───────────────────────────────────────────────────────────────
@app.route("/", methods=["GET"])
def index():
    return render_template_string(INDEX_TEMPLATE, buttons=BUTTONS)

@app.route("/run", methods=["POST"])
def run_action():
    choice = request.form.get("action")
    # initialize session history and redirect to the proper chat
    if choice == "accounting":
        session["history_accounting"] = [{"sender":"agent","message":"Hello! I’m Deep Lithium's Accounting AI Agent. What data would you like me to add to or query from our internal Accounting Database?"}]
        return redirect(url_for("accounting_chat"))
    if choice == "legal":
        session["history_legal"] = [{"sender":"agent","message":"Hello! I’m Deep Lithium's Legal AI Agent. Keeping in mind that I can search the public internet during our interactions, how may I assist you?"}]
        return redirect(url_for("legal_chat"))
    if choice == "marketing":
        session["history_marketing"] = [{"sender":"agent","message":"Hi there! I’m Deep Lithium's Marketing AI Agent. What would you like to post on Deep Lithium's Twitter account today?"}]
        return redirect(url_for("marketing_chat"))
    if choice == "bizdev":
        session["history_bizdev"] = [{"sender":"agent","message":"Greetings! I’m Deep Lithium's Sales/Business Dev AI Agent. What data would you like me to add to or query from our internal BizDev Database?"}]
        return redirect(url_for("bizdev_chat"))
    if choice == "hr":
        session["history_hr"] = [{"sender":"agent","message":"Hello! I’m Deep Lithium's HR/Sourcing AI Agent. What would you like help with?"}]
        return redirect(url_for("hr_chat"))
    return redirect(url_for("index"))

def load_credentials(file_path='keys.json'):
    """
    Reads a JSON file containing both OpenAI and Twitter API keys.
    """
    with open(file_path, 'r') as f:
        credentials = json.load(f)
    return credentials

# ─── Accounting Chat ────────────────────────────────────────────────────────────
def accounting_logic(user_text: str) -> str:
    # Create new Accounting DB
    db = LLMSQLite("accounting.db")
    db.conn.execute("""
    CREATE TABLE IF NOT EXISTS accounting (
      id    INTEGER PRIMARY KEY AUTOINCREMENT,
      line_item  TEXT,
      cost TEXT
    );
    """)
    db.conn.commit()

    """
    Prompts the OpenAI LLM to produce a single SQL statement that fulfills the Natural Language (NL) command,
    given the current DB schema.
    """
    prompt = f"""
    You are an expert SQL assistant. Based on the following SQLite schema:

    {LLMSQLite._get_schema(db)}

    Generate exactly one valid SQLite statement (no explanations) to fulfill this request:
    “{user_text}”
    """

    # Get OpenAI credentials from keys.json
    with open("/Users/deeptaanshukumar/keys_isp.json", 'r') as f:
        credentials = json.load(f)
    openai.api_key = credentials["openai_api_key"]

    resp = openai.ChatCompletion.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": "You generate SQL only."},
            {"role": "user",   "content": prompt}
        ],
        temperature=0,
        max_tokens=256
    )
    sql = resp.choices[0].message.content.strip().strip("```sql").strip("```")

    # Query via NL
    rows = db.execute_nl(sql)
    if isinstance(rows, int):
        output = "Data added successfully!"
    else:
        output = ""
        for row in rows:
            output = output + str(dict(row)) + "\n"

    return f"🤖 (Accounting) Here is the data from the Accounting database: “{output}”"

@app.route("/accounting", methods=["GET","POST"])
def accounting_chat():
    hist = session.get("history_accounting", [])
    if request.method == "POST":
        user = request.form["user_input"].strip()
        hist.append({"sender":"user","message":user})
        reply = accounting_logic(user)
        hist.append({"sender":"agent","message":reply})
        session["history_accounting"] = hist
    return render_template_string(CHAT_TEMPLATE, history=hist, agent_label="Accounting AI Agent")

# ─── Legal Chat ─────────────────────────────────────────────────────────────────
def legal_logic(user_text: str) -> str:

    # Extract the OpenAI API key
    credentials = load_credentials("/Users/deeptaanshukumar/keys_isp.json")
    chatgpt_api_key = credentials["openai_api_key"]

    """
    This prompt will allow users to use public internet to answer their Legal-related questions
    """
    openai.api_key = chatgpt_api_key
    response = openai.ChatCompletion.create(
        model="gpt-4o-search-preview", # need to use this model since 4.5-preview api doesn't allow for searching web for results
        messages=[
            {"role": "user", "content": "Assume you are the company's Chief Legal Officer, and answer the following question by one of your employees: " + user_text}
        ],
    )
    # Extracting the answer text from the response
    answer = response.choices[0].message['content'].strip()

    return f"🤖 (Legal): “{answer}”"

@app.route("/legal", methods=["GET","POST"])
def legal_chat():
    hist = session.get("history_legal", [])
    if request.method == "POST":
        user = request.form["user_input"].strip()
        hist.append({"sender":"user","message":user})
        reply = legal_logic(user)
        hist.append({"sender":"agent","message":reply})
        session["history_legal"] = hist
    return render_template_string(CHAT_TEMPLATE, history=hist, agent_label="Legal AI Agent")

# ─── Marketing Chat ─────────────────────────────────────────────────────────────
def marketing_logic(user_text: str) -> str:

    # Extract the OpenAI and Twitter API keys
    credentials = load_credentials("/Users/deeptaanshukumar/keys_isp.json")
    chatgpt_api_key = credentials["openai_api_key"]

    """
    This prompt will take a users topic and make a Twitter post in approximately 250 characters.
    """
    openai.api_key = chatgpt_api_key
    response = openai.ChatCompletion.create(
        model="gpt-4.1",
        messages=[
            {"role": "user", "content": "Assume the role of a Head of Social Media at Deep Lithium and use the following prompt to make a post for Twitter with a length of exactly 250 characters: " + user_text}
        ],
        temperature=0.7  # Adjust the creativity of the answer if desired
    )
    # Extracting the answer text from the response
    answer = response.choices[0].message['content'].strip()

    tweet_text = answer
    client = tweepy.Client(
    consumer_key=credentials["twitter_api_key"],
    consumer_secret=credentials["twitter_api_secret_key"],
    access_token=credentials["twitter_access_token"],
    access_token_secret=credentials["twitter_access_token_secret"],
    bearer_token=credentials["bearer_token"])

    # Post a tweet and return the API response
    tweet_response = client.create_tweet(text=tweet_text)

    return f"🤖 (Marketing) We posted the following tweet on https://x.com/deep_lithium: “{tweet_text}”"

@app.route("/marketing", methods=["GET","POST"])
def marketing_chat():
    hist = session.get("history_marketing", [])
    if request.method == "POST":
        user = request.form["user_input"].strip()
        hist.append({"sender":"user","message":user})
        reply = marketing_logic(user)
        hist.append({"sender":"agent","message":reply})
        session["history_marketing"] = hist
    return render_template_string(CHAT_TEMPLATE, history=hist, agent_label="Marketing AI Agent")

# ─── BizDev Chat ────────────────────────────────────────────────────────────────
def bizdev_logic(user_text: str) -> str:
    # Create new BizDev DB
    db = LLMSQLite("bizdev.db")
    db.conn.execute("""
    CREATE TABLE IF NOT EXISTS bizdev (
      id    INTEGER PRIMARY KEY AUTOINCREMENT,
      name  TEXT,
      email TEXT,
      notes TEXT
    );
    """)
    db.conn.commit()

    """
    Prompts the OpenAI LLM to produce a single SQL statement that fulfills the Natural Language (NL) command,
    given the current DB schema.
    """
    prompt = f"""
    You are an expert SQL assistant. Based on the following SQLite schema:

    {LLMSQLite._get_schema(db)}

    Generate exactly one valid SQLite statement (no explanations) to fulfill this request:
    “{user_text}”
    """

    # Get OpenAI credentials from keys.json
    with open("/Users/deeptaanshukumar/keys_isp.json", 'r') as f:
        credentials = json.load(f)
    openai.api_key = credentials["openai_api_key"]

    resp = openai.ChatCompletion.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": "You generate SQL only."},
            {"role": "user",   "content": prompt}
        ],
        temperature=0,
        max_tokens=256
    )
    sql = resp.choices[0].message.content.strip().strip("```sql").strip("```")

    # 3) Query via NL
    rows = db.execute_nl(sql)
    if isinstance(rows, int):
        output = "Data added successfully!"
    else:
        output = ""
        for row in rows:
            output = output + str(dict(row)) + "\n"

    return f"🤖 (BizDev) Here is the data from the Accounting database: “{output}”"

@app.route("/bizdev", methods=["GET","POST"])
def bizdev_chat():
    hist = session.get("history_bizdev", [])
    if request.method == "POST":
        user = request.form["user_input"].strip()
        hist.append({"sender":"user","message":user})
        reply = bizdev_logic(user)
        hist.append({"sender":"agent","message":reply})
        session["history_bizdev"] = hist
    return render_template_string(CHAT_TEMPLATE, history=hist, agent_label="Sales / Business Dev. AI Agent")

# ─── HR Chat ───────────────────────────────────────────────────────────────────
def hr_logic(user_text: str) -> str:
   # Extract the OpenAI API key
    credentials = load_credentials("/Users/deeptaanshukumar/keys_isp.json")
    chatgpt_api_key = credentials["openai_api_key"]

    """
    This prompt will allow users to use public internet to answer their HR-related questions
    """
    openai.api_key = chatgpt_api_key
    response = openai.ChatCompletion.create(
        model="gpt-4o-search-preview", # need to use this model since 4.5-preview api doesn't allow for searching web for results
        messages=[
            {"role": "user", "content": "Assume you are the company's Chief HR Officer, and answer the following question by one of your employees: " + user_text}
        ],
    )
    # Extracting the answer text from the response
    answer = response.choices[0].message['content'].strip()

    return f"🤖 (HR) You asked: “{answer}”"

@app.route("/hr", methods=["GET","POST"])
def hr_chat():
    hist = session.get("history_hr", [])
    if request.method == "POST":
        user = request.form["user_input"].strip()
        hist.append({"sender":"user","message":user})
        reply = hr_logic(user)
        hist.append({"sender":"agent","message":reply})
        session["history_hr"] = hist
    return render_template_string(CHAT_TEMPLATE, history=hist, agent_label="HR / Sourcing AI Agent")

# ─── Core class: LLM-driven SQLite interface ──────────────────────────────────
class LLMSQLite:
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row

    def _get_schema(self) -> str:
        """Extracts CREATE statements for all tables/views."""
        cur = self.conn.execute(
            "SELECT sql FROM sqlite_master WHERE type IN ('table','view') AND sql NOT NULL"
        )
        return "\n".join(r[0] for r in cur.fetchall())

    def execute_nl(self, sql: str):
        """
        Translates the NL command to SQL and runs it.
        Returns:
          - For SELECT: a list of sqlite3.Row
          - Otherwise: number of rows affected
        """
#         schema = self._get_schema()
#         sql = generate_sql_from_nl(nl_command, schema)
        cur = self.conn.cursor()
        cur.execute(sql)
        if sql.strip().lower().startswith("select"):
            return cur.fetchall()
        elif sql.strip().lower().startswith("how"):
            return cur.fetchall()
        elif sql.strip().lower().startswith("which"):
            return cur.fetchall()
        else:
            self.conn.commit()
            return cur.rowcount

# ─── Run Server ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True)