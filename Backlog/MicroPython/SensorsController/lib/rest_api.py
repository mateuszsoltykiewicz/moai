from microdot import Microdot, Response
import ujson
from lib.config_manager import load_config, save_config, log_event

app = Microdot()

def check_token(request):
    config = load_config()
    token = request.headers.get("Authorization")
    return token == "Bearer " + config["api_token"]

@app.route('/config', methods=['GET', 'POST'])
def config(request):
    if request.method == 'POST':
        if not check_token(request):
            return {"error": "Unauthorized"}, 401
        try:
            new_config = request.json
            save_config(new_config)
            log_event("CONFIG_UPDATE", "Config updated via REST")
            return {"status": "ok"}
        except Exception as e:
            log_event("CONFIG_ERROR", f"REST update failed: {e}")
            return {"error": str(e)}, 400
    else:
        with open("config.json") as f:
            return Response(body=f.read(), content_type='application/json')

def start_api():
    app.run(port=80)
