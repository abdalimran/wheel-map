#!/usr/bin/env python3

import streamlit as st
import plotly.express as px
import pandas as pd


def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


@st.cache()
def get_df(file):
    extension = file.name.split('.')[-1]
    if extension.upper() == 'CSV':
        df = pd.read_csv(file)
    elif extension.upper() in ['XLSX', 'XLS']:
        df = pd.read_excel(file, engine='openpyxl')
    return df


@st.cache()
def wheel_map(data, title, center_label, hierarchy, color, maxdepth=None, height=750, width=750):
    data = data.fillna(" ")
    data['center_label'] = center_label

    fig = px.sunburst(data_frame=data,
                      path=['center_label']+hierarchy,
                      maxdepth=maxdepth,
                      color=color,
                      width=width,
                      height=height)

    fig.update_layout(title_text=title,
                      title_x=0.5,
                      font=dict(
                          family="Arial, sans-serif",
                          size=18,
                          color="Black")
                      )

    return fig


def download_data(chart, download_format):
    if download_format in ["png", "jpeg", "webp", "svg", "pdf"]:
        return chart.to_image(format=download_format, engine="kaleido")
    elif download_format == "html (full)":
        return chart.to_html()
    elif download_format == "html (div only)":
        return chart.to_html(full_html=False)
    else:
        return None


def main():
    sidebar = st.sidebar
    sidebar.markdown("""<h1>Wheel Map Maker</h1>""", unsafe_allow_html=True)
    main_panel, = st.columns(1)

    file = sidebar.file_uploader("Upload dataset", type=['csv', 'xlsx', 'xls'], help="Uplad a file for visualization. Supported formats: csv, xlsx, xls")
    if not file:
        sidebar.write("Upload a .csv or .xlsx file to get started")
        sidebar.markdown(f"[Save](https://raw.githubusercontent.com/abdalimran/wheel-map/main/sample_data_wheel_map.csv) the sample data to try out!", unsafe_allow_html=True)
        with main_panel:
            main_panel.warning(
                "No datset has been uploaded! Please, upload a dataset to start the process.")
        return
    else:
        data = get_df(file)
        all_features = list(data.columns)
        title = sidebar.text_input("Wheel map title", help="Give a title for the map.")
        center_label = sidebar.text_input("Center label", help="Give a name for the center of the wheel.")
        hierarchy = sidebar.multiselect("Select columns by hierarchy", tuple(all_features), help="Select the columns in a hierarchal order for showing in the wheel map.")
        maxdepth = sidebar.number_input("Maximum depth", min_value=1, max_value=1+len(hierarchy), value=1+len(hierarchy), help="Maximum depth of the wheel hierarchy level.")
        sh, sw = sidebar.columns(2)
        height = sh.number_input("Height", min_value=500, max_value=2500, value=750, help="Height of the map (plot area) in pixel.")
        width = sw.number_input("Width", min_value=500, max_value=2500, value=750, help="Width of the map (plot area) in pixel.")

        with main_panel:
            chart = wheel_map(data=data,
                              title=title,
                              center_label=center_label,
                              hierarchy=hierarchy,
                              color=hierarchy[0] if hierarchy else all_features[0],
                              maxdepth=maxdepth,
                              height=height,
                              width=width)

            st.plotly_chart(chart)

        download_format = sidebar.selectbox("Select a download format", tuple(["png", "jpeg", "webp", "svg", "pdf", "html (full)", "html (div only)"]), help="Select a format in which you want to download the map.")

        sidebar.download_button(label='Download Map',
                                data=download_data(chart, download_format),
                                file_name=f'{"_".join((map(lambda x: x.lower(), title.split())))}.{download_format}')

    sidebar.markdown(
        '<br><p style="text-align:center;">Developed by <a href=https://www.linkedin.com/in/abdalimran/>Imran</a> with ❤️ &copy; 2021</p>', unsafe_allow_html=True)


if __name__ == '__main__':
    st.set_page_config(layout="wide", page_title="Wheel Map Maker", page_icon="📊")
    local_css("style.css")
    main()
