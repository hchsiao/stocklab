import os
import stocklab
import stocklab_demo

config_file = __file__.replace('demo.py', 'config.yml')
stocklab.configure(config_file)

print(stocklab.eval('MovingAverage.stock:acme.date_idx:1000.window:5'))
