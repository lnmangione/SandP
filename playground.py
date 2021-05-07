import pandas as pd
import datetime


def load_df_daily():
    # Load and format daily dataset
    df_daily = pd.read_csv("SP_Daily_1997-2020.csv")
    df_daily = df_daily.drop(['High', 'Low', 'Volume', 'OpenInt'], axis=1)
    df_daily = df_daily.iloc[::-1]  # reverse the dataframe so chronological
    df_daily['Date'] = pd.to_datetime(df_daily['Date'], infer_datetime_format=True)

    # Calculate percent change
    df_daily['PercentChange'] = 100 * (df_daily['Close'] / df_daily['Open'] - 1)

    # Calculate EMA's and drop initial rows
    df_daily['10DayEMA'] = df_daily['Close'].ewm(span=10, min_periods=10, adjust=False).mean()
    df_daily['40DayEMA'] = df_daily['Close'].ewm(span=40, min_periods=40, adjust=False).mean()
    df_daily = df_daily.reset_index(drop=True)
    df_daily = df_daily.drop(list(range(39)))
    df_daily = df_daily.reset_index(drop=True)
    return df_daily


def get_daily_close_stats(df):
    df_red = df.loc[df['Close'] < df['Open']]
    df_green = df.loc[df['Close'] > df['Open']]
    df_neutral = df.loc[df['Close'] == df['Open']]

    print(f'Total days: {len(df)}')
    print(f'Days closing in red: {len(df_red)}, green: {len(df_green)}, unchanged: {len(df_neutral)}')


# load dataset, select cols, reorder, reset index, reformat types
def load_df_5min():
    df_5min = pd.read_csv("SP_5min_2005-2020.csv")
    df_5min = df_5min.drop(['IncVol', 'Volume', 'Open', 'Close', 'High'], axis=1)
    df_5min = df_5min.iloc[::-1]
    df_5min = df_5min.reset_index(drop=True)
    df_5min['Date'] = pd.to_datetime(df_5min['Date'], infer_datetime_format=True)
    df_5min['Time'] = pd.to_datetime(df_5min['Time'], infer_datetime_format=True)
    df_5min['Time'] = df_5min['Time'].dt.time
    return df_5min


'''
df_5min_filtered (Date, Time, Low) of 5 minute data, with many rows per day -> 
to dataframe of (Date, Time, Low) with one row per day, Time = time of day's low
'''
def get_low_times(df_5min_filtered):
    # group by date, then find low time
    indx = df_5min_filtered.groupby('Date')['Low'].idxmin()
    return df_5min_filtered.loc[indx]


'''
df_dataset: the entire daily dataset
df_subset: a subset of the daily dataset

Prints stats about subset (frequency, price increase mean/median)
'''
def print_daily_subset_stats(df_dataset, df_subset):
    subset_frequency = round(len(df_subset) / len(df_dataset), 4)
    print(f'{subset_frequency * 100}% of time, in this state')

    price_increase_median = round(df_subset['PercentChange'].median(), 3)
    price_increase_mean = round(df_subset['PercentChange'].mean(), 3)
    print(f'{price_increase_median}% median price increase in this state')
    print(f'{price_increase_mean}% mean price increase in this state')


'''
df_daily_filtered: data from daily dataframe, filtered on some condition (e.g.: close > 10d > 40d)
df_5min_lows: data from 5 min dataframe, one row per day, showing time low was made

Prints the mean / median time of low and writes data to csv
'''
def print_low_stats(df_daily_filtered, df_5min_lows, trading_period, csv_name):
    df_merged_lows = pd.merge(df_daily_filtered, df_5min_lows, on='Date')

    # Print metrics (median, mean)
    low_times_only = df_merged_lows.sort_values(by='Time')['Time'].reset_index(drop=True)
    median_time = low_times_only.iloc[len(df_merged_lows) // 2]
    print(f'{median_time} is median low time of day during {trading_period}')

    mean_hours = low_times_only.apply(lambda x: x.hour * 60 + x.minute).mean() / 60
    mean_time = f'{int(mean_hours)}:{round((mean_hours % 1) * 60, 4)}'
    print(f'{mean_time} is mean low time of day during {trading_period}')

    # df_merged_low_times = pd.Series.to_frame(df_merged_lows.groupby('Time').count()['Date']).rename(columns={'Date': 'Count'})
    # df_merged_low_times.to_csv('df_v_full_low_times.csv')
    df_merged_lows.to_csv(csv_name)


# ======================================================================================================================


df_daily = load_df_daily()

print('\n======= Part 1: Daily Close Stats =======')
get_daily_close_stats(df_daily)


# ======= Load 5 min data for parts 2 and 3 =======
df_5min = load_df_5min()

# filter by regular working hours
df_5min_regular = df_5min.loc[(df_5min['Time'] >= datetime.time(9, 30)) & (datetime.time(16, 0) >= df_5min['Time'])]
df_5min_regular_lows = get_low_times(df_5min_regular)

# filter by full hours, time < 9:30 means true trading day is yesterday
df_5min_full = df_5min.loc[(df_5min['Time'] <= datetime.time(16, 0)) | (df_5min['Time'] > datetime.time(18, 0))]
mask = df_5min_full['Time'] < datetime.time(9, 30)
df_5min_full.loc[mask, 'Date'] = df_5min_full.loc[mask, 'Date'] - pd.DateOffset(1)
df_5min_full_lows = get_low_times(df_5min_full)


print('\n======= Part 2: Strictly Rising (close > 10d > 40d) =======')
df_rising = df_daily.loc[(df_daily['Close'] > df_daily['10DayEMA']) & (df_daily['10DayEMA'] > df_daily['40DayEMA'])]
print_daily_subset_stats(df_daily, df_rising)

print_low_stats(df_rising, df_5min_regular_lows, 'regular hours', 'rising_regular_with_lows.csv')
print_low_stats(df_rising, df_5min_full_lows, 'full hours', 'rising_full_with_lows.csv')


print('\n======= Part 3: V-shape (close > 10d, close > 40d, but 10d < 40d) =======')
df_v = df_daily.loc[(df_daily['Close'] > df_daily['10DayEMA']) & (df_daily['Close'] > df_daily['10DayEMA']) &
                    (df_daily['10DayEMA'] < df_daily['40DayEMA'])]
print_daily_subset_stats(df_daily, df_v)

print_low_stats(df_v, df_5min_regular_lows, 'regular hours', 'v_shape_regular_with_lows.csv')
print_low_stats(df_v, df_5min_full_lows, 'full hours', 'v_shape_full_with_lows.csv')
