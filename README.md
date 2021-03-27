# Stock-Recommender
### A project for the Web Information Retrieval and Data Mining Course


The project includes a web-scraper that retrieves data from News API (real-time news) and AlphaVantage (stock information), to create a public sentiment recognition system, that recommends to buy or sell stocks. 
Three components are addded, and a weightage is assigned to the recommendations from all of them.
The first component is the Sentiment Analysis system.
The second is the time-series library Prophet (created by Facebook).
The third is a mixed neural-network architecture with RNN layers.

Theoretically, an ensemble system such as this should become better with more training data, so we train it upon data and information from previous years.

(Built in collaboration with Abhishek Mahadevan Raju)