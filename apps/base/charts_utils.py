import plotly.graph_objects as go
import pandas as pd
import time
import datetime

bars_colors = ["#413c69", "#4a47a3", "#709fb0", "#a7c5eb", "#c6ffc1"]
# pie_colors = ["#003f5c","#2f4b7c","#665191","#a05195","#d45087","#f95d6a","#ff7c43","#ffa600"]
# pie_colors = ["#00876c","#6da576","#b0c28b","#ede0ae","#e6b177","#e07c57","#d43d51"]
pie_colors = ["#00876c","#51a676","#88c580","#c2e38c","#ffff9d","#fdd172","#f7a258","#ea714e","#d43d51"]

portfolio_value_chart_layout = {
                                "paper_bgcolor" : "rgba(0,0,0,0)",
                                "plot_bgcolor" : "rgba(0,0,0,0)",
                                "xaxis":{"title":"Dates"}, 
                                "yaxis":{"title":"Portfolio Value"},
                                "autosize":True
                                }

pie_chart_layout = {
                                "paper_bgcolor" : "rgba(0,0,0,0)",
                                "plot_bgcolor" : "rgba(0,0,0,0)",
                                "autosize":True,
                                "showlegend":False,
                                "margin":{"l":0,"r":0,"t":0,"b":0}, 
                                
                                }         

bar_chart_layout = {
                                "paper_bgcolor" : "rgba(0,0,0,0)",
                                "plot_bgcolor" : "rgba(0,0,0,0)",
                                "autosize":True,
                                "showlegend":False,
                                "margin":{"l":0,"r":0,"t":0,"b":0}, 
                                # "xaxis":{'categoryorder':'total descending'}
                                }                                                           
sentiment_chart_layout = {
                                "paper_bgcolor" : "rgba(0,0,0,0)",
                                "plot_bgcolor" : "rgba(0,0,0,0)",
                                "autosize":True,
                                "yaxis":{"title":"Negative VS Positive"},
                                "margin":{"l":0,"r":0,"t":0,"b":0},
                                "xaxis_tickangle":-45,
                                "xaxis_nticks":40,
                                "barmode":"stack",
                                "bargroupgap":0

}

general_chart_layout = {
                                "paper_bgcolor" : "rgba(0,0,0,0)",
                                "plot_bgcolor" : "rgba(0,0,0,0)",
                                "xaxis":{"title":"Dates"}, 
                                "yaxis":{"title":"Values"},
                                "autosize":True
                                }


charts_layouts = {
    "Portfolio Value":portfolio_value_chart_layout,
    "Pie Chart" : pie_chart_layout,
    "Bar Chart" : bar_chart_layout,
    "Sentiment": sentiment_chart_layout,
    "General":general_chart_layout
}


def init_chart():
    df=pd.DataFrame({"date":[1,2,3,4,5], "prt_value":[1,2,3,4,5]})
    fig = go.Figure()
    fig.add_trace(go.Scatter(mode="lines", x=df["date"], y=df["prt_value"]))
    

    fig.update_layout(
        portfolio_value_chart_layout
    )

    return fig



class Chart():
    def __init__(self, chart_name):
        self.chart_name=chart_name
        self.fig = go.Figure()
        chart_layout = charts_layouts.get(self.chart_name, {})
        self.fig.update_layout(chart_layout)
    
    def draw_portfolio_value(self, df, name):
        self.fig.add_trace(go.Scatter(mode="lines",x=df["date"], y=df["prt_value"], name=name))
        
    def draw_df(self, df, name, x_name, y_name):
        self.fig.add_trace(go.Scatter(mode="lines",x=df[x_name], y=df[y_name], name=name))

    def draw_pie_chart(self, df, title=None):
        self.fig.add_trace(go.Pie(labels=df.index, values=df.values,textinfo='label',
    textposition='inside', title=title, hole=0.3,marker=dict(colors=pie_colors)))

    def draw_bars_chart(self, df, title=None):
        if "cash" in df.index:
            idx = df.index.tolist().index("cash")
            bars_colors[idx] = "#4aa96c"
        self.fig.add_trace(go.Bar(x=df.index, y=df.values, marker_color=bars_colors))
    
    def draw_sentiment_chart(self,df,title=None,
                            chart_type='bar',
                            dates=None,
                            mean_trend=False):
        nbins = 60
        
        if dates != None:
            d1 = datetime.datetime.strptime(dates[0].split(' ')[0], '%Y-%m-%d')
            d2 = datetime.datetime.strptime(dates[1].split(' ')[0], '%Y-%m-%d')
            print(d2 - d1)
            #print(f'Condition: {(d2 - d1) > datetime.timedelta(days=nbins)}')
            if (d2 - d1) > datetime.timedelta(days=nbins):
                df = df.loc[dates[0]:dates[1]]
            else:
                df = df.loc[(d2 - datetime.timedelta(days=nbins)):d2]

        if type(df) != list:
            if chart_type == 'bar':
                # Splitting data into bins
                bin_size = ((df.index.max() - df.index.min())/nbins).round('d')
                # print(bin_size)
                # DF that holds new df counts 
                new_df = pd.DataFrame()
                for i in range(nbins):
                    total = df.loc[(df.index.min()+bin_size*i):min(df.index.min() + bin_size*(i+1),df.index.max()),['transformers_pos_count_title','transformers_neg_count_title']].sum()
                    if new_df.empty:
                        new_df = pd.DataFrame(total,columns=[min(df.index.min() + bin_size*(i+1),df.index.max()).strftime('%Y-%m-%d')]).T
                    else:
                        new_df = pd.concat([new_df,pd.DataFrame(total,columns=[(df.index.min() + bin_size*(i+1)).strftime('%Y-%m-%d')]).T])

                # Calculate percentages
                new_df['pos_perc'] = round(new_df.transformers_pos_count_title/(new_df.transformers_neg_count_title+new_df.transformers_pos_count_title),2)
                new_df['neg_perc'] = round(new_df.transformers_neg_count_title/(new_df.transformers_neg_count_title+new_df.transformers_pos_count_title),2)

                # Add bars
                self.fig.add_trace(go.Bar(
                                    x=new_df.index,
                                    y=new_df.neg_perc,
                                    name='Negative',
                                    marker_color='#e53935',
                                    #offset=0,
                                    width=bin_size.total_seconds() * 1000 *0.8, #*1000*3600*24,
                                    # edgecolor='black'
                                    # xperiod="D" + str(nbins),
                                    marker_line_color='black' #, marker_line_width=5
                                    ))
                self.fig.add_trace(go.Bar(
                                    x=new_df.index,
                                    y=new_df.pos_perc,
                                    name='Positive',
                                    marker_color='#00b276',
                                    #offset=0,
                                    
                                    width=bin_size.total_seconds() * 1000 *0.8, #*1000*3600*24,
                                    # edgecolor='black'
                                    # xperiod="D" + str(nbins),
                                    marker_line_color='black' #, marker_line_width=5
                                    ))

                if mean_trend:
                    self.fig.add_trace(go.Scatter(x=[new_df.index.min(),df.index.max()], 
                                                    y=[new_df.neg_perc.mean(),new_df.neg_perc.mean()],
                                                    mode='lines',
                                                    marker_color='black',
                                                    name='Mean trend'))

        self.fig.update_layout(legend=dict(
                    yanchor="top",
                    y=0.6,
                    xanchor="right",
                    x=1.12
                ))

    def get_chart(self):
        return self.fig
