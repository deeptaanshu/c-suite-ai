from flask import Flask, render_template_string, request

app = Flask(__name__)

# HTML template with 5 arbitrarily-labeled buttons
TEMPLATE = """
<!doctype html>
<html>
  <head>
    <title>C-Suite AI</title>
  </head>
  <body>
    <h1>Choose a C-Suite AI Role</h1>
    {% for key, label in buttons.items() %}
      <form action="/run" method="post" style="display:inline-block; margin:8px;">
        <button type="submit" name="action" value="{{ key }}">{{ label }}</button>
      </form>
    {% endfor %}
    {% if result %}
      <p><strong>Result:</strong> {{ result }}</p>
    {% endif %}
  </body>
</html>
"""

# Define your handlers
def accounting_agent():
    return "Accounting AI Agent"

def legal_agent():
    return "Legal AI Agent"

def marketing_agent():
    return "Marketing AI Agent"

def bizdev_agent():
    return "Sales / Business Development AI Agent"

def hr_agent():
    return "HR / Sourcing AI Agent"

# Map action-keys to handler functions
ACTION_MAP = {
    "accounting":     accounting_agent,
    "legal":       legal_agent,
    "marketing":      marketing_agent,
    "bizdev":      bizdev_agent,
    "hr":    hr_agent
}

# The labels you actually want on the buttons
BUTTONS = {
    "accounting":  "Accounting AI Agent",
    "legal":    "Legal AI Agent",
    "marketing":   "Marketing AI Agent",
    "bizdev":   "Sales / Business Development AI Agent",
    "hr": "HR / Sourcing AI Agent"
}

@app.route("/", methods=["GET"])
def index():
    return render_template_string(TEMPLATE, buttons=BUTTONS, result=None)

@app.route("/run", methods=["POST"])
def run_action():
    action_key = request.form.get("action")
    handler = ACTION_MAP.get(action_key)
    if handler:
        result = handler()
    else:
        result = f"⚠️ Unknown action: {action_key}"
    return render_template_string(TEMPLATE, buttons=BUTTONS, result=result)

if __name__ == "__main__":
    app.run(debug=True)
