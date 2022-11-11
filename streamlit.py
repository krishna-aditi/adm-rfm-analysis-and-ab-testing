# -*- coding: utf-8 -*-
"""
Created on Thu Nov 10 15:50:49 2022

@author: krish
"""
import streamlit as st
from st_aggrid import AgGrid
from rfmAnalysis.RFManalysis import rfm
from abTesting.abtesting import conversion_rate, lift, std_err, std_err_diff, z_score, p_value, significance, plot_chart, style_negative, style_p_value, calculate_significance
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

plt.rcParams['font.family'] = 'Verdana'
plt.rcParams.update({'font.size': 30})
plt.style.use('ggplot')

def main():
    # st. set_page_config(layout="wide")
    page = st.sidebar.radio("Navigation Pane:", ["RFM Analysis", "A/B Testing"])
   
    #Add sidebar to the app
    st.sidebar.markdown("")
    st.sidebar.markdown("")
    st.sidebar.markdown("")
    st.sidebar.markdown("")
    st.sidebar.markdown("")
    st.sidebar.markdown("")
    st.sidebar.markdown("##### Made by: :computer:")
    st.sidebar.markdown("### Aditi Krishna :dog:")
    
    if page == "RFM Analysis":
        st.write(
            """
            # 📊 Superstore RFM Analysis
            """
        )
        
        use_example_file = st.checkbox(
        "Use example file!", False, help="Use in-built example file to demo the app"
        )
        
        if use_example_file:
            uploaded_file = "data/sample-orders.csv"
            rfm(uploaded_file)
            
            # About RFM
            st.markdown('## What is RFM Analysis?')
            st.markdown('It is a customer segmentation technique that uses past purchase behavior to segment customers. To perform RFM analysis, we divide customers into four equal groups according to the distribution of values for recency, frequency, and monetary value.')
            st.markdown('**1. Recency (R)**: Time since last purchase')
            st.markdown('**2. Frequency (F)**: Total number of purchases')
            st.markdown('**3. Monetary Value (M)**: Total monetary value')
            
            # Understanding the Customer Segments
            df_segments = { 'Segment' : ['Best Customers', 'Loyal Customers', 'Big Spenders', 'Almost Lost', 'Lost Customers', 'Lost Cheap Customers'],
                   'RFM': ['111', 'X1X', 'XX1', '311', '411', '444'],
                   'Description' : ['Customers who bought most recently, most often and spend the most.', '	Customers who bought most recently', '	Customers who spend the most', "Haven't purchased for some time, but purchased frequently and spend the most.", "Haven't purchased for some time, but purchased frequently and spend the most.", 'Last purchase long ago, purchased few and spend little.'],
                   'Marketing' : ['No price incentives, New products and loyalty programs', 'Use R and M to further segment.', 'Market your most expensive products.', 'Agressive price incentives', 'Agressive price incentives.', "Don't spend too much trying to re-acquire."]
                 }
            df_segments = pd.DataFrame(df_segments, columns= ['Segment', 'RFM', 'Description', 'Marketing'])
            html_temp_title = """
                    <div style="background-color:#154360;padding:2px">
                    <h3 style="color:white;text-align:center;">Key RFM Segments</h3>
                    </div>
                """
            st.markdown("")
            st.markdown(html_temp_title, unsafe_allow_html=True)
            st.markdown("")
            AgGrid(df_segments, theme='blue', height = 200, width = 150)
            
            # Analysis Understanding 
            html_temp = """
            <div style="background-color:#154360;padding:2px">
            <h3 style="color:White;text-align:center;">Understanding Segmented data</h3>
            </div>
            """
            st.markdown(html_temp, unsafe_allow_html=True)
            st.markdown("")
            # Read analysis table
            html_temp_title = """
                    <div style="background-color:SteelBlue;padding:4px">
                    <h6 style="color:white;text-align:center;">Interpreting the RFM Analysis</h6>
                    </div>
                """
            st.markdown(html_temp_title, unsafe_allow_html=True)
            
            # Read output file        
            rfm_tab = pd.read_csv('data/rfm-table.csv', encoding='latin1')
            
            # New column 'Segment' based on RFM value
            rfm_tab.loc[ rfm_tab['RFMClass'].astype('str').str.match(r'\d1\d') == True, 'Segment'] = 'Loyal Customers'
            rfm_tab.loc[ rfm_tab['RFMClass'].astype('str').str.match(r'\d\d1') == True, 'Segment'] = 'Big Spenders'
            rfm_tab.loc[ rfm_tab['RFMClass'].astype('str').str.match(r'111') == True, 'Segment'] = 'Best Customers'
            rfm_tab.loc[ rfm_tab['RFMClass'].astype('str').str.match(r'311') == True, 'Segment'] = 'Almost Lost'
            rfm_tab.loc[ rfm_tab['RFMClass'].astype('str').str.match(r'411') == True, 'Segment'] = 'Lost Customers'
            rfm_tab.loc[ rfm_tab['RFMClass'].astype('str').str.match(r'444') == True, 'Segment'] = 'Lost Cheap Customers'
            rfm_tab.loc[ rfm_tab['Segment'].isnull(), 'Segment'] = 'Others'
            
            # MonetaryValue
            rfm_tab['MonetaryValue'] = '$' + rfm_tab['MonetaryValue'].astype(str)

            # Copy of the OG dataframe            
            rfm_analysis = rfm_tab.copy()
            rfm_analysis = rfm_analysis.drop(['R_Quartile', 'F_Quartile', 'M_Quartile'], axis = 1)
            rfm_analysis.rename(columns={ 'Frequency': 'Orders', 
                                       'RFMClass': 'RFM'}, inplace=True)
            
            # Interactive table
            AgGrid(rfm_analysis, theme='blue', height = 200, width = 150)
            
            # Writeup to help understand RFM
            st.markdown("#### Interpretation")
            st.markdown('**1.  Etha K.** belongs to the “Best Customers” segment; she purchased recently (R=1), frequently buys (F=1) and spent the most (M=1)')
            st.markdown('**2.  Jerold Sporer** is about to enter the “Lost Cheap Customers” segment; he has not purchased in a while (R=3), bought few (F=4), and spent little (M=4).')
            st.markdown('**3. Anie Hettinger** is a type of “Almost Lost” customer. She has not made a purchase for some time (R=3), she bought somewhat frequently (F=2), but she is in the group who spent the most (M=1).')
                        
            ##### Plots
            fontsize_label= 16
            
            # Countplot for Segments
            html_temp_title = """
                    <div style="background-color:SteelBlue;padding:4px">
                    <h6 style="color:white;text-align:center;"># Customers / Segment</h6>
                    </div>
                """
            st.markdown(html_temp_title, unsafe_allow_html=True)
            # st.markdown("")
           
            sns.catplot(y="Segment", kind="count", data=rfm_analysis, palette = 'crest')
            # Labelling
            # plt.title('# Customers / Segment', fontdict={'fontsize': fontsize_title})
            plt.xlabel('Customer Count', fontdict={'fontsize': fontsize_label})
            plt.ylabel('Segment', fontdict={'fontsize': fontsize_label})
            # Set size for plot
            fig = plt.gcf()
            fig.set_size_inches(20,10)
            st.pyplot(fig)
            
            # Number of customers (y) vs. Number of orders (x)
            html_temp_title = """
                    <div style="background-color:SteelBlue;padding:4px">
                    <h6 style="color:white;text-align:center;"># Customers vs. # Orders</h6>
                    </div>
                """
            st.markdown(html_temp_title, unsafe_allow_html=True)
            # st.markdown("")
            sns.catplot(x="Orders", kind="count", data=rfm_analysis, palette = 'crest')
            # plt.title('# Customers vs. # Orders (x)',fontdict={'fontsize': fontsize_title})
            plt.xlabel('# Customers', fontdict={'fontsize': fontsize_label})
            plt.ylabel('# Orders',fontdict={'fontsize': fontsize_label})
            # Set size for plot
            fig = plt.gcf()
            fig.set_size_inches(20,10)
            st.pyplot(fig)
            
        
    if page == "A/B Testing":
        
        st.write(
            """
            # 📊 A/B Testing for Smart Ads
            """
        )
    
        use_example_file_ab = st.checkbox(
        "Use example file!", False, help="Use in-built example file to demo the app"
        )
        
        ab_default = None
        result_default = None
        
        # If CSV is not uploaded and checkbox is filled, use values from the example file
        # and pass them down to the next if block
        
        if use_example_file_ab:
            uploaded_file= "data/AdSmartABdata.csv"
                        
            df = pd.read_csv(uploaded_file)
            html_temp_title = """
                    <div style="background-color:#154360;padding:2px">
                    <h3 style="color:white;text-align:center;">Data preview</h3>
                    </div>
                """
            st.markdown(html_temp_title, unsafe_allow_html=True)
            st.markdown("")
            
            AgGrid(df, theme='blue', height = 200, width = 150)
            
            # Metrics information
            st.markdown("")
            html_temp_title = """
                    <div style="background-color:SteelBlue;padding:2px">
                    <h6 style="color:white;text-align:center;padding:4px;">Metrics used for A/B Testing</h6>
                    </div>
                """
            st.markdown(html_temp_title, unsafe_allow_html=True)
            st.markdown("")
            st.markdown("**1. Conversion Rate:** The conversion rate for a given number of conversions and number of visitors, i.e., (no. of conversions / no. of visitors) x 100 ).")
            st.markdown("")
            st.markdown("**2. Lift:** The relative uplift in conversion rate between Group A (control) and Group B (treatment).")
            st.markdown("")
            st.markdown("**3. Z-score:** It is a test statistic measuring exactly how many standard deviations above or below the mean a data point is.")
            st.markdown("")
            st.markdown("**4. P-value**: The probability of obtaining test results at least as extreme as the results actually observed, under the assumption that the null hypothesis is in effect.") 
            st.markdown("")
            st.markdown("**5. Significance**: If a p-value (p) is less than the significance level (alpha) is statistically significant.")
            st.markdown("")
            
            html_temp_title = """
                    <div style="background-color:SteelBlue;padding:2px">
                    <h6 style="color:white;text-align:center;padding:4px;">Select columns for analysis</h6>
                    </div>
                """
            st.markdown(html_temp_title, unsafe_allow_html=True)
            
            with st.form(key="my_form"):
                ab = st.multiselect(
                    "A/B column",
                    options=df.columns,
                    help="Select which column refers to your A/B testing labels.",
                    default=ab_default
                )
                if ab:
                    control = df[ab[0]].unique()[0]
                    treatment = df[ab[0]].unique()[1]
                    decide = st.radio(
                        f"Is {treatment} Group B?",
                        options=["Yes", "No"],
                        help="Select yes if this is group B (or the treatment group) from your test.",
                    )
                    if decide == "No":
                        control, treatment = treatment, control
                    visitors_a = df[ab[0]].value_counts()[control]
                    visitors_b = df[ab[0]].value_counts()[treatment]
        
                result = st.multiselect(
                    "Result column",
                    options=df.columns,
                    help="Select which column shows the result of the test.",
                    default=result_default,
                )
        
                if result:
                    conversions_a = (
                        df[[ab[0], result[0]]].groupby(ab[0]).agg("sum")[result[0]][control]
                    )
                    conversions_b = (
                        df[[ab[0], result[0]]].groupby(ab[0]).agg("sum")[result[0]][treatment]
                    )
        
                with st.expander("Adjust test parameters"):
                    st.markdown("### Parameters")
                    st.radio(
                        "Hypothesis type",
                        options=["One-sided", "Two-sided"],
                        index=0,
                        key="hypothesis",
                        help="TBD",
                    )
                    st.slider(
                        "Significance level (α)",
                        min_value=0.01,
                        max_value=0.10,
                        value=0.05,
                        step=0.01,
                        key="alpha",
                        help=" The probability of mistakenly rejecting the null hypothesis, if the null hypothesis is true. This is also called false positive and type I error. ",
                    )
        
                submit_button = st.form_submit_button(label="Submit")
        
            if not ab or not result:
                st.warning("Please select both an **A/B column** and a **Result column**.")
                st.stop()
                
            st.write("")
            html_temp_title = """
                    <div style="background-color:#154360;padding:2px">
                    <h3 style="color:white;text-align:center;">Results for A/B Test for Smart Ad data</h3>
                    </div>
                """
            st.markdown(html_temp_title, unsafe_allow_html=True)
            st.write("")
        
            # Obtain the metrics to display
            calculate_significance(
                conversions_a,
                conversions_b,
                visitors_a,
                visitors_b,
                st.session_state.hypothesis,
                st.session_state.alpha,
            )
        
            mcol1, mcol2 = st.columns(2)
        
            # Use st.metric to diplay difference in conversion rates
            with mcol1:
                st.metric(
                    "Delta",
                    value=f"{(st.session_state.crb - st.session_state.cra):.3g}%",
                    delta=f"{(st.session_state.crb - st.session_state.cra):.3g}%"
                )
            # Display whether or not A/B test result is statistically significant
            with mcol2:
                st.metric("Significant?", value=st.session_state.significant)
        
            # Create a single-row, two-column DataFrame to use in bar chart
            results_df = pd.DataFrame(
                {
                    "Group": ["Control", "Treatment"],
                    "Conversion": [st.session_state.cra, st.session_state.crb],
                }
            )
            st.write("")
            st.write("")
        
            # Plot bar chart of conversion rates
            plot_chart(results_df)
        
            ncol1, ncol2 = st.columns([2, 1])
        
            table = pd.DataFrame(
                {
                    "Converted": [conversions_a, conversions_b],
                    "Total": [visitors_a, visitors_b],
                    "% Converted": [st.session_state.cra, st.session_state.crb],
                },
                index=pd.Index(["Control", "Treatment"]),
            )
        
            # Format "% Converted" column values to 3 decimal places
            table1 = ncol1.write(table.style.format(formatter={("% Converted"): "{:.3g}%"}))
        
            metrics = pd.DataFrame(
                {
                    "p-value": [st.session_state.p],
                    "z-score": [st.session_state.z],
                    "uplift": [st.session_state.uplift],
                },
                index=pd.Index(["Metrics"]),
            )
        
            # Color negative values red; color significant p-value green and not significant red
            table2 = ncol1.write(
                metrics.style.format(
                    formatter={("p-value", "z-score"): "{:.3g}", ("uplift"): "{:.3g}%"}
                )
                .applymap(style_negative, props="color:red;")
                .apply(style_p_value, props="color:red;", axis=1, subset=["p-value"])
            )
            
                        
if __name__ == "__main__":
    main()
