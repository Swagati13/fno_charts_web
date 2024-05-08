
import datetime, pytz, time, os, pyotp
import traceback
import pandas as pd
from threading import Thread
import pickle
import requests
from flask import Flask, render_template, jsonify
import logging

with open("strategies_list.pkl", 'rb') as pkl:
    strategies_list = pickle.load(pkl)

with open("trade_details.pkl", 'rb') as pkl:
    trade_details = pickle.load(pkl)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('trade_details.html')

@app.route('/s/')
def strategiessss():
    return render_template('strategies_list.html')

@app.route('/t/')
def trade_detailssss():
    return render_template('trade_details.html')

@app.route('/get_strategies_list')
def get_strategies_list():
    global strategies_list
    df = pd.DataFrame(strategies_list)
    df = df[['name', 'sl_percent', 'entry_time', 'exit_time',
        'strike_distance', 'entry_done', 'exit_done',
        'max_loss_per_lot', 'target_profit_per_lot', 'index_name', 'quantity',
            'ce_order_placed', 'pe_order_placed', 'execution_done']]
    html = df.to_html(index=False)
    return html

@app.route('/get_trade_details')
def get_trade_details():
    global trade_details
    df = pd.DataFrame(trade_details).T
    df = df[['strategy', 'entry_time', 'ce_symbol',
       'pe_symbol', 'ce_sell_price', 'pe_sell_price',
       'ce_sl_price', 'pe_sl_price', 'qty', 'ce_buy_price', 'pe_buy_price', 'ce_exit_time',
       'pe_exit_time', 'ce_sl_hit', 'pe_sl_hit', 'lot_size', 'ce_sl_hit_actual', 'pe_sl_hit_actual',
       'ce_pnl', 'pe_pnl', 'max_loss_per_lot', 'strategy_pnl', 'strategy']]
    df2 = pd.DataFrame([df.columns], columns=df.columns)
    df = pd.concat([df, df2], ignore_index=True)
    html = df.to_html(index=False)
    return html

if __name__ == '__main__':
    from waitress import serve
    app.run(host="0.0.0.0", port=4999, debug=True)
    # serve(app, host="0.0.0.0", port=4999)