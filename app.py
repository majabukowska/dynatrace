from flask import Flask, request, jsonify
import requests
import logging
import datetime
import sys

app = Flask(__name__)

date = sys.argv[1]
currency = sys.argv[2]
quotations = int(sys.argv[3])


@app.route('/')
def start():
    return 'start'


@app.route('/avg_rate', methods=['GET'])
def avg_currency_rate():

    date_format = '%Y-%m-%d'
    if date is None:
        raise Exception("Date is not set")
    else:
        try:
            datetime.datetime.strptime(date, date_format)
        except ValueError:
            print("Incorrect data format, should be YYYY-MM-DD")

    if currency is None:
        raise Exception("Currency is not set")

    url = f'http://api.nbp.pl/api/exchangerates/rates/A/{currency}/{date}/'
    response = requests.get(url)

    if response.status_code != 200:
        logging.warning(f'Wrong status code - {response.status.code}')
    else:
        data = response.json()
        avg_currency_rate = data['rates'][0]['mid']
        return jsonify({'date': date, 'avg': avg_currency_rate})


@app.route('/min_max', methods=['GET'])
def get_min_max_avg():
    avg_daily = []
    if currency is None:
        raise Exception("Currency is not set")
    if quotations is None:
        raise Exception("Quotations are not set")

    url = f"http://api.nbp.pl/api/exchangerates/rates/a/{currency}/last/{quotations}/?format=json"
    response = requests.get(url)
    data = response.json()['rates']

    for day in data:
        avg_daily.append({'date': day['effectiveDate'], 'avg': day['mid']})

    max_avg = avg_daily[0]
    min_avg = avg_daily[0]

    for daily_data in avg_daily:
        if daily_data['avg'] > max_avg['avg']:
            max_avg = daily_data
        if daily_data['avg'] < min_avg['avg']:
            min_avg = daily_data

    return jsonify({'max_avg_value': max_avg['avg'], 'max_avg_date': max_avg['date'],
                    'min_avg_value': min_avg['avg'], 'min_avg_date': min_avg['date']})


@app.route('/major_difference', methods=['GET'])
def get_major_diff():
    if currency is None:
        raise Exception("Currency is not set")
    if quotations is None:
        raise Exception("Quotations are not set")

    url = f"http://api.nbp.pl/api/exchangerates/rates/c/{currency}/last/{quotations}/?format=json"
    response = requests.get(url)
    data = response.json()['rates']

    major_diff = 0.0
    for day in data:
        if 'ask' in day and 'bid' in day:
            diff = abs(day['ask'] - day['bid'])
            if diff > major_diff:
                major_diff = diff

    return jsonify({'major_difference': major_diff})


if __name__ == '__main__':
    app.run(debug=True)