import plotly.graph_objects as go
import pandas as pd


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
sentiment_chart_layout = {
                                "paper_bgcolor" : "rgba(0,0,0,0)",
                                "plot_bgcolor" : "rgba(0,0,0,0)",
                                "autosize":True,
                                "yaxis":{"title":"Sentiment score"},
                                "margin":{"l":0,"r":0,"t":0,"b":0},

}


charts_layouts = {
    "Portfolio Value":portfolio_value_chart_layout,
    "Pie Chart" : pie_chart_layout,
    "Sentiment": sentiment_chart_layout
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
    textposition='inside', title=title))
    
    def draw_sentiment_chart(self,df,title=None):
        self.fig.add_trace(go.Scatter(
            x=df.index,
            y=df.transformers_score_title,
            marker=dict(
                size=4,
                cmax=10,
                cmin=0,
                color=df.num_news,
                colorbar=dict(
                    title="#News"
                ),
                colorscale="RdYlBu_r"
            ),
            mode="markers"
        ))

    def get_chart(self):
        return self.fig
