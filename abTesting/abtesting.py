# -*- coding: utf-8 -*-
"""
Created on Fri Nov 11 15:53:06 2022

@author: krish
"""

import streamlit as st
import pandas as pd
import numpy as np
import scipy.stats
from scipy.stats import norm
import altair as alt

st.set_page_config(
    page_title="A/B Testing App", page_icon="📊", initial_sidebar_state="expanded"
)


def conversion_rate(conversions, visitors):
    """Returns the conversion rate for a given number of conversions and number of visitors.
    Parameters
    ----------
    conversions: int
        Total number of conversions
    visitors: int
        Total number of unique visitors
    Returns
    -------
    float
        The conversion rate
    """
    return (conversions / visitors) * 100


def lift(cra, crb):
    """Returns the relative uplift in conversion rate.
    Parameters
    ----------
    cra: float
        Conversion rate of Group A
    crb: float
        Conversion rate of Group B
    Returns
    -------
    float
        Relative uplift in conversion rate
    """
    return ((crb - cra) / cra) * 100


def std_err(cr, visitors):
    """
    Returns the standard error of the conversion rate.
    The standard error is used to calculate the deviation in conversion rates for a specific
    Group if the experiment is repeated multiple times.
    For a given conversion rate (cr) and a number of trials (visitors),
    the standard error is calculated as:
    Standard Error (std_err) = Square root of (cr * (1-cr) / visitors)
    Parameters
    ----------
    cr: float
        Conversion rate of a group (either A or B)
    visitors: float
        Total number of unique visitors
    Returns
    -------
    float
        Returns the standard error of the conversion rate
    """
    return np.sqrt((cr / 100 * (1 - cr / 100)) / visitors)


def std_err_diff(sea, seb):
    """Returns the z-score test statistic.
    Parameters
    ----------
    sea: float
        Standard error of conversion rate of Group A
    seb: float
        Standard error of conversion rate of Group B
    Returns
    -------
    float
        Standard error of the sampling distribution difference between
        Group A and Group B
    """
    return np.sqrt(sea ** 2 + seb ** 2)


def z_score(cra, crb, error):
    """Returns the z-score test statistic measuring exactly how many
    standard deviations above or below the mean a data point is.
    Parameters
    ----------
    cra: float
        Conversion rate of Group A
    crb: float
        Conversion rate of Group B
    error: float
        Standard error of the sampling distribution difference between
        Group A and Group B
    Returns
    -------
    float
        z-score test statistic
    """
    return ((crb - cra) / error) / 100


def p_value(z, hypothesis):
    """Returns the p-value, which is the probability of obtaining test
    results at least as extreme as the results actually observed, under
    the assumption that the null hypothesis is correct.
    Parameters
    ----------
    z: float
        z-score test statistic
    hypothesis: str
        Type of hypothesis test: "One-sided" or "Two-sided"
        "One-sided" is a statistical hypothesis test set up to
        show that the sample mean would be higher or lower than the
        population mean, but not both.
        "Two-sided" is a statistical hypothesis test in which the
        critical area of a distribution is two-sided and tests whether
        a sample is greater or less than a range of values.
    Returns
    -------
    float
        p-value
    """
    if hypothesis == "One-sided" and z < 0:
        return 1 - norm().sf(z)
    elif hypothesis == "One-sided" and z >= 0:
        return norm().sf(z) / 2
    else:
        return norm().sf(z)


def significance(alpha, p):
    """Returns whether the p-value is statistically significant or not.
    A p-value (p) less than the significance level (alpha) is statistically
    significant.
    Parameters
    ----------
    alpha: float
        The sigificance level (α) is the probability of a type I error --
        the probability of rejecting the null hypothesis when it is true
    p: float
        p-value
    Returns
    -------
    str
        "YES" if significant result; else "NO"
    """
    return "YES" if p < alpha else "NO"


