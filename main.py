from flask import Flask, render_template_string, request

app = Flask(__name__)

# HTML template with 5 buttons
TEMPLATE = """
<!doctype html>
<html>
  <head>
    <title>5-Button Python UI</title>
  </head>
  <body>
    <h1>Choose an action</h1>
    {% for i in range(1,6) %}
      <form action="/run/{{i}}" method="post" style="display:inline-block; margin:10px;">
        <button type="submit">Action {{i}}</button>
      </form>
    {% endfor %}
    {% if result %}
      <p><strong>Result:</strong> {{ result }}</p>
    {% endif %}
  </body>
</html>
"""

# Map each action to its handler
def action_one():   return "Executed action one"
def action_two():   return "Executed action two"
def action_three(): return "Executed action three"
def action_four():  return "Executed action four"
def action_five():  return "Executed action five"

ACTION_MAP = {
    '1': action_one,
    '2': action_two,
    '3': action_three,
    '4': action_four,
    '5': action_five,
}

@app.route('/', methods=['GET'])
def index():
    return render_template_string(TEMPLATE, result=None)

@app.route('/run/<action_id>', methods=['POST'])
def run_action(action_id):
    func = ACTION_MAP.get(action_id)
    if not func:
        result = "Unknown action"
    else:
        result = func()
    return render_template_string(TEMPLATE, result=result)

if __name__ == '__main__':
    app.run(debug=True)
