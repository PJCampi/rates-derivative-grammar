# Rates derivative grammar

## What is it?

This package defines an EBNF grammar for representing as string a range of interest rates derivatives (f.ex. swap, 
fras & swap strategies, along with swaptions, caps and cap strategies).
 
It also provides functions to:

 - parse string representations into a product type and a dictionary of attribute names to attribute values of 
 meaningful type (for example a date string is converted to a date):
```
from rates_derivative_grammar import AssetClassParser

parser = AssetClassParser()
parser.parse("5Y10Y 100mm")  # -> ("swap", {"start_time": "5Y", "end_time": "10Y", "size": 100_000_000})
```
 
 - format attribute dictionaries back to their string representation:
```
from rates_derivative_grammar import AssetClassFormatter

formatter = AssetClassFormatter()
format.format("swap", {"start_time": "5Y", "end_time": "10Y", "size": 100_000_000}) -> "5Y10Y 100mm"
```  

The grammar roughly follows informal lingo in the interbank market, though some characters are added to make 
the grammar a bit more explicit: for example b3s for swap ag. 3m instead of 3s. 

We provide a couple of examples here:
```
EUR 10Y -> swap, {currency: EUR, end_time: 10Y}
10mar20 P b3s 100mm -> swaption, {end_time: 10-mar-2020, contract_type: PAYER, float_freq: 3m, size: 100_000_000}
EUR 5s10s 10kr -> curve, {end_time:[5Y, 7Y], size: [10_000, true]} (notional is expressed in risk terms)
```
Check the grammar files (under grammar folder inside the package) and my unit tests for an exhaustive set of examples.

Note that the grammar is not completely bijective as "100.0mm" and "100m" both resolve to a float value of 100_000_000 
which is formatted back to "100mm".

## How to install?

I have created a package as an exercise to learn how to write a grammar. Given the very limited use case I did not bother 
publishing to pypi & doing CI/CD.