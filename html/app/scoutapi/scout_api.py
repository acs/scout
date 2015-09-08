from flask import Flask, request, Response
from ConfigParser import SafeConfigParser
import os
import subprocess
import traceback


app = Flask(__name__)
scout_home = "/home/bitergia/scout"
scout_conf = scout_home +"/scout.conf"

@app.route("/api/category/<name>", methods = ['GET'])
def get_category(name):
    return "Getting category data ..."

@app.route("/api/category", methods = ['POST'])
def create_category():
    """ Add a new category to scout config file  """
    # return "Added new category " + name

    if request.headers['Content-Type'] == 'application/json':
        category_data = request.json
        resp = add_category(category_data)
        try:
            return "Category added " + category_data.keys()[0]
        except:
            traceback.print_exc()

    else:
        # 502: Bad gateway
        # resp = Response(json.dumps(urls_bad), status=502, mimetype='application/json')
        resp = Response("JSON data for category not received", status=502)
        return resp

def add_category(category):
    name = category.keys()[0]
    cat_name = "category_" + name  # section name for a category in config
    config = read_config()
    config[cat_name] = {}
    try:
        config[cat_name]["keywords"] = category[name]
        # Time to write the new config file
        # TODO: control concurrency
        write_config(config)
        # res = update_scout()
    except:
        traceback.print_exc()

    return config

def update_scout():
    # Launch scout to update events and deploy them to web server

    command = os.path.join(scout_home,"utils/update-scout.sh")
    res = subprocess.call(command, shell = True)

    return res


def read_config():
    options = {}

    parser = SafeConfigParser()
    try:
        fd = open(scout_conf, 'r')
    except:
        traceback.print_exc()

    parser.readfp(fd)
    fd.close()

    sections = parser.sections()

    for s in sections:
        options[s] = {}
        opti = parser.options(s)
        for o in opti:
            options[s][o] = parser.get(s,o)

    return options

def write_config(config):
    """Create the scout config file"""

    parser = SafeConfigParser()

    os.rename(scout_conf, scout_conf+".old")
    fd = open(scout_conf, 'w')

    print "write_config"

    for section in config:
        parser.add_section(section)
        for key in config[section].keys():
            value = config[section][key]
            if isinstance(value, list):
                value = ",".join(value)
            parser.set(section, key, value)

    parser.write(fd)
    fd.close()

if __name__ == "__main__":
    app.debug = True
    app.run()
