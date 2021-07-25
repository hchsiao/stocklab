from stocklab.crawler import Crawler, speed_limiter

class FooCrawler(Crawler):
    @speed_limiter(max_speed=1)
    def bar(date, stock_id):
        FooCrawler.logger.warn(f'Crawler started. Args: date={date}, stock_id={stock_id}')
        return [{
            'stock': stock_id,
            'date': date,
            'price': date + 123,
            'note': 'the data was given by FooCrawler'
            }]
