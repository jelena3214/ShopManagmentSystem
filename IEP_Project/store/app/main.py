from flask import Flask, jsonify

application = Flask (__name__)

import os
import subprocess

@application.route("/", methods = ["GET"])
def hello_world():
    return "<h1>Hello world!</h1>"

@application.route("/products", methods = ['GET'])
def products ( ):
    os.environ["SPARK_APPLICATION_PYTHON_LOCATION"] = "/app/product_statistics.py"

    os.environ["SPARK_SUBMIT_ARGS"] = "--driver-class-path /app/mysql-connector-j-8.0.33.jar --jars /app/mysql-connector-j-8.0.33.jar"
     
    result = subprocess.check_output ( ["/template.sh"] )
    result_decoded = result.decode()
    print(result_decoded)  # Log the complete result

    # Extract the result from product_statistics.py output
    start_marker = "=== START RESULT ==="
    end_marker = "=== END RESULT ==="
    start_index = result_decoded.find(start_marker) + len(start_marker) + 1
    end_index = result_decoded.find(end_marker, start_index)
    result_extracted = result_decoded[start_index:end_index]

    return jsonify(result_extracted.strip()), 200

@application.route("/categories", methods = ['GET'])
def categories ( ):
    os.environ["SPARK_APPLICATION_PYTHON_LOCATION"] = "/app/category_statistics.py"

    os.environ["SPARK_SUBMIT_ARGS"] = "--driver-class-path /app/mysql-connector-j-8.0.33.jar --jars /app/mysql-connector-j-8.0.33.jar"
     
    result = subprocess.check_output ( ["/template.sh"] )
    result_decoded = result.decode()
    print(result_decoded)  # Log the complete result

    # Extract the result from product_statistics.py output
    start_marker = "=== START RESULT ==="
    end_marker = "=== END RESULT ==="
    start_index = result_decoded.find(start_marker) + len(start_marker) + 1
    end_index = result_decoded.find(end_marker, start_index)
    result_extracted = result_decoded[start_index:end_index]
    return jsonify(result_extracted.strip()), 200

if ( __name__ == "__main__" ):
    application.run(host = "0.0.0.0", port=5007)