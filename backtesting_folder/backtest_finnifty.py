import datetime
import pandas as pd
from threading import Thread
import traceback
import pickle
from tabulate import tabulate
import os

import warnings
warnings.filterwarnings("ignore")

holidays = ["2022-01-26", "2022-03-1", "2022-03-18", "2022-04-14", "2022-04-15", "2022-05-03", "2022-08-09", "2022-08-15", "2022-08-31", "2022-10-05", "2022-10-24", "2022-10-26", "2022-11-08",
            "2023-01-26", "2023-03-07", "2023-03-30", "2023-04-04", "2023-04-07", "2023-04-14", "2023-05-01", "2023-06-29", "2023-08-15", "2023-09-19", "2023-10-02", "2023-10-24", "2023-11-14", "2023-11-27", "2023-12-25",
            "2024-01-26", "2024-03-08", "2024-03-25","2024-03-29","2024-04-11","2024-04-17","2024-05-01"]

def get_strategy_stats(selected_dte,start_time, end_time, strike_distance, sl_percent, max_loss_points, target_points, get_trades = False):
    trades = []
    max_loss_points = - abs(max_loss_points)
    re_entry = False
    ce_strike = pe_strike = idx = 0
    
    dt_now = datetime.datetime.now()
    expiry_dates = []
    prev_date = ""
    for i in range(2000):
        date = datetime.datetime(2022,1,1) + datetime.timedelta(days=i)
        date_str = str(date.date())
        if date.isoweekday() == 2 and date <= dt_now:
            if date_str in holidays:
                expiry_dates.append(prev_date)
            else:
                expiry_dates.append(date)
        prev_date = date
        
    data_path = "/home/mestha/Desktop/bt_one_sec_data_21-4-2024/bt_one_sec_data"
    day_wise_pkl_path = "day_wise_pkl"
    bnf_data_path = os.path.join(data_path, "finnifty", day_wise_pkl_path)
    bnf_spot_path = os.path.join(data_path, "finnifty", "finnifty_spot.pkl")
    bnf_folder = os.path.join(data_path, "finnifty")
    expiry_dates = list(set(expiry_dates))
    def get_current_expiry_date(date):
        for exp in expiry_dates:
            if exp >= date:
                return exp
        if date.month == 12:
            for exp in expiry_dates:
                if exp >= date:
                    return exp
        raise Exception('Not found')

    dte1_dates = []
    for expiry_date in expiry_dates:
        date = expiry_date - datetime.timedelta(days=1)
        date_str = str(date.date())
        if date_str not in holidays and date.isoweekday() in [1,2,3,4,5]:
            dte1_dates.append(date)
        else:
            date_originial = date
            for i in range(7):
                date = date_originial - datetime.timedelta(days=i)
                date_str = str(date.date())
                if date_str not in holidays and date.isoweekday() in [1,2,3,4,5]:
                    dte1_dates.append(date)
                    break
    dte2_dates = []
    for expiry_date_1_dte in dte1_dates:
        date = expiry_date_1_dte - datetime.timedelta(days=1)
        date_str = str(date.date())
        if date_str not in holidays and date.isoweekday() in [1, 2, 3, 4, 5]:
            dte2_dates.append(date)
        else:
            date_original = date
            for i in range(7):
                date = date_original - datetime.timedelta(days=i)
                date_str = str(date.date())
                if date_str not in holidays and date.isoweekday() in [1, 2, 3, 4, 5]:
                    dte2_dates.append(date)
                    break

    dte3_dates = []
    for expiry_date_2_dte in dte2_dates:
        date = expiry_date_2_dte - datetime.timedelta(days=1)
        date_str = str(date.date())
        if date_str not in holidays and date.isoweekday() in [1, 2, 3, 4, 5]:
            dte3_dates.append(date)
        else:
            date_original = date
            for i in range(7):
                date = date_original - datetime.timedelta(days=i)
                date_str = str(date.date())
                if date_str not in holidays and date.isoweekday() in [1, 2, 3, 4, 5]:
                    dte3_dates.append(date)
                    break

    dte4_dates = []
    for date_3_dte in dte3_dates:
        date = date_3_dte - datetime.timedelta(days=1)
        date_str = str(date.date())
        if date in expiry_dates:
            continue
        if date_str not in holidays and date.isoweekday() in [1, 2, 3, 4, 5]:
            dte4_dates.append(date)
        else:
            date_original = date
            for i in range(7):
                date = date_original - datetime.timedelta(days=i)
                date_str = str(date.date())
                if date_str not in holidays and date.isoweekday() in [1, 2, 3, 4, 5]:
                    dte4_dates.append(date)
                    break
    if selected_dte == "0DTE":
        trading_dates = expiry_dates
    elif selected_dte == "1DTE":
        trading_dates = dte1_dates
    elif selected_dte == "2DTE":
        trading_dates = dte2_dates
    elif selected_dte == "3DTE":
        trading_dates = dte3_dates
    elif selected_dte == "4DTE":
        trading_dates = dte4_dates
    elif selected_dte == "ALLDATES":  
        trading_dates = []
        for file_name in os.listdir(bnf_data_path):
            try:
                date_str = file_name.split('.')[0]
                date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
                if date_obj.year >= 2023:  
                    trading_dates.append(date_obj)
            except Exception as e:
                print(f"Error processing file {file_name}: {e}")
    else:
        raise ValueError("Invalid DTE selection")
    bnf_data = {}
    for date in trading_dates:
        date_str = str(date.date()) 
        try:
            with open(os.path.join(bnf_data_path, date_str + '.pkl'), 'rb') as pkl:
                day_data = pickle.load(pkl)
                bnf_data[date_str] = day_data
        except:
            pass

    with open(bnf_spot_path, 'rb') as pkl:
        bnf_spot = pickle.load(pkl)
        
    def get_nifty_atm_strike(ltp):
        diff = ltp % 50
        if diff > 25:
            atm_strike = ltp - diff +50
        else:
            atm_strike = ltp - diff
        return int(atm_strike)

    for date in trading_dates:
        try:
            max_loss_done = False
            booked_pnl = 0

            ce_entry_time = pe_entry_time = start_time
            current_pnl = 0
            exit_done = False
            ce_sl_hit = False
            pe_sl_hit = False
            ce_reentry_done = False
            pe_reentry_done = False
            ce_pnl = pe_pnl = 0
            date_str = str(date.date())
            ltp = bnf_spot[date_str][start_time]
            atm_strike = get_nifty_atm_strike(ltp)
            ce_strike = atm_strike + strike_distance
            pe_strike = atm_strike - strike_distance
            ce_sell_price = bnf_data[date_str][ce_strike]['CE'][start_time]
            pe_sell_price = bnf_data[date_str][pe_strike]['PE'][start_time]

            ce_sl_price = round(ce_sell_price + (ce_sell_price * sl_percent), 1)
            pe_sl_price = round(pe_sell_price + (pe_sell_price * sl_percent), 1)

            for idx in range(start_time+1, end_time):
                
                if not ce_sl_hit:
                    ce_ltp = bnf_data[date_str][ce_strike]['CE'][idx]
                    if ce_ltp >= ce_sl_price:
                        ce_sl_hit = True
                        ce_pnl = ce_sell_price - ce_ltp
                        trade = [date, ce_entry_time, ce_strike, 'ce', ce_sell_price, ce_ltp, idx, ce_sell_price - ce_ltp]
                        trades.append(trade)
                        booked_pnl += ce_pnl
                        pe_sl_price = pe_sell_price
                if not pe_sl_hit:
                    pe_ltp = bnf_data[date_str][pe_strike]['PE'][idx]
                    if pe_ltp >= pe_sl_price:
                        pe_sl_hit = True
                        pe_pnl = pe_sell_price - pe_ltp
                        trade = [date, pe_entry_time, pe_strike, 'pe', pe_sell_price, pe_ltp, idx, pe_sell_price - pe_ltp]
                        trades.append(trade)
                        ce_sl_price = ce_sell_price
                        booked_pnl += pe_pnl
                
                if not ce_sl_hit and not pe_sl_hit:
                    ce_ltp = bnf_data[date_str][ce_strike]['CE'][idx]
                    pe_ltp = bnf_data[date_str][pe_strike]['PE'][idx]
                    current_pnl = booked_pnl + ce_sell_price - ce_ltp + pe_sell_price - pe_ltp
                
                elif ce_sl_hit and not pe_sl_hit:
                    pe_ltp = bnf_data[date_str][pe_strike]['PE'][idx]
                    current_pnl = booked_pnl + pe_sell_price - pe_ltp

                
                elif not ce_sl_hit and pe_sl_hit:
                    ce_ltp = bnf_data[date_str][ce_strike]['CE'][idx]
                    current_pnl = booked_pnl + ce_sell_price - ce_ltp
                
                if re_entry:
                    if ce_sl_hit:
                        if re_entry and ce_reentry_done == False:
                            ce_ltp = bnf_data[date_str][ce_strike]['CE'][idx]
                            if ce_ltp <= ce_sell_price:
                                ce_reentry_done = True
                                ce_sl_hit = False
                                ce_entry_time = idx
                                ce_sell_price = bnf_data[date_str][ce_strike]['CE'][idx]
                                ce_sl_price = ce_sell_price + 50
                                ce_pnl = 0
                    
                    if pe_sl_hit:
                        if re_entry and pe_reentry_done == False:
                            pe_ltp = bnf_data[date_str][pe_strike]['PE'][idx]
                            if pe_ltp <= pe_sell_price:
                                pe_reentry_done = True
                                pe_sl_hit = False
                                pe_entry_time = idx
                                pe_sell_price = bnf_data[date_str][pe_strike]['PE'][idx]
                                pe_sl_price = pe_sell_price + 50
                                pe_pnl = 0

                running_pnl = current_pnl
                if running_pnl < max_loss_points:
                    max_loss_done = True

                if idx == end_time - 1 or max_loss_done:
                    if not ce_sl_hit:
                        ce_ltp = bnf_data[date_str][ce_strike]['CE'][idx]
                        trade = [date, ce_entry_time, ce_strike, 'ce', ce_sell_price, ce_ltp, idx, ce_sell_price - ce_ltp]
                        trades.append(trade)
                    if not pe_sl_hit:
                        pe_ltp = bnf_data[date_str][pe_strike]['PE'][idx]
                        trade = [date, pe_entry_time, pe_strike, 'pe', pe_sell_price, pe_ltp, idx, pe_sell_price - pe_ltp]
                        trades.append(trade)
                    break

                if running_pnl > target_points:
                    if not ce_sl_hit:
                        ce_ltp = bnf_data[date_str][ce_strike]['CE'][idx]
                        trade = [date, ce_entry_time, ce_strike, 'ce', ce_sell_price, ce_ltp, idx, ce_sell_price - ce_ltp]
                        trades.append(trade)
                    if not pe_sl_hit:
                        pe_ltp = bnf_data[date_str][pe_strike]['PE'][idx]
                        trade = [date, pe_entry_time, pe_strike, 'pe', pe_sell_price, pe_ltp, idx, pe_sell_price - pe_ltp]
                        trades.append(trade)
                    break
        except Exception as e:
            pass

    trades_df = pd.DataFrame(trades, columns = ["date", "entry_time", "strike", 'ce', "sell_price", "buy_price", "exit_time", "pnl"])
    trades_df["pnl2"] = trades_df["sell_price"] - trades_df["buy_price"]
    trades_df['pnl'] = (trades_df['sell_price'] - trades_df['sell_price'] * 0.005) - (trades_df['buy_price'] + trades_df['buy_price'] * 0.005)
    trades_df["count"] = 1

    if get_trades:
        return trades_df

    trades_df = trades_df.groupby(['date']).sum().reset_index()
    trades_df

    trades_df['pnl'] = trades_df['pnl'] * 40
    trades_df['equity'] = trades_df['pnl'].cumsum()

    def get_drawdown_start_dt(trades_df, max_drawdown):
        max_drawdown_idx = trades_df[trades_df['drawdown'] == max_drawdown].index[0]
        for i in reversed(range(max_drawdown_idx)):
            if trades_df['drawdown'].iloc[i] == 0:
                return trades_df['date'].iloc[i+1]

    def get_max_winning_and_losing_streak(trades_df):
        trades_df['profit'] = trades_df['pnl'] > 0
        trades_df['start_of_streak'] = trades_df.profit.ne(trades_df['profit'].shift())
        trades_df['streak_id'] = trades_df['start_of_streak'].cumsum()
        trades_df['streak_count'] = trades_df.groupby('streak_id').cumcount() + 1
        max_winning_streak = trades_df[trades_df['profit'] == True]['streak_count'].max()
        max_losing_streak = trades_df[trades_df['profit'] == False]['streak_count'].max()
        return max_winning_streak, max_losing_streak

    total_pnl = trades_df['pnl'].sum()
    avg_pnl_per_trade = trades_df['pnl'].sum() / trades_df.shape[0]
    max_profit = trades_df['pnl'].max()
    max_loss = trades_df['pnl'].min()
    if max_loss >0:
        max_loss = 0
    total_trades = trades_df.shape[0]
    win_percent = round(trades_df[trades_df['pnl'] >0].shape[0] / trades_df.shape[0] *100, 2)
    lose_percent = round(trades_df[trades_df['pnl'] <=0].shape[0] / trades_df.shape[0] *100, 2)
    avg_profit_on_winning_trades = trades_df[trades_df['pnl'] >0]['pnl'].mean()
    avg_loss_on_losing_trades = trades_df[trades_df['pnl'] <=0]['pnl'].mean()
    roll_max = trades_df['equity'].rolling(window=252, min_periods=1).max()
    trades_df['drawdown'] = roll_max - trades_df['equity']
    max_drawdown = trades_df['drawdown'].max()
    date_of_max_drawdown = trades_df[trades_df['drawdown'] == max_drawdown]['date'].iloc[-1]
    drawdown_start_dt = get_drawdown_start_dt(trades_df, max_drawdown)
    expectancy = round((abs(avg_profit_on_winning_trades/avg_loss_on_losing_trades) * win_percent - lose_percent)/100, 2)
    max_winning_streak, max_losing_streak = get_max_winning_and_losing_streak(trades_df)
    max_dd_index = trades_df[trades_df['drawdown'] == max_drawdown].index[0]
    max_dd_end_index = -1
    for counter, dd in enumerate(trades_df['drawdown'].iloc[max_dd_index:]):
        if dd == 0:
            max_dd_end_index = max_dd_index + counter -1
            break
    max_dd_end_date = None
    if max_dd_end_index != -1:
        max_dd_end_date = trades_df['date'].iloc[max_dd_end_index]
    trades_df['drawdown_phase'] = trades_df['drawdown'] > 0
    trades_df['start_of_drawdown_streak'] = trades_df.drawdown_phase.ne(trades_df['drawdown_phase'].shift())
    trades_df['drawdown_streak_id'] = trades_df['start_of_drawdown_streak'].cumsum()
    trades_df['drawdown_streak_count'] = trades_df.groupby('drawdown_streak_id').cumcount() + 1
    dd_df = trades_df[trades_df['drawdown_phase'] == True]
    longest_drawdown_streak = dd_df['drawdown_streak_count'].max()
    longest_drawdown_duration = 0
    try:
        longest_drawdown_end_index = dd_df[dd_df["drawdown_streak_count"] == longest_drawdown_streak].index[0]
        longest_drawdown_start_date = trades_df['date'].iloc[longest_drawdown_end_index-longest_drawdown_streak+1]
        longest_drawdown_end_date = trades_df['date'].iloc[longest_drawdown_end_index]

        if type(longest_drawdown_start_date) == str:
            longest_drawdown_start_date = datetime.datetime.strptime(longest_drawdown_start_date, "%Y-%m-%d")
            longest_drawdown_end_date = datetime.datetime.strptime(longest_drawdown_end_date, "%Y-%m-%d")
            drawdown_start_dt = datetime.datetime.strptime(drawdown_start_dt, "%Y-%m-%d")
        longest_drawdown_duration = longest_drawdown_end_date - longest_drawdown_start_date
    except:
        longest_drawdown_end_index = None
        longest_drawdown_start_date = None
        longest_drawdown_end_date = None

    if max_dd_end_date == None:
        max_dd_end_date = trades_df['date'].iloc[-1]
    if type(max_dd_end_date) == str:
        max_dd_end_date = datetime.datetime.strptime(max_dd_end_date, "%Y-%m-%d")
    try:
        max_dd_duration = max_dd_end_date - drawdown_start_dt
    except:
        max_dd_duration = None

    return [avg_pnl_per_trade, max_profit, max_loss, int(max_drawdown), avg_profit_on_winning_trades, avg_loss_on_losing_trades, expectancy, longest_drawdown_duration, win_percent, max_winning_streak, max_losing_streak]