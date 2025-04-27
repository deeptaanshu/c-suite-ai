from flask import Flask, render_template_string, request, session, redirect, url_for
import json
import openai

app = Flask(__name__)
app.secret_key = "replace_with_a_strong_random_secret"

# ─── Shared Templates ───────────────────────────────────────────────────────────
INDEX_TEMPLATE = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
    <title>AI Agent Suite</title>
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
      <h1>AI Agent Suite</h1>
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
        session["history_accounting"] = [{"sender":"agent","message":"Hello! I’m your Accounting AI Agent. What can I help you with?"}]
        return redirect(url_for("accounting_chat"))
    if choice == "legal":
        session["history_legal"] = [{"sender":"agent","message":"Hello! I’m your Legal AI Agent. How may I assist?"}]
        return redirect(url_for("legal_chat"))
    if choice == "marketing":
        session["history_marketing"] = [{"sender":"agent","message":"Hi there! I’m your Marketing AI Agent. What are we promoting today?"}]
        return redirect(url_for("marketing_chat"))
    if choice == "bizdev":
        session["history_bizdev"] = [{"sender":"agent","message":"Greetings! I’m your Sales/Business Dev AI Agent. Let’s grow your pipeline."}]
        return redirect(url_for("bizdev_chat"))
    if choice == "hr":
        session["history_hr"] = [{"sender":"agent","message":"Hello! I’m your HR/Sourcing AI Agent. Need help finding talent?"}]
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
    # TODO: replace with your accounting-specific logic
    return f"🤖 (Accounting) You asked: “{user_text}”"

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
    This prompt will allow users to use public internet to answer their legal-related questions
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
    # TODO: replace with your marketing-specific logic
    return f"🤖 (Marketing) You asked: “{user_text}”"

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
    # TODO: replace with your sales/bizdev-specific logic
    return f"🤖 (BizDev) You asked: “{user_text}”"

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
    # TODO: replace with your HR/sourcing-specific logic
    return f"🤖 (HR) You asked: “{user_text}”"

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

# ─── Run Server ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True)