def plot_chart(df):
    """Diplays a bar chart of conversion rates of A/B test groups,
    with the y-axis denoting the conversion rates.
    Parameters
    ----------
    df: pd.DataFrame
        The source DataFrame containing the data to be plotted
    Returns
    -------
    streamlit.altair_chart
        Bar chart with text above each bar denoting the conversion rate
    """
    chart = (
        alt.Chart(df)
        .mark_bar(color="#fdc086")
        .encode(
            x=alt.X("Group:O", axis=alt.Axis(labelAngle=0)),
            y=alt.Y("Conversion:Q", title="Conversion rate (%)"),
            opacity="Group:O",
        )
        .properties(width=500, height=500)
    )

    # Place conversion rate as text above each bar
    chart_text = chart.mark_text(
        align="center", baseline="middle", dy=-10, color="black"
    ).encode(text=alt.Text("Conversion:Q", format=",.3g"))

    return st.altair_chart((chart + chart_text).interactive())


def style_negative(v, props=""):
    """Helper function to color text in a DataFrame if it is negative.
    Parameters
    ----------
    v: float
        The text (value) in a DataFrame to color
    props: str
        A string with a CSS attribute-value pair. E.g "color:red;"
        See: https://pandas.pydata.org/pandas-docs/stable/user_guide/style.html
    Returns
    -------
    A styled DataFrame with negative values colored in red.
    Example
    -------
    >>> df.style.applymap(style_negative, props="color:red;")
    """
    return props if v < 0 else None


def style_p_value(v, props=""):
    """Helper function to color p-value in DataFrame. If p-value is
    statististically significant, text is colored green; else red.
    Parameters
    ----------
    v: float
        The text (value) in a DataFrame to color
    props: str
        A string with a CSS attribute-value pair. E.g "color:green;"
        See: https://pandas.pydata.org/pandas-docs/stable/user_guide/style.html
    Returns
    -------
    A styled DataFrame with negative values colored in red.
    Example
    -------
    >>> df.style.apply(style_p_value, props="color:red;", axis=1, subset=["p-value"])
    """
    return np.where(v < st.session_state.alpha, "color:green;", props)


def calculate_significance(
    conversions_a, conversions_b, visitors_a, visitors_b, hypothesis, alpha
):
    """Calculates all metrics to be displayed including conversion rates,
    uplift, standard errors, z-score, p-value, significance, and stores them
    as session state variables.
    Parameters
    ----------
    conversions_a: int
        Number of users who converted when shown variant/Group A
    conversions_b: int
        Number of users who converted when shown variant/Group B
    visitors_a: int
        Total number of users shown variant/Group A
    visitors_b: int
       Total number of users shown variant/Group B
    hypothesis: str
        Type of hypothesis test: "One-sided" or "Two-sided"
        "One-sided" is a statistical hypothesis test set up to
        show that the sample mean would be higher or lower than the
        population mean, but not both.
        "Two-sided" is a statistical hypothesis test in which the
        critical area of a distribution is two-sided and tests whether
        a sample is greater or less than a range of values.
    alpha: float
        The sigificance level (α) is the probability of a type I error --
        the probability of rejecting the null hypothesis when it is true
    """
    st.session_state.cra = conversion_rate(int(conversions_a), int(visitors_a))
    st.session_state.crb = conversion_rate(int(conversions_b), int(visitors_b))
    st.session_state.uplift = lift(st.session_state.cra, st.session_state.crb)
    st.session_state.sea = std_err(st.session_state.cra, float(visitors_a))
    st.session_state.seb = std_err(st.session_state.crb, float(visitors_b))
    st.session_state.sed = std_err_diff(st.session_state.sea, st.session_state.seb)
    st.session_state.z = z_score(
        st.session_state.cra, st.session_state.crb, st.session_state.sed
    )
    st.session_state.p = p_value(st.session_state.z, st.session_state.hypothesis)
    st.session_state.significant = significance(
        st.session_state.alpha, st.session_state.p
    )