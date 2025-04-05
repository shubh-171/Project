import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go

app = dash.Dash(__name__)
server = app.server

df = pd.read_csv('data.csv')

for col in ['Total', 'Men', 'Women']:
    df[col] = df[col].astype(str).str.replace(',', '').astype(float)

df['Major Occupation'] = df['Occupation'].str.extract(r'^(\d)')[0]

occupation_mapping = {
    '0': '0 Legislative and senior management occupations',
    '1': '1 Business, finance and administration occupations',
    '2': '2 Natural and applied sciences and related occupations',
    '3': '3 Health occupations',
    '4': '4 Occupations in education, law and social, community and government services',
    '5': '5 Occupations in art, culture, recreation and sport',
    '6': '6 Sales and service occupations',
    '7': '7 Trades, transport and equipment operators and related occupations',
    '8': '8 Natural resources, agriculture and related production occupations',
    '9': '9 Occupations in manufacturing and utilities'
}

df['Major Occupation Name'] = df['Major Occupation'].map(occupation_mapping)

essential_services = {
    'Nurses': ['31301 Registered nurses and registered psychiatric nurses', 
               '32101 Licensed practical nurses',
               '31302 Nurse practitioners'],
    'Police': ['42100 Police officers (except commissioned)',
               '41310 Police investigators and other investigative occupations',
               '43201 Correctional service officers'],
    'Firefighters': ['42101 Firefighters']
}

engineers_data = {
    'Computer Engineers': ['21311 Computer engineers (except software engineers and designers)',
                          '2122 Computer and information systems professionals',
                          '2123 Computer, software and Web designers and developers'],
    'Mechanical Engineers': ['21301 Mechanical engineers',
                            '22301 Mechanical engineering technologists and technicians'],
    'Electrical Engineers': ['21310 Electrical and electronics engineers',
                            '22310 Electrical and electronics engineering technologists and technicians']
}

province_population = {
    'Alberta': 4648076,
    'British Columbia': 5343545,
    'Manitoba': 1431795,
    'New Brunswick': 825474,
    'Newfoundland and Labrador': 533710,
    'Northwest Territories': 45602,
    'Nova Scotia': 1037485,
    'Nunavut': 40220,
    'Ontario': 15398475,
    'Prince Edward Island': 173954,
    'Quebec': 8833635,
    'Saskatchewan': 1214618,
    'Yukon': 44412
}

def create_provincial_distribution(national_count):
    total_pop = sum(province_population.values())
    provincial_data = {province: (pop/total_pop) * national_count 
                      for province, pop in province_population.items()}
    return provincial_data

app.layout = html.Div([
    html.H1("Canadian Employment Statistics Dashboard", style={'textAlign': 'center'}),
    dcc.Tabs(id='tabs', value='tab-1', children=[
        dcc.Tab(label='Essential Services Distribution', value='tab-1'),
        dcc.Tab(label='Gender Employment Statistics', value='tab-2'),
        dcc.Tab(label='EV Factory Workforce', value='tab-3'),
        dcc.Tab(label='Additional Insights', value='tab-4'),
    ]),
    html.Div(id='tabs-content'),
    html.Div([
        html.P("Note: Provincial distributions are estimated based on population proportions.",
              style={'fontStyle': 'italic', 'color': 'gray'})
    ])
])

