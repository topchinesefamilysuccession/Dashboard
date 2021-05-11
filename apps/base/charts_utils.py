import plotly.graph_objects as go
import pandas as pd

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

charts_layouts = {
    "Portfolio Value":portfolio_value_chart_layout,
    "Pie Chart" : pie_chart_layout,
    "Bar Chart" : bar_chart_layout
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

    def draw_pie_chart(self, df, title=None):
        self.fig.add_trace(go.Pie(labels=df.index, values=df.values,textinfo='label',
    textposition='inside', title=title, hole=0.3,marker=dict(colors=pie_colors)))

    def draw_bars_chart(self, df, title=None):
        if "cash" in df.index:
            idx = df.index.tolist().index("cash")
            bars_colors[idx] = "#4aa96c"
        self.fig.add_trace(go.Bar(x=df.index, y=df.values, marker_color=bars_colors))

    def get_chart(self):
        return self.fig
