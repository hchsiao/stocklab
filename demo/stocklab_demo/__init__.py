import stocklab
stocklab.configure("config.yml")
stocklab.bundle(__file__)

# Debug
print(stocklab.eval('Date.target_date:5.n:6.phase_shift:lag'))