@app.callback(
    Output('tabs-content', 'children'),
    Input('tabs', 'value')
)
def render_content(tab):
    if tab == 'tab-1':
        return html.Div([
            html.H3("Distribution of Essential Services Across Provinces/Territories"),
            dcc.Dropdown(
                id='essential-service-dropdown',
                options=[
                    {'label': 'Nurses', 'value': 'Nurses'},
                    {'label': 'Police Officers', 'value': 'Police'},
                    {'label': 'Firefighters', 'value': 'Firefighters'}
                ],
                value='Nurses',
                style={'width': '50%', 'margin': '10px'}
            ),
            dcc.RadioItems(
                id='normalization-radio',
                options=[
                    {'label': 'Absolute Numbers', 'value': 'absolute'},
                    {'label': 'Per 100,000 Population', 'value': 'normalized'}
                ],
                value='absolute',
                style={'margin': '10px'}
            ),
            dcc.Graph(id='essential-services-map')
        ])
    elif tab == 'tab-2':
        return html.Div([
            html.H3("Gender Employment Statistics by Major Occupation Category"),
            dcc.Dropdown(
                id='province-dropdown',
                options=[{'label': prov, 'value': prov} for prov in province_population.keys()],
                value='Ontario',
                style={'width': '50%', 'margin': '10px'}
            ),
            dcc.RadioItems(
                id='gender-metric-radio',
                options=[
                    {'label': 'Total Employment', 'value': 'Total'},
                    {'label': 'Percentage Women', 'value': 'percent_women'},
                    {'label': 'Gender Ratio (Women:Men)', 'value': 'ratio'}
                ],
                value='Total',
                style={'margin': '10px'}
            ),
            dcc.Graph(id='gender-occupation-bar')
        ])
    elif tab == 'tab-3':
        return html.Div([
            html.H3("Workforce Availability for Electric Vehicle Factory Setup"),
            dcc.Dropdown(
                id='engineer-type-dropdown',
                options=[
                    {'label': 'Computer Engineers', 'value': 'Computer Engineers'},
                    {'label': 'Mechanical Engineers', 'value': 'Mechanical Engineers'},
                    {'label': 'Electrical Engineers', 'value': 'Electrical Engineers'},
                    {'label': 'All Engineering Types', 'value': 'All'}
                ],
                value='Computer Engineers',
                style={'width': '50%', 'margin': '10px'}
            ),
            dcc.RadioItems(
                id='engineer-normalization-radio',
                options=[
                    {'label': 'Absolute Numbers', 'value': 'absolute'},
                    {'label': 'Per 100,000 Population', 'value': 'normalized'}
                ],
                value='normalized',
                style={'margin': '10px'}
            ),
            dcc.Graph(id='engineer-map'),
            html.Div([
                html.H4("Top 5 Provinces/Territories by Workforce Availability"),
                html.Div(id='top-provinces-table')
            ])
        ])
    elif tab == 'tab-4':
        return html.Div([
            html.H3("Additional Insights: Gender Distribution Across Occupations"),
            dcc.Dropdown(
                id='occupation-category-dropdown',
                options=[{'label': name, 'value': code} for code, name in occupation_mapping.items()],
                value='2',
                style={'width': '50%', 'margin': '10px'}
            ),
            dcc.Graph(id='gender-distribution-sunburst')
        ])

@app.callback(
    Output('essential-services-map', 'figure'),
    [Input('essential-service-dropdown', 'value'),
     Input('normalization-radio', 'value')]
)
def update_essential_services_map(service_type, normalization):
    occupations = essential_services[service_type]
    service_df = df[df['Occupation'].isin(occupations)]
    total_workers = service_df['Total'].sum()
    provincial_data = create_provincial_distribution(total_workers)
    plot_df = pd.DataFrame({
        'Province': list(provincial_data.keys()),
        'Workers': list(provincial_data.values()),
        'Population': [province_population[prov] for prov in provincial_data.keys()]
    })
    if normalization == 'normalized':
        plot_df['Workers'] = (plot_df['Workers'] / plot_df['Population']) * 100000
        z_title = f"{service_type} per 100,000 population"
    else:
        z_title = f"Number of {service_type}"
    fig = px.choropleth(
        plot_df,
        locations='Province',
        locationmode='country names',
        scope='canada',
        color='Workers',
        hover_name='Province',
        hover_data={'Workers': ':.0f', 'Population': ':.0f'},
        color_continuous_scale='Viridis',
        title=f'Distribution of {service_type} Across Canada'
    )
    fig.update_layout(
        geo=dict(
            lakecolor='rgb(255, 255, 255)',
            landcolor='rgba(255, 255, 255, 0)',
            subunitcolor='grey'
        ),
        coloraxis_colorbar=dict(title=z_title),
        margin={"r":0,"t":40,"l":0,"b":0}
    )
    return fig

