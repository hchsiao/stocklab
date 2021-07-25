# stocklab
In the financial data analysis tasks,
data are retrieved from a very large base.
We could collect all the potentially useful data first, and then perform the analysis logic.
However, the completeness of data at hand poses limits on the potential of the research.

At a personal pet project scale,
it is somewhat difficult to gather every possible piece of data
due to its amount, the awkward APIs, and the scattered nature of information from different sources.
Stocklab is a framework to defer the data retrieval until the analysis logic needs it.

All of the data accessable on the internet can be indexed as stocklab's `DataIdentifier`.
By using DataIdentifier as a proxy of the real data handle,
one can assume that all of the data are virtually available at hand when programming the analysis logic.
The missing data will then be retrieved during the executing of the analysis logic.
Crawlers and analysis logics can then be nicely decoupled.

## Usage
An (arguably) minimal example can be found [here](demo).
Run the entry point by:
```
python demo.py
```
If you run this twice, you'll see that the crawler logs only appear on the first run.
The second run will not trigger data retrival because the all data were available in the database.

This framework has been used to build another real-world application,
see [stocklab-twse](https://github.com/hchsiao/stocklab-twse) for a more practical demo.

## Configuration
| Name | Description |
|------|-------------|
| `config_name` | TODO: may be removed? |
| `force_offline` | `CrawlerTrigger` will not trigger crawler actions. |
| `root_dir` | Root path to all runtime generated files. |
| `log_level` | See [Logging Levels](https://docs.python.org/3/library/logging.html#levels). |
| `database` | See [Database configuration](#database-configuration). |

### Database configuration
TODO
```
database:
  type: sqlite
  filename: db.sqlite
```

## API documentation
See [this](https://hchsiao.github.io/stocklab/).

## Specification
Conceptually, a data analysis system consists of the data and the analysis logic.
As mentioned, DataIdentifier is used as the access key to data.
Analysis logics are also represented with DataIdentifier in the sense that the results of analysis are also data.

### DataIdentifier

#### Design choices (TODO)
- A single underscore in the expression means dont-care, otherwise expressions cannot start/end with underscore
- TODO: is this really needed?

#### Expression
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
```
from stocklab import DataIdentifier as DI
DI('ClosePrice')(stock=2330, date=20201201)
```

This syntax for a DataIdentifier will not made portable across languages.

## TODO
- Move non-generic features from the old full version to `stocklab-twse`
  - fix bug: init before mid-night (00:00), bug appears after mid-night (such as update conditions checking)
