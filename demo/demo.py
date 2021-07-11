import os
import stocklab
import stocklab_demo

config_file = __file__.replace('demo.py', 'config.yml')
stocklab.configure(config_file)

print(stocklab.eval('Price.stock:acme.target_date:20201201'))
