# patterns_and_seasonality
This algorithm searches for price patterns with high percent hit rate in various commodities.

The idea is that seasonality plays very important role in commodities like crude oil, natural gas, wheat, corn, gold etc. This algorithm constructs the normalized seasonality based on the last 15,10 and 5 years. The reason in dividing it in 3 different periods is that commodities themselves go through fundamental changes and we want to see if there is also change in their seasonals.

The algorithm searches also for the best correlating contract throughout those 15 years. For example it could find that may futures contract of Crude Oil in 2022 (clk22) are best correlated with the may futures contracts in 2008 (clk08). This could suggest that there are some similarities in the fundamentals between the prices in 2022 and in 2008, which would helps us make hypothesis about the future movement of the prices.

The core idea of the code is to find price patterns with high percent hit rate, based on the last 15,10,5 years. For example it can find that in 14 out of 15 years, the prices of Wheat closed higher, beginning 1st of May until 15 of June with average profit per contract - $1500.

The main code is in the 'main' file. 
In 'miscellaneous' are the specifications for every contract, which are important for constructing the proper timeseries data. Also it pulls data from Interactive Brokers, for the most recent futures contract. 

In the end we have a dataframe with the values for the last 15,10,5 Years, the most recent contract and its best correlating contract. 
We also get the table with the price patterns with high percent hit rate for the specific commodity.
