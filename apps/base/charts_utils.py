import plotly.graph_objects as go
from plotly.subplots import make_subplots

import pandas as pd
import time
import datetime
import squarify
import matplotlib
import matplotlib.cm
from matplotlib.colors import LinearSegmentedColormap


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
                                "height":250
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
                                #"autosize":True,
                                "yaxis":{"title":"Negative VS Positive"},
                                "margin":{"l":0,"r":0,"t":0,"b":0},
                                "xaxis_tickangle":-45,
                                "xaxis_nticks":40,
                                "barmode":"stack",
                                "bargroupgap":0,
                                #"height":400,

}

general_chart_layout = {
                                "paper_bgcolor" : "rgba(0,0,0,0)",
                                "plot_bgcolor" : "rgba(0,0,0,0)",
                                "xaxis":{"title":"Dates"}, 
                                "yaxis":{"title":"Values"},
                                "autosize":True
                                }
trend_chart_layout = {
                                "paper_bgcolor" : "rgba(0,0,0,0)",
                                "plot_bgcolor" : "rgba(0,0,0,0)",
                                "autosize":True,
                                "margin":{"t":10,"b":0,"l":0,"r":0}
}


charts_layouts = {
    "Portfolio Value":portfolio_value_chart_layout,
    "Pie Chart" : pie_chart_layout,
    "Bar Chart" : bar_chart_layout,
    "Sentiment": sentiment_chart_layout,
    "General":general_chart_layout,
    "Trend Chart":trend_chart_layout
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
    def __init__(self, chart_name, multiple_axes=False):
        self.chart_name=chart_name
        if multiple_axes:
            self.fig = make_subplots(specs=[[{"secondary_y":True}]])
        else:
            self.fig = go.Figure()
        chart_layout = charts_layouts.get(self.chart_name, {})
        self.fig.update_layout(chart_layout)
    
    def draw_portfolio_value(self, df, name):
        if name == "Portfolio Value":
            hover_dict = {}
            for idx, row in df.iterrows():
                p = row[[c for c in row.index.values if c not in ["date"]]]
                p.sort_values(ascending=False, inplace=True, key=abs)
                hover_dict.update({row["date"]: p.head(6).to_dict()})
            text = ["<br>".join([f"<i>{k2}: {(v2*100):.2f}%</i>" if k2 !="prt_value" else f"<b>Portfolio Value: {v2:,.0f}$<b><br>" for k2,v2 in v.items()]) for k,v in hover_dict.items()]
        else:
            text = [f"{name}"]
        
        self.fig.add_trace(go.Scatter(mode="lines",x=df["date"], y=df["prt_value"], name='', text = text, hovertemplate="<b>%{text}</b>"))

        
    def draw_df(self, df, name, x_name, y_name):
        self.fig.add_trace(go.Scatter(mode="lines",x=df[x_name], y=df[y_name], name=name))
    def draw_no_data(self):
         self.fig.add_trace(go.Scatter(mode="lines",x=[1, 2, 3, 4, 5, 6 ], y=[1, 1, 1, 1, 1, 1]))

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
                            mean_trend=False,
                            price_graph=[]):
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
        new_df['pos_perc'] = round(new_df.transformers_pos_count_title/(new_df.transformers_neg_count_title+new_df.transformers_pos_count_title),4)
        new_df['neg_perc'] = round(new_df.transformers_neg_count_title/(new_df.transformers_neg_count_title+new_df.transformers_pos_count_title),4)


        if type(df) != list:
            if chart_type == 'bar':
                # Add bars
                self.fig.add_trace(go.Bar(
                                    x=new_df.index,
                                    y=new_df.pos_perc,
                                    name='Positive',
                                    marker_color='#00b276',
                                    #offset=0,
                                    customdata=new_df.transformers_pos_count_title,
                                    hovertemplate="%{y}, count: %{customdata}",
                                    width=bin_size.total_seconds() * 1000 *0.8, #*1000*3600*24,
                                    # edgecolor='black'
                                    # xperiod="D" + str(nbins),
                                    marker_line_color='black' #, marker_line_width=5
                                    ),
                                    secondary_y=False)
                self.fig.add_trace(go.Bar(
                                    x=new_df.index,
                                    y=new_df.neg_perc,
                                    name='Negative',
                                    marker_color='#e53935',
                                    #offset=0,
                                    width=bin_size.total_seconds() * 1000 *0.8, #*1000*3600*24,
                                    customdata=new_df.transformers_neg_count_title,
                                    hovertemplate="%{y}, count: %{customdata}",
                                    # edgecolor='black'
                                    # xperiod="D" + str(nbins),
                                    marker_line_color='black' #, marker_line_width=5
                                    ),
                                    secondary_y=False)
            elif chart_type == 'area':
                new_df.dropna(inplace=True)
                new_df['date'] = new_df.index
                self.fig.add_trace(go.Scatter(
                                    x=new_df.date,
                                    y=new_df.pos_perc,
                                    name='Positive',
                                    customdata=new_df.transformers_pos_count_title,
                                    hovertemplate="%{y}, count: %{customdata}",
                                    mode='lines',
                                    fillcolor='#46b08c',
                                    line=dict(width=0.5,color='#00b276'),
                                    stackgroup='one',
                                    opacity=0
                                    ))
                self.fig.add_trace(go.Scatter(
                                    x=new_df.date,
                                    y=new_df.neg_perc,
                                    name='Negative',
                                    customdata=new_df.transformers_neg_count_title,
                                    hovertemplate="%{y}, count: %{customdata}",
                                    mode='lines',
                                    fillcolor='#e64b47',
                                    line=dict(width=0.5,color='#e53935'),
                                    stackgroup='one',
                                    opacity=0
                                    ))
                self.fig.update_layout(hovermode="x unified")
            
            if mean_trend:
                self.fig.add_trace(go.Scatter(x=[new_df.index.min(),df.index.max()], 
                                                y=[new_df.pos_perc.mean(),new_df.pos_perc.mean()],
                                                mode='lines',
                                                marker_color='black',
                                                name='Mean trend'),
                                    secondary_y=False)

            if len(price_graph) != 0:
                self.fig.add_trace(go.Scatter(x=price_graph.index, 
                                                y=price_graph.close,
                                                mode='lines',
                                                marker_color='black',
                                                name='Close Price'),
                                    secondary_y=True)

        self.fig.update_layout(legend=dict(
                                    yanchor="top",
                                    y=0.6,
                                    xanchor="right",
                                    x=1.12),
                                xaxis_range=[df.index.min(),df.index.max()+bin_size],
                                yaxis=dict(tickformat='.0%'))

    def getTrendMap(self, df, labels_column, size_column, colors_column):

        values = df[size_column].to_list()
        labels = [x.upper() for x in df[labels_column].to_list()]

        norm = matplotlib.colors.Normalize(vmin=-1,vmax=1)

        cmap=LinearSegmentedColormap.from_list('rg',["r", "w", "g"], N=256)

        colors = [matplotlib.colors.to_hex(cmap(norm(x))) for x in df[colors_column]]

        x = 0
        y = 0
        width = 100
        height = 100

        normed = squarify.normalize_sizes(values, width, height)
        rects = squarify.squarify(normed, x, y, width, height)

        shapes = []
        annotations = []

        for r, color, text in zip(rects, colors, labels):
            shapes.append( 
                dict(
                    type = 'rect', 
                    x0 = r['x'], 
                    y0 = r['y'], 
                    x1 = r['x']+r['dx'], 
                    y1 = r['y']+r['dy'],
                    line = dict( width = 2, color = '#ffffff' ),
                    fillcolor = color
                ) 
            )
            annotations.append(
                dict(
                    x = r['x']+(r['dx']/2),
                    y = r['y']+(r['dy']/2),
                    text = text.replace(' ','<br>'),
                    showarrow = False,
                    font=dict(
                        size=14,
                        color="#ffffff"
                        )
                )
            )
        
        self.fig.add_trace(go.Scatter(
                    x = [ r['x']+(r['dx']/2) for r in rects ], 
                    y = [ r['y']+(r['dy']/2) for r in rects ],
                    text = labels, 
                    mode = 'text'
                    # textfont = dict(color="#ffffff", size=14)
                )
            )
        # self.fig.add_annotation(annotations)      
        self.fig.update_layout(
            autosize=True,
            xaxis={'showgrid':False, 'zeroline':False, 'showticklabels': False},
            yaxis={'showgrid':False, 'zeroline':False, 'showticklabels': False},
            shapes=shapes,
            annotations=annotations,
            hovermode='closest',
            hoverdistance=-1
            
        )

        ## self.fig = go.FigureWidget(self.fig)
            
    def draw_simulation(self, df, name, color):
        self.fig.add_trace(go.Scatter(mode="lines",x=df.index.strftime("%Y/%m/%d"), y=df, name=name, line={"color":color}))

    def get_chart(self):
        return self.fig