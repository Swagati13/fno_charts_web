from flask import Flask, render_template, request
import importlib
import datetime 

app = Flask(__name__)

def get_index_num_from_time(hour, min=0, sec=0):
    if hour >= 9 and hour <= 15:
        return (datetime.datetime(2023,1,1, hour, min, sec) - datetime.datetime(2023,1,1, 9, 15)).seconds
    else:
        return None
    
def get_time_from_index_num(num):
    if num >=0 and num <= 22500:
        return (datetime.datetime(2023,1,1, 9, 15, 0) + datetime.timedelta(seconds = num)).time()
    else:
        return None
    
@app.route('/', methods=['GET', 'POST'])
def index():
    input_details={}
    if request.method == 'POST':
        selected_index = request.form.get('folderSelect')
        selected_DTE=request.form.get('folderDTE')
        start_time_str = request.form.get('start_time')
        end_time_str = request.form.get('end_time')
        strike_distance = int(request.form.get('strike_distance'))
        sl_percent = float(request.form.get('sl_percent'))
        max_loss_points = int(request.form.get('max_loss_points'))
        target_points = int(request.form.get('target_points'))

        start_time_parts = list(map(int, start_time_str.split(':')))
        end_time_parts = list(map(int, end_time_str.split(':')))

        start_index = get_index_num_from_time(*start_time_parts)
        end_index = get_index_num_from_time(*end_time_parts)

        module_name = f"backtest_{selected_index}"
        backtest_module = importlib.import_module(module_name)
        results = backtest_module.get_strategy_stats(selected_DTE,start_index, end_index, strike_distance, sl_percent, max_loss_points, target_points)
        
        input_details = {
            'selected_index': selected_index,
            'selected_DTE' : selected_DTE,
            'start_time': start_time_str,
            'end_time': end_time_str,
            'strike_distance': strike_distance,
            'sl_percent': sl_percent,
            'max_loss_points': max_loss_points,
            'target_points': target_points
        }
        
        results_dict = {
            'avg_pnl_per_trade': results[0],
            'max_profit': results[1],
            'max_loss': results[2],
            'max_drawdown': results[3],
            'avg_profit_on_winning_trades': results[4],
            'avg_loss_on_losing_trades': results[5],
            'expectancy': results[6],
            'longest_drawdown_duration': results[7],
            'win_percent': results[8],
            'max_winning_streak': results[9],
            'max_losing_streak': results[10]
        }
        trades_df = backtest_module.get_strategy_stats(selected_DTE,start_index, end_index, strike_distance, sl_percent, max_loss_points, target_points, get_trades=True)
        trades_df['entry_time'] = trades_df['entry_time'].apply(get_time_from_index_num)
        trades_df['exit_time'] = trades_df['exit_time'].apply(get_time_from_index_num)
        return render_template('result.html', results=results_dict, input_details=input_details, trades=trades_df)

    return render_template('result.html',input_details=input_details)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)
