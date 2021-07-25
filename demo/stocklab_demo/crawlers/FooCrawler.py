from stocklab.crawler import Crawler, speed_limiter

class FooCrawler(Crawler):
    def bar(date, stock_id):
        FooCrawler.logger.info(f'Crawler started. Args: date={date}, stock_id={stock_id}')
        return [{
            'stock': stock_id,
            'date': date,
            'price': date + 123,
            'note': 'the data was given by FooCrawler'
            }]
