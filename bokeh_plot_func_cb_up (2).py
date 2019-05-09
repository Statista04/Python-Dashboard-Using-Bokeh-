# Bokeh plot function
def bokeh_plot(import_df):
    import pandas as pd
    import numpy as np
    from bokeh.plotting import figure, show
    from bokeh.layouts import layout, widgetbox, row, column, gridplot
    from bokeh.models import ColumnDataSource, HoverTool, BoxZoomTool, ResetTool, PanTool, CustomJS, PrintfTickFormatter,WheelZoomTool, SaveTool, LassoSelectTool, NumeralTickFormatter
    from bokeh.models.widgets import Slider, Select, TextInput, Div, Tabs, Panel, DataTable, DateFormatter, TableColumn, PreText, NumberFormatter,RangeSlider
    from bokeh.io import curdoc
    from functools import lru_cache
    from bokeh.transform import dodge
    from os.path import dirname, join
    from bokeh.core.properties import value

    #load plotting data here
    @lru_cache()
    def load_data():
        df=import_df
        df.dropna(how='all',axis=0)
        #Northest=['3229','3277','3276','3230','3259','All_Stores_NE']
        df.location_reference_id = df.location_reference_id.astype(str)
        #df['region'] = ['Northeast' if x in Northest else 'Midwest' for x in df['location_reference_id']]
        df['date']=pd.to_datetime(df['date'])
        df[['BOH_gt_Shelf_Capacity',
           'OTL_gt_Shelf_Capacity', 'Ideal_BOH_gt_Shelf_Capacity', 'BOH_lt_Ideal',
           'BOH_eq_Ideal', 'BOH_gt_Ideal', 'Demand_Fulfilled',  'Fill_Rate',
            'Backroom_OH', 'Total_OH',
           'Prop_OH_in_Backroom', 'Never_Q98_gt_POG', 'Never_Ideal_BOH_gt_POG',
           'Sometimes_OTL_Casepack_1_gt_POG', 'Always_OTL_Casepack_1_le_POG',
           'Non_POG']]=df[['BOH > Shelf Capacity',
           'OTL > Shelf Capacity', 'Ideal BOH > Shelf Capacity', 'BOH < Ideal',
           'BOH = Ideal', 'BOH > Ideal', 'Demand Fulfilled',  'Fill Rate',
       'Backroom_OH', 'Total OH',
           'Prop OH in Backroom', 'Never: Q98 > POG', 'Never: Ideal BOH > POG',
           'Sometimes: OTL+Casepack-1 > POG', 'Always: OTL+Casepack-1 <= POG',
           'Non-POG']]
        df['date_bar']=df['date']
        df['date_bar']=df['date_bar'].astype(str)
        return df

    #Filter data source for "All" stores OR data agrregation on DC level
    df_agg=load_data().groupby(['location_reference_id'],as_index=False).sum()
    source1 = ColumnDataSource(data=df_agg)
    sdate=min(load_data()['date'])
    edate=max(load_data()['date'])
    nodes=len(list(load_data().location_reference_id.unique()))
    days=len(list(load_data().date.unique()))
    policy="Prod"

    #list of dates for vbar charts
    x_range_list=list(load_data().date_bar.unique())
    #direct access to number of location_reference_idand region
    all_locations1=list(load_data().location_reference_id.unique())
    #agg_value=['All']
    #all location_reference_idfrom csv file along with an option for agg data "All"
    #all_locations=all_locations1+agg_value
    #all_regions = ['Northeast', 'Midwest']
    all_regions=list(load_data().region.unique())

    desc = Div(text="All locations", width=230)
    pre = Div(text="_", width=230)
    location = Select(title="Location", options=all_locations1, value="All_Stores_NE")
    region = Select(title="Region", options=all_regions, value="NE")

    text_input = TextInput(value="default", title="Search Location:")
    #full data set from load_data(df=df_import)
    source = ColumnDataSource(data=load_data())
    original_source = ColumnDataSource(data=load_data())

    #plotting starts........... here are total 8 graphs for each Metric.

    #Back room on hand
    hover = HoverTool(tooltips=[("Location", "@location_reference_id"),("Date", "@date_bar"), ("Backroom_OH", "@Backroom_OH{0,0.00}") ])
    TOOLS = [ hover, BoxZoomTool(), LassoSelectTool(), WheelZoomTool(), PanTool(),ResetTool(), SaveTool() ]
    p = figure(x_range=x_range_list, plot_width=1000,plot_height=525, title="Backroom On hand by store",  tools=TOOLS,
               toolbar_location='above', x_axis_label="Date",
        y_axis_label="Backroom OH")
    p.background_fill_color = "#e6e9ed"
    p.background_fill_alpha = 0.5
    p.vbar(x=dodge('date_bar', -0.25, range=p.x_range), top='Backroom_OH',hover_alpha=0.5, hover_line_color='black', width=0.8, source=source,
           color="#718dbf")
    p.xaxis.major_label_orientation = 1
    p.legend.border_line_width = 3
    p.legend.border_line_color = None
    p.legend.border_line_alpha = 0.5
    p.title.text_color = "olive"

    #inbound outbound
    hover_m = HoverTool(tooltips=[ ("Location", "@location_reference_id"),("Date", "@date_bar"), ("Inbound", "@Inbound{0,0.00}"),("Outbound", "@Outbound{0,0.00}")  ])
    TOOLS_m = [ hover_m, BoxZoomTool(), LassoSelectTool(), WheelZoomTool(), PanTool(), ResetTool(), SaveTool()]
    m = figure(plot_height=525, plot_width=1000,x_range=x_range_list,  title="Inbound/Outbound by store",tools=TOOLS_m,
               toolbar_location='above', x_axis_label="Date", y_axis_label="Units")
    m.background_fill_color = "#e6e9ed"
    m.background_fill_alpha = 0.5
    m.vbar(x=dodge('date_bar', -0.25, range=m.x_range), top='Inbound',hover_alpha=0.5, hover_line_color='black', width=0.4, source=source,
           color="#718dbf", legend=value("Inbound"))
    m.vbar(x=dodge('date_bar', 0.25, range=m.x_range), top='Outbound',hover_alpha=0.5, hover_line_color='black', width=0.4, source=source,
           color="#e84d60", legend=value("Outbound"))
    m.xaxis.major_label_orientation = 1
    m.legend.border_line_width = 3
    m.legend.border_line_color = None
    m.legend.border_line_alpha = 0.5
    m.title.text_color = "olive"

    #Stockout
    hover_s = HoverTool(tooltips=[ ("Location", "@location_reference_id"),("Date", "@date_bar"), ("BOH_OOS", "@BOH_OOS{0,0.000}"),("EOH_OOS", "@EOH_OOS{0,0.000}")])
    TOOLS_s = [ hover_s, BoxZoomTool(), LassoSelectTool(), WheelZoomTool(), PanTool(), ResetTool(), SaveTool() ]
    s = figure( plot_height=525, plot_width=1000, title="Stockouts by store", x_axis_type="datetime",
               toolbar_location='above', tools=TOOLS_s,  x_axis_label="Date",y_axis_label="Prop Stockout")
    s.background_fill_color = "#e6e9ed"
    s.background_fill_alpha = 0.5
    s.circle(x='date', y='EOH_OOS', source=source, fill_color=None, line_color="#4375c6")
    s.line(x='date', y='EOH_OOS', source=source, hover_alpha=0.5, hover_line_color='black', line_width=2, line_color='navy',legend=value("EOH OOS"))
    s.circle(x='date', y='BOH_OOS', source=source, fill_color=None, line_color="#4375c6")
    s.line(x='date', y='BOH_OOS', source=source, hover_alpha=0.5, hover_line_color='black', line_width=2, line_color='red',legend=value("BOH OOS"))
    s.legend.border_line_width = 3
    s.legend.border_line_color = None
    s.legend.border_line_alpha = 0.5
    s.title.text_color = "olive"

    #Fill rate
    hover_t = HoverTool(tooltips=[ ("Location", "@location_reference_id"),("Date", "@date_bar"), ("Fill Rate", "@Fill_Rate{0,0.00}")])
    TOOLS_t = [ hover_t, BoxZoomTool(), LassoSelectTool(), WheelZoomTool(), PanTool(), ResetTool(), SaveTool() ]
    t = figure(plot_height=525, x_range=x_range_list,plot_width=1000, title="Fill rates by store",  tools=TOOLS_t,
               toolbar_location='above', x_axis_label="Date",y_axis_label="Fill rate")
    t.background_fill_color = "#e6e9ed"
    t.background_fill_alpha = 0.5
    t.vbar(x=dodge('date_bar', -0.25, range=t.x_range), top='Fill Rate',hover_alpha=0.5, hover_line_color='black', width=0.8, source=source,
           color="#718dbf")
    t.xaxis.major_label_orientation = 1
    t.legend.border_line_width = 3
    t.legend.border_line_color = None
    t.legend.border_line_alpha = 0.5
    t.title.text_color = "olive"

    # % Backroom spillover
    hover_w = HoverTool(tooltips=[ ("Location", "@location_reference_id"),("Date", "@date_bar"), ("Prop OH in Backroom", "@Prop_OH_in_Backroom{0,0.00}") ])
    TOOLS_w = [ hover_w, BoxZoomTool(), LassoSelectTool(), WheelZoomTool(), PanTool(),ResetTool(), SaveTool() ]
    w = figure(plot_height=525, plot_width=1000, title="Prop OH in Backroom by store", x_axis_type="datetime", tools=TOOLS_w,
               toolbar_location='above', x_axis_label="Date", y_axis_label=" % Backroom spillover")
    w.background_fill_color = "#e6e9ed"
    w.background_fill_alpha = 0.5
    w.circle(x='date', y='Prop OH in Backroom', source=source, fill_color=None, line_color="#4375c6")
    w.line(x='date', y='Prop OH in Backroom', source=source, hover_alpha=0.5, hover_line_color='black', line_width=2, line_color='navy')
    w.title.text_font_style = "bold"
    w.title.text_color = "olive"
    w.legend.click_policy="hide"
    w.yaxis[0].formatter = NumeralTickFormatter(format="0.0%")

    #BOH vs Ideal
    hover_f = HoverTool(tooltips=[ ("Location", "@location_reference_id"),("Date", "@date_bar"), ('BOH < Ideal', "@BOH_lt_Ideal{0,0.00}")
    ,('BOH > Ideal', "@BOH_gt_Ideal{0,0.00}"),('BOH = Ideal', "@BOH_eq_Ideal{0,0.00}")  ])
    TOOLS_f = [ hover_f, BoxZoomTool(), LassoSelectTool(), WheelZoomTool(), PanTool(),ResetTool(), SaveTool() ]
    colors = ["#c9d9d3", "#718dbf", "#e84d60"]
    BOH_vs_ideal=['BOH < Ideal','BOH > Ideal','BOH = Ideal']
    f = figure(x_range=x_range_list, plot_height=525, plot_width=1000, title="BOH vs Ideal by store",
               toolbar_location='above', x_axis_label="Date", y_axis_label="Prop", tools=TOOLS_f)
    f.vbar_stack(BOH_vs_ideal, x='date_bar', width=0.9, color=colors, source=source,legend=[value(x) for x in BOH_vs_ideal], name=BOH_vs_ideal)
    f.xaxis.major_label_orientation = 1
    f.legend.border_line_width = 3
    f.legend.border_line_color = None
    f.legend.border_line_alpha = 0.5
    f.title.text_color = "olive"

    #Pog Fit
    hover_g = HoverTool(tooltips=[ ("Location", "@location_reference_id"),("Date", "@date_bar"), ('Never: Q98 > POG', "@Never_Q98_gt_POG{0,0.00}")
    ,("Never: Ideal BOH > POG", "@Never_Ideal_BOH_gt_POG{0,0.00}"),("Sometimes: OTL+Casepack-1 > POG", "@Sometimes_OTL_Casepack_1_gt_POG{0,0.00}")
    ,("Always: OTL+Casepack-1 <= POG", "@Always_OTL_Casepack_1_le_POG{0,0.00}"),("Non-POG'", "@Non_POG{0,0.00}") ])
    TOOLS_g = [ hover_g, BoxZoomTool(), LassoSelectTool(), WheelZoomTool(), PanTool(),ResetTool(), SaveTool() ]
    colors2 = ['#79D151', "#718dbf", '#29788E','#fc8d59', '#d53e4f']
    pog_fit=['Never: Q98 > POG','Never: Ideal BOH > POG','Sometimes: OTL+Casepack-1 > POG','Always: OTL+Casepack-1 <= POG','Non-POG']
    g = figure(x_range=x_range_list, plot_height=525, plot_width=1200, title="Pog Fit by store",
               toolbar_location='above', x_axis_label="Date", y_axis_label="Counts",tools=TOOLS_g)
    g.vbar_stack(pog_fit, x='date_bar', width=0.9, color=colors2, source=source, legend=[value(x) for x in pog_fit], name=pog_fit)
    g.xaxis.major_label_orientation = 1
    g.legend.border_line_width = 3
    g.legend.border_line_color = None
    g.legend.border_line_alpha = 0.5
    g.title.text_color = "olive"
    g.legend.location = "top_right"

    # BOH vs Pog
    colors3 = ["#c9d9d3", "#718dbf", "#e84d60"]
    shelf=['BOH > Shelf Capacity', 'OTL > Shelf Capacity', 'Ideal BOH > Shelf Capacity']
    hover_h = HoverTool(tooltips=[ ("Location", "@location_reference_id"),("Date", "@date_bar"), ("OTL > Shelf Capacity", "@OTL_gt_Shelf_Capacity{0,0.00}")
    ,("BOH > Shelf Capacity", "@BOH_gt_Shelf_Capacity{0,0.00}"),("Ideal BOH > Shelf Capacity", "@Ideal_BOH_gt_Shelf_Capacity{0,0.00}")])
    TOOLS_h = [ hover_h, BoxZoomTool(), LassoSelectTool(), WheelZoomTool(), PanTool(), ResetTool(), SaveTool() ]
    h = figure( plot_height=525, plot_width=1000, title="BOH vs Pog by store", x_axis_type="datetime",
               toolbar_location='above', tools=TOOLS_h,  x_axis_label="Date", y_axis_label="Prop")
    h.background_fill_color = "#e6e9ed"
    h.background_fill_alpha = 0.5
    h.circle(x='date', y='BOH > Shelf Capacity', source=source, fill_color=None, line_color="#4375c6")
    h.line(x='date', y='BOH > Shelf Capacity', source=source, hover_alpha=0.5, hover_line_color='black', line_width=2, line_color='navy',
           legend=value("BOH > Shelf Capacity"))
    h.circle(x='date', y='OTL > Shelf Capacity', source=source, fill_color=None, line_color="#4375c6")
    h.line(x='date', y='OTL > Shelf Capacity', source=source, hover_alpha=0.5, hover_line_color='black', line_width=2, line_color="green",
           legend=value("OTL > Shelf Capacity"))
    h.circle(x='date',y='Ideal BOH > Shelf Capacity',  source=source, fill_color=None, line_color="#4375c6")
    h.line(x='date', y='Ideal BOH > Shelf Capacity', source=source, hover_alpha=0.5, hover_line_color='black', line_width=2, line_color="#e84d60",
           legend=value("Ideal BOH > Shelf Capacity"))
    h.legend.border_line_width = 3
    h.legend.border_line_color = None
    h.legend.border_line_alpha = 0.5
    h.title.text_color = "olive"
    h.legend.click_policy="mute"

    # Inventory
    hover_j = HoverTool(tooltips=[ ("Location", "@location_reference_id"),("Date", "@date_bar"), ("DFE_Q98", "@DFE_Q98{0,0.00}")
    ,("OTL", "@OTL{0,0.00}"),("EOH", "@EOH{0,0.00}"),("BOH", "@BOH{0,0.00}") ])
    TOOLS_j = [ hover_j, BoxZoomTool(), LassoSelectTool(), WheelZoomTool(), PanTool(), ResetTool(), SaveTool()]
    j = figure(plot_height=525, plot_width=1200,x_range=x_range_list,  title="Inbound/Outbound by store",tools=TOOLS_j,
               toolbar_location='above', x_axis_label="Date", y_axis_label="Units")
    j.background_fill_color = "#e6e9ed"
    j.background_fill_alpha = 0.5
    j.vbar(x=dodge('date_bar', -0.40, range=j.x_range), top='DFE_Q98',hover_alpha=0.3, hover_line_color='black', width=0.2, source=source,
           color="#FBA40A", legend=value("DFE_Q98"))
    j.vbar(x=dodge('date_bar', -0.20, range=j.x_range), top='OTL',hover_alpha=0.3, hover_line_color='black', width=0.2, source=source,
           color="#4292c6", legend=value("OTL"))
    j.vbar(x=dodge('date_bar', 0.00, range=j.x_range), top='EOH',hover_alpha=0.3, hover_line_color='black', width=0.2, source=source,
           color='#a1dab4', legend=value("EOH"))
    j.vbar(x=dodge('date_bar', 0.20, range=j.x_range), top='BOH',hover_alpha=0.3, hover_line_color='black', width=0.2, source=source,
           color="#DC5039", legend=value("BOH"))
    j.xaxis.major_label_orientation = 1
    j.legend.border_line_width = 3
    j.legend.border_line_color = None
    j.legend.border_line_alpha = 0.5
    j.title.text_color = "olive"
    j.legend.location = "top_left"
    j.legend.click_policy="mute"


    #desc.text = " <br >  <b> Region:</b> <i>  </i> <br /> "
    pre.text = " <b>Start date:</b>  <i>{}</i> <br />  <b>End date:</b> <i>{}</i> <br /> <b>Time period:</b> <i>{}</i> days <br />  <b> Total Number of Nodes:</b> <i>{}</i> <br /> <b>Policy</b> = <i>{}</i><br /> ".format( sdate , edate , days,nodes,policy )


    #fuction to update data on selection
    callback = CustomJS(args=dict(source=source,original_source=original_source,location_select_obj=location,region_select_obj=region,div=desc,text_input=text_input), code="""
    var data = source.get('data');
    var original_data = original_source.get('data');
    var loc = location_select_obj.get('value');
    var reg = region_select_obj.get('value');
    var line = " <br />  <b> Region:</b>"+ reg + "<br />  <b>Location:</b> " +   loc;
    var text_input =text_input.get('value');
    div.text=line;
    for (var key in original_data) {
    data[key] = [];
    for (var i = 0; i < original_data['location_reference_id'].length; ++i) {
    if ((original_data['location_reference_id'][i] === loc) && (original_data['region'][i] === reg) ) {
    data[key].push(original_data[key][i]);
    }   }   }
    source.trigger('change');
    """)

    #controls = [location, region]
    #for control in controls:
        #control.js_on_change("value", callback)
    #source.js_on_change("value", callback)
    desc.js_on_event('event', callback)
    location.js_on_change('value', callback)
    region.js_on_change('value', callback)
    text_input.js_on_change('value', callback)
    #inputs = widgetbox(*controls, sizing_mode="fixed")
    #inputs = widgetbox(*controls,width=220,height=500)
    inputs = widgetbox(location,region,desc,pre,width=220,height=500)
    # controls number of tabs
    tab1 = Panel(child=p, title='Backroom OH')
    tab2 = Panel(child=s, title='Stockouts')
    tab3 = Panel(child=f, title='BOH vs Ideal')
    tab4 = Panel(child=g, title='Pog Fit')
    tab5 = Panel(child=m, title='Inbound/Outbound')
    tab6 = Panel(child=h, title='BOH vs POG')
    tab7 = Panel(child=t, title='Fill Rate')
    tab8 = Panel(child=j, title='Inventory')
    tab9 = Panel(child=w, title='Prop OH in Backroom')

    #data table columns to summarize data
    columns = [
        TableColumn(field="location_reference_id", title="Location"),
        TableColumn(field="Backroom_OH", title="Backroom_OH", formatter=NumberFormatter(format="0,0")),
        TableColumn(field="Outbound", title="Outbound", formatter=NumberFormatter(format="0,0")),
        TableColumn(field="Inbound", title="Inbound", formatter=NumberFormatter(format="0,0")),
        TableColumn(field="OTL", title="OTL", formatter=NumberFormatter(format="0,0")),
        TableColumn(field="DFE_Q98", title="DFE_Q98", formatter=NumberFormatter(format="0,0")),
        TableColumn(field="BOH", title="BOH", formatter=NumberFormatter(format="0,0")),
        TableColumn(field="EOH", title="EOH", formatter=NumberFormatter(format="0,0")),
        TableColumn(field="BOH_OOS", title="BOH_OOS", formatter=NumberFormatter(format="0,0")),
        TableColumn(field="EOH_OOS", title="EOH_OOS", formatter=NumberFormatter(format="0,0"))
              ]
    data_table = DataTable(source=source1, columns=columns, width=1250)

    tab10 = Panel(child=data_table, title='Summary Table')
    view=Tabs(tabs=[tab1, tab2, tab5,tab8, tab6 , tab3,tab7, tab4,tab9,tab10])

    layout_text=column(inputs)
    layout1 = row( layout_text,view)
    #laying out plot
    layout2=layout(children=[[layout_text,view]],sizing_mode='scale_height')
    #update plots
    return layout2
