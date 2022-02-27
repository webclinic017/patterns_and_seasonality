from ib_insync import *

util.startLoop()
ib = IB()

# us this for TWS (Workstation)
ib.connect('127.0.0.1', 7497, 335)

class FuturesData:
    def __init__(self):
        pass

    # Download futures data from IB
    def futures(self, main, contr, exch, duration, bar_size):
        fut = Future(main, contr, exch, includeExpired=True)
        fut_contr = ib.reqHistoricalData(fut,
                                         endDateTime='',
                                         durationStr=duration,
                                         barSizeSetting=bar_size,
                                         whatToShow='TRADES',
                                         useRTH=False,
                                         formatDate=1)
        df_contr = util.df(fut_contr)
        df_contr[main] = df_contr['close']
        df_contr = df_contr[['date', main]]

        return df_contr

    # Assign month range depending on the contract
    def months(self,code):
        if code[-1][-1] == 'f':
            self.range_months = 4, 5, 6, 7, 8, 9, 10, 11, 12, 1
        elif code[-1][-1] == 'g':
            self.range_months = 5, 6, 7, 8, 9, 10, 11, 12, 1, 2
        elif code[-1][-1] == 'h':
            self.range_months = 6, 7, 8, 9, 10, 11, 12, 1, 2, 3
        elif code[-1][-1] == 'j':
            self.range_months = 7, 8, 9, 10, 11, 12, 1, 2, 3, 4
        elif code[-1][-1] == 'k':
            self.range_months = 8, 9, 10, 11, 12, 1, 2, 3, 4, 5
        elif code[-1][-1] == 'm':
            self.range_months = 9, 10, 11, 12, 1, 2, 3, 4, 5, 6
        elif code[-1][-1] == 'n':
            self.range_months = 10, 11, 12, 1, 2, 3, 4, 5, 6, 7
        elif code[-1][-1] == 'q':
            self.range_months = 11, 12, 1, 2, 3, 4, 5, 6, 7, 8
        elif code[-1][-1] == 'u':
            self.range_months = 12, 1, 2, 3, 4, 5, 6, 7, 8, 9
        elif code[-1][-1] == 'v':
            self.range_months = 1, 2, 3, 4, 5, 6, 7, 8, 9, 10
        elif code[-1][-1] == 'x':
            self.range_months = 2, 3, 4, 5, 6, 7, 8, 9, 10, 11
        elif code[-1][-1] == 'z':
            self.range_months = 3, 4, 5, 6, 7, 8, 9, 10, 11, 12

        return self.range_months

    def market_symbol(self,d,results_main):
        self.results_main = results_main
        if d == 'zw':
            results_main['Market'] = 'Wheat (CBOT)'
        elif d == 'zc':
            results_main['Market'] = 'Corn (CBOT)'
        elif d == 'zs':
            results_main['Market'] = 'Soybean (CBOT)'
        elif d == 'zl':
            results_main['Market'] = 'Soybean oil (CBOT)'
        elif d == 'zm':
            results_main['Market'] = 'Soybean meal (CBOT)'
        elif d == 'ke':
            results_main['Market'] = 'Wheat (KCBT)'
        elif d == 'ebm':
            results_main['Market'] = 'Wheat (MATIF)'
        elif d == 'eco':
            results_main['Market'] = 'Rapeseeds (MATIF)'
        elif d == 'ema':
            results_main['Market'] = 'Corn (MATIF)'
        elif d == 'cl':
            results_main['Market'] = 'Crude oil (NYMEX)'
        elif d == 'ng':
            results_main['Market'] = 'Natural gas (NYMEX)'
        elif d == 'zn':
            results_main['Market'] = '10Y US T-note (CBOT)'
        elif d == 'es':
            results_main['Market'] = 'E-mini S&P 500 (CME)'

        return results_main

    def contract_symbol(self,code,results_main):
        if code[-1] == 'f':  # If the last letter of the code is 'f', then Contract = 'Януари'
            results_main['Contract'] = 'Януари'
        elif code[-1] == 'g':
            results_main['Contract'] = 'Февруари'
        elif code[-1] == 'h':
            results_main['Contract'] = 'Март'
        elif code[-1] == 'j':
            results_main['Contract'] = 'Април'
        elif code[-1] == 'k':
            results_main['Contract'] = 'Май'
        elif code[-1] == 'm':
            results_main['Contract'] = 'Юни'
        elif code[-1] == 'n':
            results_main['Contract'] = 'Юли'
        elif code[-1] == 'q':
            results_main['Contract'] = 'Август'
        elif code[-1] == 'u':
            results_main['Contract'] = 'Септември'
        elif code[-1] == 'v':
            results_main['Contract'] = 'Октомври'
        elif code[-1] == 'x':
            results_main['Contract'] = 'Ноември'
        elif code[-1] == 'z':
            results_main['Contract'] = 'Декември'

        return results_main

    # perform formatting for the specific contract to find profit per contract (PPC)
    def formatting_df(self,d,dfz):
        if d == 'zw' or d == 'zc' or d == 'zs' or d == 'ke':
            dfz['PPC'] = round((dfz['Avg'] / 100) * 5000).apply(lambda x: "{:.0f} usd".format((x)))
            dfz['Avg'] = dfz['Avg'].apply(lambda x: "{:.2f} cents".format((x)))
            dfz['APD'] = dfz['APD'].apply(lambda x: "{:.2f} cents".format((x)))

        elif d == 'zl':
            dfz['PPC'] = round((dfz['Avg'] / 100) * 60000).apply(lambda x: "{:.0f} usd".format((x)))
            dfz['Avg'] = dfz['Avg'].apply(lambda x: "{:.2f} cents".format((x)))
            dfz['APD'] = dfz['APD'].apply(lambda x: "{:.2f} cents".format((x)))

        elif d == 'zm':
            dfz['PPC'] = round((dfz['Avg']) * 100).apply(lambda x: "{:.0f} usd".format((x)))
            dfz['Avg'] = dfz['Avg'].apply(lambda x: "{:.2f} usd".format((x)))
            dfz['APD'] = dfz['APD'].apply(lambda x: "{:.2f} usd".format((x)))

        elif d == 'ebm' or d == 'eco' or d == 'ema':
            dfz['PPC'] = round((dfz['Avg']) * 50).apply(lambda x: "{:.0f} eur".format((x)))
            dfz['Avg'] = dfz['Avg'].apply(lambda x: "{:.2f} eur".format((x)))
            dfz['APD'] = dfz['APD'].apply(lambda x: "{:.2f} eur".format((x)))

        elif d == 'cl':
            dfz['PPC'] = round(dfz['Avg'] * 1000).apply(lambda x: "{:.0f} usd".format((x)))
            dfz['Avg'] = dfz['Avg'].apply(lambda x: "{:.2f} cents".format((x)))
            dfz['APD'] = dfz['APD'].apply(lambda x: "{:.2f} cents".format((x)))

        elif d == 'ng':
            dfz['PPC'] = round(dfz['Avg'] * 10000).apply(lambda x: "{:.0f} usd".format((x)))
            dfz['Avg'] = dfz['Avg'].apply(lambda x: "{:.2f} cents".format((x)))
            dfz['APD'] = dfz['APD'].apply(lambda x: "{:.2f} cents".format((x)))

        elif d == 'zn':
            dfz['PPC'] = round((dfz['Avg']) * 1000).apply(lambda x: "{:.0f} usd".format((x)))
            dfz['Avg'] = dfz['Avg'].apply(lambda x: "{:.2f} usd".format((x)))
            dfz['APD'] = dfz['APD'].apply(lambda x: "{:.2f} usd".format((x)))

        elif d == 'es':
            dfz['PPC'] = round((dfz['Avg']) * 50).apply(lambda x: "{:.0f} usd".format((x)))
            dfz['Avg'] = dfz['Avg'].apply(lambda x: "{:.2f} usd".format((x)))
            dfz['APD'] = dfz['APD'].apply(lambda x: "{:.2f} usd".format((x)))

        return dfz