@app.callback(
    Output('gender-occupation-bar', 'figure'),
    [Input('province-dropdown', 'value'),
     Input('gender-metric-radio', 'value')]
)
def update_gender_occupation_chart(province, metric):
    grouped = df.groupby('Major Occupation Name').agg({'Total': 'sum', 'Men': 'sum', 'Women': 'sum'}).reset_index()
    grouped['percent_women'] = (grouped['Women'] / grouped['Total']) * 100
    grouped['ratio'] = grouped['Women'] / grouped['Men']
    national_pop = sum(province_population.values())
    province_ratio = province_population[province] / national_pop
    grouped['Total'] = grouped['Total'] * province_ratio
    grouped['Men'] = grouped['Men'] * province_ratio
    grouped['Women'] = grouped['Women'] * province_ratio
    if metric == 'Total':
        grouped = grouped.sort_values('Total', ascending=False)
        y_values = grouped['Total']
        y_title = 'Number of Workers'
        title = f'Total Employment by Major Occupation in {province}'
    elif metric == 'percent_women':
        grouped = grouped.sort_values('percent_women', ascending=False)
        y_values = grouped['percent_women']
        y_title = 'Percentage of Women (%)'
        title = f'Percentage of Women by Major Occupation in {province}'
    else:
        grouped = grouped.sort_values('ratio', ascending=False)
        y_values = grouped['ratio']
        y_title = 'Gender Ratio (Women:Men)'
        title = f'Gender Ratio by Major Occupation in {province}'
    fig = px.bar(
        grouped,
        x='Major Occupation Name',
        y=y_values,
        color='Major Occupation Name',
        labels={'Major Occupation Name': 'Occupation Category'},
        title=title
    )
    fig.update_layout(
        xaxis_title='Major Occupation Category',
        yaxis_title=y_title,
        showlegend=False
    )
    return fig

@app.callback(
    [Output('engineer-map', 'figure'),
     Output('top-provinces-table', 'children')],
    [Input('engineer-type-dropdown', 'value'),
     Input('engineer-normalization-radio', 'value')]
)
def update_engineer_map(engineer_type, normalization):
    if engineer_type == 'All':
        all_engineers = []
        for eng_type in engineers_data:
            all_engineers.extend(engineers_data[eng_type])
        occupations = all_engineers
        title = 'All Engineering Professionals'
    else:
        occupations = engineers_data[engineer_type]
        title = engineer_type
    engineer_df = df[df['Occupation'].isin(occupations)]
    total_workers = engineer_df['Total'].sum()
    provincial_data = create_provincial_distribution(total_workers)
    plot_df = pd.DataFrame({
        'Province': list(provincial_data.keys()),
        'Workers': list(provincial_data.values()),
        'Population': [province_population[prov] for prov in provincial_data.keys()]
    })
    if normalization == 'normalized':
        plot_df['Workers'] = (plot_df['Workers'] / plot_df['Population']) * 100000
        z_title = f"{title} per 100,000 population"
    else:
        z_title = f"Number of {title}"
    fig = px.choropleth(
        plot_df,
        locations='Province',
        locationmode='country names',
        scope='canada',
        color='Workers',
        hover_name='Province',
        hover_data={'Workers': ':.0f', 'Population': ':.0f'},
        color_continuous_scale='Plasma',
        title=f'Distribution of {title} Across Canada'
    )
    fig.update_layout(
        geo=dict(
            lakecolor='rgb(255, 255, 255)',
            landcolor='rgba(255, 255, 255, 0)',
            subunitcolor='grey'
        ),
        coloraxis_colorbar=dict(title=z_title),
        margin={"r":0,"t":40,"l":0,"b":0}
    )
    plot_df = plot_df.sort_values('Workers', ascending=False)
    top_provinces = plot_df.head(5)
    table = html.Table([
        html.Thead(
            html.Tr([html.Th("Province"), html.Th("Workers"), html.Th("Population")])
        ),
        html.Tbody([
            html.Tr([
                html.Td(row['Province']),
                html.Td(f"{row['Workers']:.1f}"),
                html.Td(f"{row['Population']:,}")
            ]) for _, row in top_provinces.iterrows()
        ])
    ], style={'margin': '20px'})
    return fig, table

@app.callback(
    Output('gender-distribution-sunburst', 'figure'),
    [Input('occupation-category-dropdown', 'value')]
)
def update_gender_sunburst(occupation_code):
    if occupation_code == '0':
        filtered_df = df[df['Occupation'].str.startswith('0 ')]
    else:
        filtered_df = df[df['Occupation'].str.startswith(occupation_code)]
    fig = px.sunburst(
        filtered_df,
        path=['Major Occupation Name', 'Occupation'],
        values='Total',
        color='Women',
        color_continuous_scale='RdBu',
        range_color=[0, filtered_df['Total'].max()],
        title=f"Gender Distribution in {occupation_mapping[occupation_code]}"
    )
    fig.update_layout(margin=dict(t=40, l=0, r=0, b=0))
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
 
