import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from streamlit_extras.colored_header import colored_header

from utils.auth import is_authenticated
from styles.custom import apply_custom_styles

# Page configuration
st.set_page_config(
    page_title="Recommendations | Energy Anomaly Detection",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom styles
apply_custom_styles()

# Check authentication
if not is_authenticated():
    st.warning("Please login to access this page")
    st.stop()

def analyze_anomalies(results):
    """
    Analyze anomalies and generate recommendations
    """
    recommendations = []
    
    if results is None or len(results) == 0:
        return []
    
    # Get anomalies
    anomalies = results[results['is_anomaly'] == 1].copy()
    
    if len(anomalies) == 0:
        recommendations.append({
            "title": "No Anomalies Detected",
            "description": "Your energy consumption patterns appear normal. Continue monitoring regularly.",
            "impact": "Low",
            "action": "Maintain current energy management practices."
        })
        return recommendations
    
    # Analyze time patterns
    anomalies['hour'] = anomalies['timestamp'].dt.hour
    anomalies['weekday'] = anomalies['timestamp'].dt.day_name()
    anomalies['is_weekend'] = anomalies['timestamp'].dt.weekday >= 5
    anomalies['is_working_hours'] = (anomalies['hour'] >= 8) & (anomalies['hour'] <= 18)
    
    # Count anomalies by hour
    hour_counts = anomalies.groupby('hour').size()
    peak_hours = hour_counts.nlargest(3).index.tolist()
    
    if len(peak_hours) > 0:
        peak_hours_str = ", ".join([f"{h}:00" for h in peak_hours])
        recommendations.append({
            "title": "Peak Hour Anomalies",
            "description": f"Unusual energy consumption detected during hours: {peak_hours_str}",
            "impact": "High" if hour_counts.max() > 5 else "Medium",
            "action": "Investigate equipment operation during these hours. Consider rescheduling energy-intensive operations."
        })
    
    # Weekend vs weekday patterns
    weekend_anomalies = anomalies[anomalies['is_weekend']].shape[0]
    weekday_anomalies = anomalies[~anomalies['is_weekend']].shape[0]
    
    if weekend_anomalies > weekday_anomalies:
        recommendations.append({
            "title": "Weekend Consumption Issues",
            "description": f"Higher than expected anomalies detected during weekends ({weekend_anomalies} anomalies)",
            "impact": "High",
            "action": "Check if systems are being properly shut down over weekends. Implement automated shutdown procedures."
        })
    
    # Working hours vs non-working hours
    working_hours_anomalies = anomalies[anomalies['is_working_hours']].shape[0]
    non_working_hours_anomalies = anomalies[~anomalies['is_working_hours']].shape[0]
    
    if non_working_hours_anomalies > working_hours_anomalies:
        recommendations.append({
            "title": "Off-hours Energy Waste",
            "description": f"Significant anomalies detected outside normal working hours ({non_working_hours_anomalies} anomalies)",
            "impact": "High",
            "action": "Implement better control systems for off-hours energy management. Check for equipment left running unnecessarily."
        })
    
    # Consumption magnitude analysis
    if 'consumption' in anomalies.columns:
        avg_normal = results[results['is_anomaly'] == 0]['consumption'].mean()
        avg_anomaly = anomalies['consumption'].mean()
        
        if avg_anomaly > avg_normal * 1.5:
            recommendations.append({
                "title": "High Consumption Spikes",
                "description": f"Anomalous consumption is {avg_anomaly/avg_normal:.1f}x higher than normal",
                "impact": "High",
                "action": "Investigate for potential equipment malfunction or inefficient operation. Consider load balancing."
            })
        elif avg_anomaly < avg_normal * 0.5:
            recommendations.append({
                "title": "Unusual Low Consumption",
                "description": f"Anomalous consumption is {avg_anomaly/avg_normal:.1f}x lower than normal",
                "impact": "Medium",
                "action": "Check for potential meter issues or unexpected system shutdowns."
            })
    
    # Temperature correlation if available
    if 'temperature' in anomalies.columns:
        temp_corr = results['consumption'].corr(results['temperature'])
        if abs(temp_corr) > 0.7:
            recommendations.append({
                "title": "Strong Temperature Dependency",
                "description": f"Energy consumption shows strong correlation with temperature (r={temp_corr:.2f})",
                "impact": "Medium",
                "action": "Optimize HVAC settings and improve building insulation. Consider smart temperature controls."
            })
    
    # Occupancy correlation if available
    if 'occupancy' in anomalies.columns:
        occ_corr = results['consumption'].corr(results['occupancy'])
        if abs(occ_corr) < 0.3:
            recommendations.append({
                "title": "Weak Occupancy Correlation",
                "description": "Energy usage doesn't scale well with building occupancy",
                "impact": "Medium",
                "action": "Implement occupancy-based controls for lighting and HVAC. Consider zone-based management."
            })
    
    # Add general recommendations if few specific ones were generated
    if len(recommendations) < 3:
        recommendations.append({
            "title": "Regular Energy Audit",
            "description": "Periodic comprehensive energy audits can identify inefficiencies",
            "impact": "Medium",
            "action": "Schedule quarterly energy audits focusing on peak usage periods."
        })
        
        recommendations.append({
            "title": "Equipment Maintenance",
            "description": "Regular maintenance improves equipment efficiency",
            "impact": "Medium",
            "action": "Establish a preventive maintenance schedule for energy-intensive equipment."
        })
    
    return recommendations

def main():
    st.title("⚡ Energy Efficiency Recommendations")
    
    colored_header(
        label="Actionable Insights",
        description="Recommendations based on detected energy consumption anomalies",
        color_name="blue-70"
    )
    
    # Check if results are available
    if st.session_state.detection_results is None:
        st.warning("No detection results available. Please run anomaly detection first.")
        st.stop()
    
    # Get the results
    results = st.session_state.detection_results
    
    # Generate recommendations
    recommendations = analyze_anomalies(results)
    
    # Display summary
    st.markdown("### Summary of Recommendations")
    
    # Count recommendations by impact
    impact_counts = {"High": 0, "Medium": 0, "Low": 0}
    for rec in recommendations:
        impact_counts[rec["impact"]] += 1
    
    # Display impact metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("High Impact", impact_counts["High"], delta=None)
    
    with col2:
        st.metric("Medium Impact", impact_counts["Medium"], delta=None)
    
    with col3:
        st.metric("Low Impact", impact_counts["Low"], delta=None)
    
    # Display recommendations
    st.markdown("### Key Recommendations")
    
    # Custom styling for recommendation cards
    st.markdown("""
    <style>
    .recommendation-card {
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .high-impact {
        background-color: rgba(255, 75, 75, 0.2);
        border-left: 5px solid #ff4b4b;
    }
    .medium-impact {
        background-color: rgba(255, 165, 0, 0.2);
        border-left: 5px solid orange;
    }
    .low-impact {
        background-color: rgba(46, 204, 113, 0.2);
        border-left: 5px solid #2ecc71;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Sort recommendations by impact
    impact_order = {"High": 0, "Medium": 1, "Low": 2}
    sorted_recommendations = sorted(recommendations, key=lambda x: impact_order[x["impact"]])
    
    # Display recommendations in expandable sections
    for i, rec in enumerate(sorted_recommendations):
        impact_class = rec["impact"].lower() + "-impact"
        
        with st.expander(f"{i+1}. {rec['title']} (Impact: {rec['impact']})", expanded=(rec["impact"] == "High")):
            st.markdown(f"""
            <div class="recommendation-card {impact_class}">
                <h4>{rec['title']}</h4>
                <p><b>Description:</b> {rec['description']}</p>
                <p><b>Recommended Action:</b> {rec['action']}</p>
                <p><b>Impact Level:</b> {rec['impact']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Potential savings visualization
    st.markdown("### Potential Energy Savings")
    
    # Create a sample savings projection
    savings_data = pd.DataFrame({
        'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        'Baseline Consumption': [100, 100, 100, 100, 100, 100],
        'Projected Consumption': [100, 95, 90, 85, 80, 75]
    })
    
    # Calculate savings percentage
    savings_data['Savings %'] = ((savings_data['Baseline Consumption'] - savings_data['Projected Consumption']) / 
                                savings_data['Baseline Consumption'] * 100)
    
    # Create the chart
    fig = go.Figure()
    
    # Add baseline consumption
    fig.add_trace(go.Bar(
        x=savings_data['Month'],
        y=savings_data['Baseline Consumption'],
        name='Current Consumption',
        marker_color='#4b7bec'
    ))
    
    # Add projected consumption
    fig.add_trace(go.Bar(
        x=savings_data['Month'],
        y=savings_data['Projected Consumption'],
        name='Projected Consumption',
        marker_color='#2ecc71'
    ))
    
    # Add savings percentage line
    fig.add_trace(go.Scatter(
        x=savings_data['Month'],
        y=savings_data['Savings %'],
        mode='lines+markers',
        name='Savings %',
        yaxis='y2',
        line=dict(color='#e74c3c', width=3),
        marker=dict(size=8)
    ))
    
    # Update layout
    fig.update_layout(
        title='Projected Energy Savings with Implemented Recommendations',
        barmode='group',
        xaxis=dict(title='Month'),
        yaxis=dict(title='Energy Consumption (kWh)', showgrid=True, gridcolor='rgba(255, 255, 255, 0.1)'),
        yaxis2=dict(
            title='Savings %',
            overlaying='y',
            side='right',
            showgrid=False,
            range=[0, 30]
        ),
        plot_bgcolor='rgba(30, 39, 46, 0.8)',
        paper_bgcolor='rgba(30, 39, 46, 0)',
        font=dict(color='white'),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # ROI analysis
    st.markdown("### Return on Investment Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Cost estimate for implementing recommendations
        implementation_costs = {
            "Equipment Upgrades": 5000,
            "Control System Improvements": 3000,
            "Maintenance Procedures": 1500,
            "Training & Awareness": 1000,
            "Monitoring Tools": 2500
        }
        
        # Create a pie chart for implementation costs
        fig_costs = px.pie(
            values=list(implementation_costs.values()),
            names=list(implementation_costs.keys()),
            title='Estimated Implementation Costs ($)',
            color_discrete_sequence=px.colors.sequential.Blues_r
        )
        
        fig_costs.update_layout(
            plot_bgcolor='rgba(30, 39, 46, 0)',
            paper_bgcolor='rgba(30, 39, 46, 0)',
            font=dict(color='white')
        )
        
        st.plotly_chart(fig_costs, use_container_width=True)
    
    with col2:
        # Projected monthly savings
        current_monthly_cost = 10000
        projected_savings_percent = 15
        annual_savings = current_monthly_cost * (projected_savings_percent / 100) * 12
        total_implementation_cost = sum(implementation_costs.values())
        payback_period = total_implementation_cost / (annual_savings / 12)
        
        # Create ROI visualization
        payback_data = []
        cumulative_savings = 0
        
        for month in range(1, 25):
            monthly_savings = current_monthly_cost * (projected_savings_percent / 100)
            cumulative_savings += monthly_savings
            net_position = cumulative_savings - total_implementation_cost
            
            payback_data.append({
                'Month': month,
                'Cumulative Savings': cumulative_savings,
                'Net Position': net_position
            })
        
        payback_df = pd.DataFrame(payback_data)
        
        fig_roi = px.line(
            payback_df,
            x='Month',
            y=['Cumulative Savings', 'Net Position'],
            title='ROI Analysis - Payback Period',
            labels={"value": "Amount ($)", "variable": "Metric"}
        )
        
        # Add horizontal line at zero
        fig_roi.add_hline(y=0, line_dash="dash", line_color="white")
        
        # Add vertical line at payback point
        fig_roi.add_vline(x=payback_period, line_dash="dash", line_color="green",
                          annotation_text=f"Payback: {payback_period:.1f} months",
                          annotation_position="top right")
        
        # Add implementation cost horizontal line
        fig_roi.add_hline(y=-total_implementation_cost, line_dash="dot", line_color="red",
                          annotation_text=f"Initial Investment: ${total_implementation_cost}",
                          annotation_position="bottom right")
        
        fig_roi.update_layout(
            plot_bgcolor='rgba(30, 39, 46, 0.8)',
            paper_bgcolor='rgba(30, 39, 46, 0)',
            font=dict(color='white'),
            xaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'),
            yaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'),
            height=400
        )
        
        st.plotly_chart(fig_roi, use_container_width=True)
    
    # ROI metrics
    st.markdown("### Financial Impact")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Annual Savings", f"${annual_savings:,.2f}")
    
    with col2:
        st.metric("Implementation Cost", f"${total_implementation_cost:,.2f}")
    
    with col3:
        st.metric("Payback Period", f"{payback_period:.1f} months")
    
    with col4:
        roi_3yr = (annual_savings * 3 - total_implementation_cost) / total_implementation_cost * 100
        st.metric("3-Year ROI", f"{roi_3yr:.1f}%")
    
    # Implementation timeline
    st.markdown("### Implementation Timeline")
    
    # Create a Gantt chart for implementation
    tasks = [
        dict(Task="Energy Audit", Start='2023-08-01', Finish='2023-08-15', Resource='Analysis'),
        dict(Task="Equipment Upgrades", Start='2023-08-20', Finish='2023-09-15', Resource='Implementation'),
        dict(Task="Control System Improvements", Start='2023-09-01', Finish='2023-09-30', Resource='Implementation'),
        dict(Task="Staff Training", Start='2023-09-15', Finish='2023-09-30', Resource='Training'),
        dict(Task="Monitoring Setup", Start='2023-10-01', Finish='2023-10-15', Resource='Implementation'),
        dict(Task="Post-Implementation Review", Start='2023-11-01', Finish='2023-11-15', Resource='Analysis')
    ]
    
    fig_gantt = px.timeline(
        tasks, 
        x_start="Start", 
        x_end="Finish", 
        y="Task",
        color="Resource",
        title="Recommendation Implementation Timeline",
        color_discrete_map={
            "Analysis": "#4b7bec",
            "Implementation": "#3867d6",
            "Training": "#2ecc71"
        }
    )
    
    fig_gantt.update_layout(
        plot_bgcolor='rgba(30, 39, 46, 0.8)',
        paper_bgcolor='rgba(30, 39, 46, 0)',
        font=dict(color='white'),
        xaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'),
        yaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'),
        height=400
    )
    
    st.plotly_chart(fig_gantt, use_container_width=True)
    
    # Download recommendations as PDF
    st.markdown("### Export Recommendations")
    st.markdown("Download a detailed report of all recommendations and analysis.")
    
    # Generate report (in a real app, this would create a PDF)
    if st.button("Generate Recommendations Report"):
        st.success("Report generated successfully! (This is a placeholder - in a real app, a PDF would be generated)")
    
    # Footer
    st.markdown("---")
    st.markdown("© 2025 Opulent Chikwiramakomo. All rights reserved.")

if __name__ == "__main__":
    main()
