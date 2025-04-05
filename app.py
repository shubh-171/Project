{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 4,
   "id": "7ff3501e-38d4-4335-b32e-21b9aeaaf934",
   "metadata": {},
   "outputs": [],
   "source": [
    "import dash\n",
    "from dash import dcc, html\n",
    "from dash.dependencies import Input, Output\n",
    "import plotly.express as px\n",
    "import pandas as pd"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 5,
   "id": "68651d55-c37a-447d-a08b-156e8e360e57",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/html": [
       "\n",
       "        <iframe\n",
       "            width=\"100%\"\n",
       "            height=\"650\"\n",
       "            src=\"http://127.0.0.1:8050/\"\n",
       "            frameborder=\"0\"\n",
       "            allowfullscreen\n",
       "            \n",
       "        ></iframe>\n",
       "        "
      ],
      "text/plain": [
       "<IPython.lib.display.IFrame at 0x7b7f14d0a9e0>"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    }
   ],
   "source": [
    "\n",
    "\n",
    "data_cleaned = pd.read_csv('data.csv')\n",
    "\n",
    "essential_services = ['Nurses', 'Police', 'Firefighters']\n",
    "\n",
    "app = dash.Dash(__name__)\n",
    "\n",
    "server = app.server\n",
    "\n",
    "app.layout = html.Div([\n",
    "    html.H1(\"Essential Services Distribution Dashboard\"),\n",
    "    \n",
    "    dcc.Dropdown(\n",
    "        id='service-dropdown',\n",
    "        options=[{'label': service, 'value': service} for service in essential_services],\n",
    "        value='Nurses',  # Default value\n",
    "        style={'width': '50%'}\n",
    "    ),\n",
    "    \n",
    "    dcc.Graph(id='distribution-chart')\n",
    "])\n",
    "\n",
    "@app.callback(\n",
    "    Output('distribution-chart', 'figure'),\n",
    "    Input('service-dropdown', 'value')\n",
    ")\n",
    "def update_graph(selected_service):\n",
    "    filtered_data = data_cleaned[data_cleaned['Occupation'].str.contains(selected_service, case=False, na=False)]\n",
    "    \n",
    "    fig = px.bar(filtered_data, \n",
    "                 x='Geography', \n",
    "                 y='Total', \n",
    "                 title=f'Distribution of {selected_service} across Provinces/Territories',\n",
    "                 labels={'Total': 'Number of Workers', 'Geography': 'Administrative Unit'},\n",
    "                 color='Geography')\n",
    "\n",
    "    fig.update_layout(barmode='stack', xaxis_tickangle=-45)\n",
    "    \n",
    "    return fig\n",
    "\n",
    "if __name__ == '__main__':\n",
    "    app.run(debug=True)\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "id": "a2426e81-1243-4ca6-a338-b30d1f483c37",
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "anaconda-2024.02-py310",
   "language": "python",
   "name": "conda-env-anaconda-2024.02-py310-py"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.10.14"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
