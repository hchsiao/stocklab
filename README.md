# stocklab
In tasks such as financial data analysis and manipulation,
data are usually retrieved from a very large base.
People used to collect all the potentially useful data first, and then perform the analysis logic.
However, the completeness of data at hand poses limits on the potential of the research.
At a personal pet project scale,
it is somewhat difficult to gather every possible piece of data
due to its amount, the awkward APIs, and the scattered nature of different information.
Stocklab is a framework to defer the data retrieval until the analysis logic needs it.

All of the data around the world are indexed as stocklab's `DataIdentifier`.
By using DataIdentifier as a surrogate of the real data handle,
one can assume that all of the data are virtually available at hand when programming the analysis logic.
The missing data will then be retrieved during the executing of the analysis logic.

## Usage
See [stocklab-twse](https://github.com/hchsiao/stocklab-twse).

## Specification
Conceptually, a data analysis system consists of the data and the analysis logic.
As mentioned, DataIdentifier is used as the access key to data.
Analysis logics are also represented with DataIdentifier in the sense that the results of analysis are also data.

### DataIdentifier

#### Design choices (TODO)
- A single underscore in the expression means dont-care, otherwise expressions cannot start/end with underscore
- TODO: is this really needed?

#### Expression (TODO)
Here's the BNF grammar of the expression of a `DataIdentifier`.
```
<data-identifier> ::= <data-identifier> <seperator1> <field> | <node-name>
<field>           ::= <field-name> <seperator2> <field-value>
<node-name>       ::= <node-name> <character2> | <character1>
<field-name>      ::= <field-name> <character2> | <character1>
<field-value>     ::= <field-value> <character2> | <character2>
<seperator1>      ::= "."
<seperator2>      ::= ":"
<character1>      ::= [a-zA-Z]
<character2>      ::= [a-zA-Z0-9_]
```

#### Nodes and Fields
From the definition, a DataIdentifier consists of exactly one node and zero or more fields.
Fields act like function arguments.
At the interface, nodes act like functions in functional programming:
evaluating a DataIdentifier is a mapping process from a field tuple to some constant.
The following is the example a DataIdentifier may be:
```
ClosePrice.stock:2330.date:20201201
```

The correct outcome of an evaluation of DataIdentifier should be a unique constant (pure function).
Hence, the following example is a violation of this intent:
```
ClosePrice.stock:2330.date:today
```

Even if we never implement impure evaluation deliberately,
it's hard to guarentee the pure function property since crawlers rely on side-effects to load data.
Another possible impureness is that, nodes are also responsible for database management.
If the during the evaluation a node detects that it may not be able to deliver the very constant (e.g. database temporarily unavailable),
an exception should be raised.

#### Alternative Syntax
For convinence, `ClosePrice.stock:2330.date:20201201` can also be written in Python as:
`DI('ClosePrice')(stock=2330, date=20201201)` after `from stocklab import DataIdentifier as DI`.
The Python syntax for a DataIdentifier will not made portable across languages.

## TODO
- fix bug: init before mid-night (00:00), bug appears after mid-night (such as update conditions checking)
