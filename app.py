# -*- coding: utf-8 -*-
# created by restran on 2019/05/06
from __future__ import unicode_literals, absolute_import

import os
import shutil
import zipfile
from optparse import OptionParser

from flask import Flask, request, jsonify, g
from future.moves.urllib.parse import urlparse
from mountains import logging
from mountains.logging import StreamHandler, RotatingFileHandler
from werkzeug.routing import BaseConverter

from config import *
from index import WizIndex

if not os.path.exists('logs'):
    os.makedirs('logs')

logging.init_log(StreamHandler(level=logging.INFO,
                               format=logging.FORMAT_VERBOSE,
                               datefmt=logging.DATE_FMT_SIMPLE),
                 RotatingFileHandler(level=logging.INFO, filename='logs/app.txt'),
                 disable_existing_loggers=False)


class RegexConverter(BaseConverter):
    def __init__(self, _map, *args):
        super(RegexConverter, self).__init__(_map)
        self.map = _map
        self.regex = args[0]


parser = OptionParser()
parser.add_option("-p", "--port", dest="port", default=5000, type="int", help="port")

app = Flask(__name__)
app.url_map.converters['regex'] = RegexConverter
# DATABASE_CONN_URL = 'sqlite:///database.db'
logger = logging.getLogger(__name__)


def get_wiz_index():
    wiz_index = getattr(g, '_wiz_index', None)
    if wiz_index is None:
        wiz_index = g._wiz_index = WizIndex()

    return wiz_index


@app.teardown_appcontext
def close_connection(exception):
    wiz_index = getattr(g, '_wiz_index', None)
    if wiz_index is not None:
        wiz_index.index_db.close()


def regex_route(regex):
    return '/<regex("{}"):path>'.format(regex)


@app.route('/')
def page_index():
    with open('templates/index.html', 'rb') as f:
        return f.read()


@app.route('/api/search', methods=['POST'])
def page_search():
    wiz_index = get_wiz_index()
    keyword = request.json.get('keyword')
    page_num = request.json.get('page_num', 1)
    total, results = wiz_index.search(keyword, page_num)
    return jsonify({'code': 200, 'data': results, 'total': total, 'msg': 'ok'})


@app.route('/document/<string:document_guid>/<string:wiz_version>/')
def view_document(document_guid, wiz_version):
    try:
        wiz_index = get_wiz_index()
        sql = """select * from WIZ_INDEX where DOCUMENT_GUID=:document_guid"""
        rows = wiz_index.index_db.query(sql, document_guid=document_guid).as_dict()
        if len(rows) < 0:
            return 'error: 请求的数据不存在'

        item = rows[0]
        zf = zipfile.ZipFile(os.path.join(WIZ_NOTE_PATH, 'notes/{%s}' % document_guid))
        path = 'tmp/{}_{}'.format(document_guid, item['WIZ_VERSION'])
        if not os.path.exists('tmp'):
            os.mkdir('tmp')
        if not os.path.exists(path):
            for dir_name in os.listdir('tmp'):
                if document_guid in dir_name:
                    shutil.rmtree('tmp/{}'.format(dir_name))

            os.mkdir(path)
            zf.extractall(path)
        with open('{}/index.html'.format(path), 'rb') as f:
            return f.read()

    except Exception as e:
        return 'error: %s' % e


@app.route('/document/<string:document_guid>/<string:wiz_version>/index_files/<path:sub_path>')
def view_document_files(document_guid, wiz_version, sub_path):
    try:
        if "../" in sub_path or "..\\" in sub_path:
            return 'error: file not found'

        path = 'tmp/{}_{}/index_files/{}'.format(document_guid, wiz_version, sub_path)
        if os.path.exists(path):
            with open(path, 'rb') as f:
                return f.read()
        else:
            return 'error: file not found'
    except Exception as e:
        return 'error: %s' % e


@app.route('/index_files/<path:sub_path>')
def view_document_files_by_referrer(sub_path):
    try:
        if "../" in sub_path or "..\\" in sub_path:
            return 'error: file not found'

        referrer = request.headers.get('Referrer')
        url_parsed = urlparse(referrer)
        if url_parsed.path.startswith('/document/'):
            document_guid, wiz_version = url_parsed.path[len('/document/'):].split('/')
        else:
            document_guid, wiz_version = None, None

        path = 'tmp/{}_{}/index_files/{}'.format(document_guid, wiz_version, sub_path)
        if os.path.exists(path):
            with open(path, 'rb') as f:
                return f.read()
        else:
            return 'error: file not found'
    except Exception as e:
        return 'error: %s' % e


def main():
    (options, args) = parser.parse_args()
    port = options.port
    logger.warning('server is running on 127.0.0.1:%s' % port)
    app.run(host="127.0.0.1", port=port, debug=True)


if __name__ == "__main__":
    main()
