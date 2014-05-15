from flask import Flask, jsonify, render_template, request

app = Flask(__name__, static_url_path='')

import matahn.views