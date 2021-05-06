import pandas as pd


def get_df_daily():
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


def daily_close_stats(df):
    df_red = df.loc[df['Close'] < df['Open']]
    df_green = df.loc[df['Close'] > df['Open']]
    df_neutral = df.loc[df_daily['Close'] == df['Open']]

    print(f'Total days: {len(df)}')
    print(f'Days closing in red: {len(df_red)}, green: {len(df_green)}, unchanged: {len(df_neutral)}')


# ======================================================================================================================

df_daily = get_df_daily()

print('\n======= Part 1: Daily Close Stats =======')
daily_close_stats(df_daily)


print('\n======= Part 2: Strictly Rising (close > 10d > 40d) =======')

df_rising = df_daily.loc[df_daily['Close'] > df_daily['10DayEMA']]
df_rising = df_rising.loc[df_rising['10DayEMA'] > df_rising['40DayEMA']]

rising_frequency = round(len(df_rising) / len(df_daily), 4)
print(f'{rising_frequency * 100}% of time, close > 10d > 40d')

price_increase_median = round(df_rising['PercentChange'].median(), 3)
price_increase_mean = round(df_rising['PercentChange'].mean(), 3)
print(f'{price_increase_median}% median price increase in this state')
print(f'{price_increase_mean}% average price increase in this state')







# df_5min = pd.read_csv("SP_5min_2005-2020.csv")
# print(df_5min.head(10))
# df_5min = df_5min.iloc[::-1]
# print(df_5min.head(10))
# df_5min['Date'] = pd.to_datetime(df_5min['Date'], infer_datetime_format=True)
# df_5min['Time'] = pd.to_datetime(df_5min['Time'], infer_datetime_format=True)
#
# print(df_5min.head(10))
#
# # df_5min_working = df_5min.loc[df_5min['Time'] > ]
#
# grouped = df_5min.groupby("Date")
#
# print(len(grouped))
#
# # print(df_5min.head(10))
# #
# # print(df_5min.dtypes)
#
# print(grouped.head(20))
# print(grouped.size())
#
# print(df_5min.head(10))

