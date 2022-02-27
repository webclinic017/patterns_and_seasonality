# patterns_and_seasonality
This algorithm searches for price patterns with high percent hit rate in various commodities

The idea is that seasonality plays very important role in commodities like crude oil, natural gas, wheat, corn, gold etc. This algorithm constructs the normalized seasonality based on the last 15,10 and 5 years. The reason to divide it in 3 different periods is that commodity themselves go through fundamental changes and we want to see how different are the seasonals in the last 5 years in respect to the last 15 years. 

The algorithm searches also for the best correlating contract throughout those 15 years. For example it could find that may futures contract of Crude Oil in 2022 (clk22) are best correlated with the may futures contracts in 2008 (clk08). This could suggest that there are some similarities in the fundamentals between the prices in 2022 and in 2008, which in turn helps us make hypothesis about the future movement of the prices.

The core idea of the code is to find price patterns with high percent hit rate, based on the last 15,10,5 years. For example it can find that in 14 out of 15 years, the prices of Wheat closed higher, beginning 1st of May until 15 of June.
