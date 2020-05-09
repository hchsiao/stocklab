# stocklab
This package does not work alone, extensions are required. Example of extesion: [stocklab-twse](https://github.com/hchsiao/stocklab-twse)

## TODO
- control no. of instance for class get_db to detect cases where 'OperationalError: database is locked' could occur

## Design choices
- stocklab expressions cannot contain curly-braces
- a single underscore in the expression means dont-care, otherwise expressions cannot start/end with underscore

## Known limitations
- When using the same sqlite file in both 'database' and 'cache' config, "OperationalError: database is locked" may ocurr
