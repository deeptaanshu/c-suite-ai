from flask import Flask, render_template_string, request

app = Flask(__name__)

TEMPLATE = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>C-Suite AI Agent</title>
    <!-- Bootstrap 5 CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.4.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
      body {
        background-color: #f5f5f5;
        color: #212529;
      }
      .container {
        max-width: 480px;
        margin-top: 3rem;
      }
      h1 {
        font-size: 1.75rem;
        margin-bottom: 1.5rem;
        text-align: center;
      }
      .btn-agent {
        width: 100%;
        padding: 0.75rem;
        font-size: 1.125rem;
        margin-bottom: 1rem;
        text-align: left;
      }
      .result-box {
        margin-top: 2rem;
      }
    </style>
  </head>
  <body>
    <div class="container bg-white p-4 rounded shadow-sm">
      <h1>AI Agent Suite</h1>
      <form action="/run" method="post">
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
      {% if result %}
      <div class="alert alert-light border result-box" role="alert">
        {{ result }}
      </div>
      {% endif %}
    </div>
    <!-- Bootstrap JS Bundle -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.4.2/dist/js/bootstrap.bundle.min.js"></script>
  </body>
</html>
"""

# Handlers for each AI Agent
def accounting_agent():
    return "✅ Accounting AI Agent ran successfully."

def legal_agent():
    return "✅ Legal AI Agent ran successfully."

def marketing_agent():
    return "✅ Marketing AI Agent ran successfully."

def bizdev_agent():
    return "✅ Sales / Business Development AI Agent ran successfully."

def hr_agent():
    return "✅ HR / Sourcing AI Agent ran successfully."

# (key, label, bootstrap button color)
BUTTONS = [
    ("accounting", "Accounting AI Agent",                    "primary"),
    ("legal",      "Legal AI Agent",                         "secondary"),
    ("marketing",  "Marketing AI Agent",                     "success"),
    ("bizdev",     "Sales / Business Development AI Agent", "info"),
    ("hr",         "HR / Sourcing AI Agent",                 "warning"),
]

ACTION_MAP = {
    "accounting": accounting_agent,
    "legal":      legal_agent,
    "marketing":  marketing_agent,
    "bizdev":     bizdev_agent,
    "hr":         hr_agent,
}

@app.route("/", methods=["GET"])
def index():
    return render_template_string(TEMPLATE, buttons=BUTTONS, result=None)

@app.route("/run", methods=["POST"])
def run_action():
    key     = request.form.get("action")
    handler = ACTION_MAP.get(key)
    result  = handler() if handler else f"⚠️ Unknown action: {key}"
    return render_template_string(TEMPLATE, buttons=BUTTONS, result=result)

if __name__ == "__main__":
    app.run(debug=True)
