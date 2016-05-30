# Imports
from flask import Flask, render_template, request, redirect, url_for
from pandas import DataFrame, to_datetime
import pandas
import numpy as np
import json
import requests
import time
from datetime import datetime,timedelta
from bokeh.plotting import figure, output_file, show
from bokeh import embed
import cgi

app = Flask(__name__)

selector = {}

@app.route('/')
def main():
  return redirect('/index')

@app.route('/index', methods=['GET','POST'])
def index():
  return render_template('index.html')

def make_plot():
	# get list of the checked features
	features = request.form.getlist('feature')
	
	# capture the ticker input from the user
	ticker = request.form['ticker']

	# calculate one month time period from now
	now = datetime.now()
	end_date = now.strftime('%Y-%m-%d') 
	start_date = (now - timedelta(days=30)).strftime('%Y-%m-%d')

	# fetch the appropriate dataset via API
	URL = 'https://www.quandl.com/api/v3/datasets/WIKI/'+ticker+'.json?start_date='+start_date+'&end_date='+end_date+'&order=asc&api_key=eFoXAcyvLhyuB3Rsvg6o'
	# URL = 'https://www.quandl.com/api/v3/datasets/WIKI/'+ticker+'.json?start_date=2015-08-01&end_date=2015-09-01&order=asc&api_key=eFoXAcyvLhyuB3Rsvg6o'
	r = requests.get(URL)

	# convert into a pandas dataframe
	request_df = DataFrame(r.json()) 
	df = DataFrame(request_df.ix['data','dataset'], columns = request_df.ix['column_names','dataset'])
	df.columns = [x.lower() for x in df.columns]
	df = df.set_index(['date'])
	df.index = to_datetime(df.index)

	# create a Bokeh plot from the dataframe
	# output_file("stock.html", title="Stock prices changes for last month")
	p = figure(x_axis_type = "datetime")
	if 'open' in features:
	    p.line(df.index, df['open'], color='blue', legend='opening price')
	if 'high' in features:
	    p.line(df.index, df['high'], color='red', legend='highest price')
	if 'close' in features:
	    p.line(df.index, df['close'], color='green', legend='closing price')
	return p
	

@app.route('/chart_page',methods=['GET','POST'])
def chart():
	plot = make_plot()
	script, div = embed.components(plot)
	return render_template('bokeh.html', script=script, div=div)
	
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
 
	#app.run(debug=True)
