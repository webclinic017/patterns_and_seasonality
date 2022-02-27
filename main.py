import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import glob
import datetime
import os.path

pd.options.mode.chained_assignment = None  # default='warn'

from miscellaneous import *

class Seasonality_Outright:
    def __init__(self,main,code,contr,exch,days):

        self.main = main
        self.code = code
        self.contr = contr
        self.exch = exch
        self.days = days

        self.duration = '230 D'
        self.bar_size = '1 day'

        self.range_y = range(2007, 2023)
        self.holding_days = range(9, 60)

        # these are the loops for constructing the main dataframe, before the pattern finder algo
        self.loop_0 = []
        self.loop_1 = []

        # this is for normalized dataframe to search for correlations and starts-ends when the current futures start-end
        self.normalized_dataframe = []

        # this is for normalized dataframe till the expiration
        self.main_dataframe = []

        # this is for the dataframe which includes the rolling returns (as per holding_days) for every contract
        self.patterns_dataframe = []

        # save results for every period - 15,10,5, as per the observed holding_days parameter
        self.splitted_dataframe = []

        # save the results for the observed holding_days parameter
        self.table_for_days = []

        # save the best results as per APD for the observed days for the week
        self.best_df = []

        # save all final results for every market here
        self.final_table = []

    def main_func(self):
        fut = FuturesData()

        # take the timeseries for the current contract
        futures_price = fut.futures(self.main, self.contr, self.exch, self.duration, self.bar_size)
        futures_price['date'] = pd.to_datetime(futures_price['date']).dt.strftime('%m/%d')
        futures_price.set_index('date', inplace=True)

        range_m = fut.months(self.code)

        # Start looping through every month
        for m in range_m:
            del self.loop_0[:]
            # Continue finding price/returns for the specific month in range_m for every year in range_y
            for r in self.range_y:
                file = open("C:/Users/Kubrat/Desktop/Python/" + self.main + "/" + self.code + ".txt", "r")
                content = file.read()
                symbols = content.split(",")

                for s in symbols:

                    # If s contains the last 2 digits of y - continue (example: if we look at zwh between 2016 and 2020,
                    # we want to skipcontracts like zwh21)
                    year = str(r)
                    year = year[-1:]

                    if year in s:
                        df = pd.read_csv("C:/Users/Kubrat/Desktop/Python/" + self.main + "/" + s + ".csv")
                        df['date'] = pd.to_datetime(df['date'], errors='coerce')
                        df['Month'] = df['date'].dt.month

                        df = df[-210:]
                        df = df.loc[(df['Month'] == m)]

                        df['date'] = pd.to_datetime(df['date']).dt.strftime('%m/%d')
                        df.set_index('date', inplace=True)

                        df = df[['close']]

                        df = df.rename(columns={'close': s})

                        self.loop_0.append(df)
            df_loop_0 = pd.concat(self.loop_0)
            df_loop_0.reset_index(inplace=True)
            df_loop_0 = df_loop_0.groupby(df_loop_0['date']).first()

            self.loop_1.append(df_loop_0)

        ####################### Seasonality constructor for 15,10,5 years and best correlating month #######################
        df_loop_1 = pd.concat(self.loop_1)

        # start from first date in the main dataframe with all contracts. This is the starting point of the current contract
        start_date = df_loop_1.index[3]

        # end the main dataframe with all contracts at the date where the current contract ends. Make separate dataframe.
        end_date = futures_price.index[-1]
        futures_price = futures_price[start_date:end_date]
        df_corr_search = pd.concat([df_loop_1, futures_price], axis=1)[:end_date]

        # Perform ffill and bfill
        df_corr_search = df_corr_search.fillna(method='ffill').fillna(method='bfill')

        # index the data to prepare it for correlation dataframe
        for column_0 in df_corr_search.columns:
            corr_per_rs = df_corr_search[[column_0]].copy()

            # calculate rolling retuns
            max_val = corr_per_rs.max()
            min_val = corr_per_rs.min()

            corr_per_rs['Index'] = (corr_per_rs - min_val) / (max_val - min_val)

            corr_per_rs = corr_per_rs.rename(columns={'Index': column_0 + '_ix'})
            corr_per_rs = corr_per_rs[[column_0 + '_ix']]

            self.normalized_dataframe.append(corr_per_rs)

        # Find correlation
        df_corr_concat = pd.concat(self.normalized_dataframe, axis=1)
        correl = df_corr_concat.corr()

        # Find best correlating contract and save its column name and correlation value.
        best_corr_contr = correl.loc[correl.iloc[:, -1] == (correl.iloc[:, -1][:-1].max())].index[-1]
        best_corr_contr = best_corr_contr[:-3]  # delete '_ix' from name so that it will be found in main_df
        best_corr_value = round((correl.iloc[:, -1][:-1].max()), 2)

        # save the ffill & bfill actual futures contract prices
        futures_actual = df_corr_search[[self.main]]

        main_df = df_loop_1.fillna(method='ffill').fillna(method='bfill')

        # save the timeseries of the best correlation contract
        corr_contr = main_df[[best_corr_contr]]

        # make new dataframe like df_corr_concat with indexing but include all the days
        for column_1 in main_df.columns:
            df_main_1 = main_df[[column_1]].copy()

            # calculate rolling retuns
            max_val = df_main_1.max()
            min_val = df_main_1.min()

            df_main_1['Index'] = (df_main_1 - min_val) / (max_val - min_val)

            df_main_1 = df_main_1.rename(columns={'Index': column_1 + '_ix'})
            df_main_1 = df_main_1[[column_1 + '_ix']]

            self.main_dataframe.append(df_main_1)

        df_main_indexed = pd.concat(self.main_dataframe, axis=1)

        # save 5,10,15 years seasonality in seperate dataframes
        five = pd.DataFrame(data=np.mean(df_main_indexed.iloc[:, 10:], axis=1), columns={self.main + self.code[-1] + '_' + '5Y'})
        ten = pd.DataFrame(data=np.mean(df_main_indexed.iloc[:, 5:], axis=1), columns={self.main + self.code[-1] + '_' + '10Y'})
        fifteen = pd.DataFrame(data=np.mean(df_main_indexed, axis=1), columns={self.main + self.code[-1] + '_' + '15Y'})

        # normalize best correlating contract and actual futures contract
        max_corr_contr = corr_contr.max()
        min_corr_contr = corr_contr.min()
        corr_contr['indexed'] = (corr_contr - min_corr_contr) / (max_corr_contr - min_corr_contr)
        corr_contr = corr_contr[['indexed']]
        corr_contr = corr_contr.rename(columns={'indexed': best_corr_contr})

        max_fut_actual = futures_actual.max()
        min_fut_actual = futures_actual.min()
        futures_actual['indexed'] = (futures_actual - min_fut_actual) / (max_fut_actual - min_fut_actual)
        futures_actual = futures_actual[['indexed']]
        futures_actual = futures_actual.rename(columns={'indexed': self.main})

        # find correlations for the actual futures and the 15,10,5 years period
        mean_15Y = pd.DataFrame(data=np.mean(df_corr_concat.iloc[:, :15], axis=1))
        corr_15Y = round((mean_15Y.iloc[:, 0].corr(futures_actual.iloc[:, 0])), 2)

        mean_10Y = pd.DataFrame(data=np.mean(df_corr_concat.iloc[:, 5:15], axis=1))
        corr_10Y = round((mean_10Y.iloc[:, 0].corr(futures_actual.iloc[:, 0])), 2)

        mean_5Y = pd.DataFrame(data=np.mean(df_corr_concat.iloc[:, 10:15], axis=1))
        corr_5Y = round((mean_5Y.iloc[:, 0].corr(futures_actual.iloc[:, 0])), 2)

        # concatenate 5,10,15 years seasonality, best correlating contract and actual contract
        df_final = pd.concat([five, ten, fifteen, corr_contr, futures_actual], axis=1)

        # rename best correlating contract and actual contract
        df_final = df_final.rename(
            columns={self.main + self.code[-1] + '_' + '15Y': self.main + self.code[-1] + '_' + '15Y' + ', ' + 'corr= ' + str(corr_15Y),
                     self.main + self.code[-1] + '_' + '10Y': self.main + self.code[-1] + '_' + '10Y' + ', ' + 'corr= ' + str(corr_10Y),
                     self.main + self.code[-1] + '_' + '5Y': self.main + self.code[-1] + '_' + '5Y' + ', ' + 'corr= ' + str(corr_5Y),
                     best_corr_contr: best_corr_contr + ', ' + 'corr= ' + str(best_corr_value),
                     self.main: self.main + self.code[-1] + self.contr[2:4]})

        #################### Pattern Finder #######################
        # start looping through holding days, to find best possible patterns for each holding period
        for hold in self.holding_days:

            # start clean for every new holding_days parameter
            del self.patterns_dataframe[:]
            del self.splitted_dataframe[:]

            # find the rolling returns for every column (every contract)
            for column in main_df.columns:
                patterns_df = main_df[[column]].copy()

                # calculate rolling retuns
                patterns_df['Rets'] = patterns_df.diff()
                patterns_df['Returns'] = patterns_df['Rets'].rolling(hold).sum()

                # shift back returns and save only that column without the last rd values (NaN values)
                patterns_df = patterns_df.rename(columns={'Returns': column + '_ret'}).shift(-hold)
                patterns_df = patterns_df[[column + '_ret']]

                self.patterns_dataframe.append(patterns_df)

            # find the winrate based on positive / sum occurences and also the average returns for the last 15,10,5 years
            for years in [15, 10, 5]:
                # But first construct the new dataframe with the rolling return values
                patterns_main = pd.concat(self.patterns_dataframe, axis=1)

                if years == 15:
                    patterns_main['Pos'] = np.sum(patterns_main > 0, axis=1)
                    patterns_main['Neg'] = np.sum(patterns_main < 0, axis=1)
                    patterns_main['WR'] = patterns_main['Pos'] / years
                    patterns_main['Avg'] = np.mean(patterns_main.iloc[:, :15], axis=1)
                    patterns_main = patterns_main.iloc[:, 15:]
                    patterns_main['Years'] = years
                elif years == 10:
                    patterns_main = patterns_main.iloc[:, 5:]
                    patterns_main['Pos'] = np.sum(patterns_main > 0, axis=1)
                    patterns_main['Neg'] = np.sum(patterns_main < 0, axis=1)
                    patterns_main['WR'] = patterns_main['Pos'] / years
                    patterns_main['Avg'] = np.mean(patterns_main.iloc[:, :10], axis=1)
                    patterns_main = patterns_main.iloc[:, 10:]
                    patterns_main['Years'] = years
                elif years == 5:
                    patterns_main = patterns_main.iloc[:, 10:]
                    patterns_main['Pos'] = np.sum(patterns_main > 0, axis=1)
                    patterns_main['Neg'] = np.sum(patterns_main < 0, axis=1)
                    patterns_main['WR'] = patterns_main['Pos'] / years
                    patterns_main['Avg'] = np.mean(patterns_main.iloc[:, :5], axis=1)
                    patterns_main = patterns_main.iloc[:, 5:]
                    patterns_main['Years'] = years

                # Make copy of patterns_main. Exclude the data for the rolling returns and leave only Pos,Neg,WR,Avg.
                # reset index, find the Starting and Ending date and then set the index again.
                results_main = patterns_main.copy()
                results_main.reset_index(inplace=True)
                results_main['Start'] = results_main['date']
                results_main['Hold'] = hold
                results_main['End'] = results_main['date'].shift(-hold)
                results_main['APD'] = results_main['Avg'] / results_main['Hold']
                results_main.set_index('date', inplace=True)

                # exclude the last NaN values
                results_main = results_main[:-hold]

                # take rows with Winrate above 0.8(below 0.2) for 15Y, above 0.9(below 0.1) for 10Y, equal to 1.0(equal to 0) for 5Y
                # also Pos + Neg should be equal to Years in order to ignore s.th. like: Pos=0, Neg=4 for 5Y period
                if years == 15:
                    results_main = results_main.loc[((results_main['WR'] >= 0.8) | (results_main['WR'] <= 0.2))]
                    results_main = results_main.loc[
                        ((results_main['Pos'] + results_main['Neg']) == results_main['Years'])]
                    results_main['Dir'] = np.where(results_main['WR'] >= 0.8, 1, -1)
                    results_main['WR'] = np.where(results_main['Dir'] == 1, results_main['WR'], 1 - results_main['WR'])

                elif years == 10:
                    results_main = results_main.loc[((results_main['WR'] >= 0.9) | (results_main['WR'] <= 0.1))]
                    results_main = results_main.loc[
                        ((results_main['Pos'] + results_main['Neg']) == results_main['Years'])]
                    results_main['Dir'] = np.where(results_main['WR'] >= 0.9, 1, -1)
                    results_main['WR'] = np.where(results_main['Dir'] == 1, results_main['WR'], 1 - results_main['WR'])

                elif years == 5:
                    results_main = results_main.loc[((results_main['WR'] == 1) | (results_main['WR'] == 0))]
                    results_main = results_main.loc[
                        ((results_main['Pos'] + results_main['Neg']) == results_main['Years'])]
                    results_main['Dir'] = np.where(results_main['WR'] == 1, 1, -1)
                    results_main['WR'] = np.where(results_main['Dir'] == 1, results_main['WR'], 1 - results_main['WR'])

                # Start arranging the final data for table
                results_pre = fut.market_symbol(self.main,results_main)
                results_pre = fut.contract_symbol(self.code,results_main)

                self.splitted_dataframe.append(results_pre)

            # after the loop for the last 15,10,5 years, concatenate the results
            results_final = pd.concat(self.splitted_dataframe)

            # multiply Avg and APD with Dir, so that if Dir=-1, and Avg=-0.1 and APD=-0.005, the Avg to be +0.1 and APD +0.005
            results_final['Avg'] = results_final['Avg'] * results_final['Dir']
            results_final['APD'] = results_final['APD'] * results_final['Dir']

            # take only the rows which correspond to the days for the observed week
            for day in self.days:
                self.table_for_days.append(results_final.loc[(results_final['Start'] == day)])
        # concatenate the corresponding results. dfz because shorter name for formatting_df function
        dfz = pd.concat(self.table_for_days)

        # perform formatting
        dfz_1 = fut.formatting_df(self.main,dfz)

        for years in [15, 10, 5]:
            filter_best = dfz.loc[(dfz['Years'] == years)]
            filter_best = filter_best.loc[(filter_best['APD'] == filter_best['APD'].max())]

            self.best_df.append(filter_best)

        pre_final = pd.concat(self.best_df)

        # final touches
        pre_final['Win'] = np.where(pre_final['Dir'] == 1, pre_final['Pos'], pre_final['Neg'])
        pre_final['All'] = pre_final['Pos'] + pre_final['Neg']
        pre_final['WR'] = pre_final['WR'].apply(lambda x: "{:.0%}".format((x)))

        pre_final_df = pd.DataFrame(
            data={'Пазар': pre_final['Market'], 'Контракт': pre_final['Contract'], 'Посока': pre_final['Dir'],
                  'Начало': pre_final['Start'], 'Дни': pre_final['Hold'], 'Край': pre_final['End'],
                  'Години': pre_final['Years'], '# Печеливши': pre_final['Win'], 'Общо': pre_final['All'],
                  '% Печеливши': pre_final['WR'], 'Ø Печалба': pre_final['Avg'],
                  'Ø Печалба/ден': pre_final['APD'], 'Ø Печалба/контракт': pre_final['PPC']})
        pre_final_df = pre_final_df.set_index('Пазар')

        # append the final results of every market
        self.final_table.append(pre_final_df)

        patterns_table = pd.concat(self.final_table)

        return df_final, patterns_table

symbol = 'zs'
contract_code = 'zsk'
contract_month = '202205'
exchange = 'ECBOT'
days = ['02/21','02/22','02/23','02/24','02/25']


seasonality = Seasonality_Outright(symbol,contract_month,exchange,exchange,days)
df,patterns = seasonality.main_func()

df.to_clipboard()
print(df,patterns)

