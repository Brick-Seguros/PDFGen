"""Flask Application"""

# load libaries
from flask import Flask, jsonify
import warnings
import logging

# Load modules PF

from src.routes.analysis_pdf import blueprint_analysis

# init Flask app
app = Flask(__name__)

# Configurations
warnings.filterwarnings("ignore")
logging.getLogger().setLevel(logging.INFO)


basepath=f"/pdf"

#Healthcheck
@app.route(basepath,methods=['GET'])
def hc():
  return jsonify({"status":'online','service':'PDFGenerator'})

# register blueprints. ensure that all paths are versioned!
app.register_blueprint(blueprint_analysis,name='blueprint_analysis', url_prefix=f"{basepath}")

##################
# Error Handlers
###################
def handle_internal_error(e):
  return jsonify({"message":'UNKNOWN_ERROR'}), 500
app.register_error_handler(500, handle_internal_error)

def handle_internal_error_large(e):
  return jsonify({"message":'FILE_TOO_LARGE_ERROR'}), 500
app.register_error_handler(413, handle_internal_error_large)