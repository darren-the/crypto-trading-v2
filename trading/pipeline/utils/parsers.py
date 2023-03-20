def parse_high_low_history(element):
    high_low_types = element['high_low_type_history'].split(',')
    high_low_timestamps = element['high_low_timestamp_history'].split(',')
    high_low_prices = element['high_low_price_history'].split(',')

    if len(high_low_types) != len(high_low_timestamps) != len(high_low_prices):
        raise Exception('Error: len(high_low_types) != len(high_low_timestamps) != len(high_low_prices)')

    history = []
    if len(high_low_types) > 0 and high_low_types[0] != '':
        for i in range(len(high_low_types)):
            history.append({
                'type': high_low_types[i],
                'timestamp': float(high_low_timestamps[i]),
                'price': float(high_low_prices[i]),
            })
    
    return history
