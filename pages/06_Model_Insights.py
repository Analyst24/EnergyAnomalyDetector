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
    page_title="Model Insights | Energy Anomaly Detection",
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

def main():
    st.title("⚡ Model Insights")
    
    colored_header(
        label="Model Performance Analysis",
        description="Detailed insights into the performance of the anomaly detection models",
        color_name="blue-70"
    )
    
    # Check if model metrics are available
    if st.session_state.model_metrics is None:
        st.warning("No model metrics available. Please run anomaly detection first.")
        st.stop()
    
    # Get model info and results
    model_info = st.session_state.model_metrics
    results = st.session_state.detection_results
    algorithm = st.session_state.selected_algorithm
    
    # Create display for model performance
    st.markdown(f"### {algorithm} Model Performance")
    
    # Model information cards
    col1, col2, col3 = st.columns(3)
    
    # Display different metrics based on the algorithm
    if algorithm == "Isolation Forest":
        with col1:
            st.metric("Contamination", f"{model_info.get('contamination', 0):.3f}")
        
        with col2:
            st.metric("Number of Estimators", model_info.get('n_estimators', 0))
        
        with col3:
            anomaly_percent = (results['is_anomaly'].sum() / len(results)) * 100
            st.metric("Detected Anomaly %", f"{anomaly_percent:.2f}%")
    
    elif algorithm == "AutoEncoder":
        with col1:
            st.metric("Threshold Percentile", f"{model_info.get('threshold_percent', 0)}")
        
        with col2:
            st.metric("Training Epochs", model_info.get('epochs', 0))
        
        with col3:
            st.metric("Reconstruction Error Threshold", f"{model_info.get('threshold', 0):.4f}")
    
    elif algorithm == "K-Means":
        with col1:
            st.metric("Number of Clusters", model_info.get('n_clusters', 0))
        
        with col2:
            st.metric("Threshold Percentile", f"{model_info.get('threshold_percent', 0)}")
        
        with col3:
            st.metric("Distance Threshold", f"{model_info.get('threshold', 0):.4f}")
    
    # Model performance visualizations
    st.markdown("### Model Analysis")
    
    # Algorithm-specific visualizations
    if algorithm == "Isolation Forest":
        # Display anomaly score distribution
        if 'anomaly_score' in results.columns:
            fig = px.histogram(
                results,
                x='anomaly_score',
                color='is_anomaly',
                marginal='box',
                nbins=50,
                title="Isolation Forest Anomaly Score Distribution",
                labels={"anomaly_score": "Anomaly Score", "is_anomaly": "Is Anomaly"},
                color_discrete_map={0: "blue", 1: "red"}
            )
            
            # Add vertical line for threshold
            if 'threshold' in model_info:
                fig.add_vline(
                    x=model_info['threshold'],
                    line_dash="dash",
                    line_color="green",
                    annotation_text="Threshold",
                    annotation_position="top right"
                )
            
            fig.update_layout(
                plot_bgcolor='rgba(30, 39, 46, 0.8)',
                paper_bgcolor='rgba(30, 39, 46, 0)',
                font=dict(color='white'),
                xaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'),
                yaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'),
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Feature importance if available
            if 'feature_importances' in model_info:
                feat_imp = model_info['feature_importances']
                feat_imp_df = pd.DataFrame({
                    'Feature': list(feat_imp.keys()),
                    'Importance': list(feat_imp.values())
                }).sort_values(by='Importance', ascending=False)
                
                fig_imp = px.bar(
                    feat_imp_df,
                    x='Feature',
                    y='Importance',
                    title="Feature Importance for Anomaly Detection",
                    labels={"Importance": "Importance Score", "Feature": "Feature Name"}
                )
                
                fig_imp.update_layout(
                    plot_bgcolor='rgba(30, 39, 46, 0.8)',
                    paper_bgcolor='rgba(30, 39, 46, 0)',
                    font=dict(color='white'),
                    xaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'),
                    yaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'),
                    height=400
                )
                
                st.plotly_chart(fig_imp, use_container_width=True)
    
    elif algorithm == "AutoEncoder":
        # Display reconstruction error
        if 'reconstruction_error' in results.columns:
            fig = px.histogram(
                results,
                x='reconstruction_error',
                color='is_anomaly',
                marginal='box',
                nbins=50,
                title="AutoEncoder Reconstruction Error Distribution",
                labels={"reconstruction_error": "Reconstruction Error", "is_anomaly": "Is Anomaly"},
                color_discrete_map={0: "blue", 1: "red"}
            )
            
            # Add vertical line for threshold
            if 'threshold' in model_info:
                fig.add_vline(
                    x=model_info['threshold'],
                    line_dash="dash",
                    line_color="green",
                    annotation_text="Threshold",
                    annotation_position="top right"
                )
            
            fig.update_layout(
                plot_bgcolor='rgba(30, 39, 46, 0.8)',
                paper_bgcolor='rgba(30, 39, 46, 0)',
                font=dict(color='white'),
                xaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'),
                yaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'),
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Training history if available
            if 'training_history' in model_info:
                history = model_info['training_history']
                history_df = pd.DataFrame({
                    'Epoch': list(range(1, len(history['loss']) + 1)),
                    'Loss': history['loss'],
                    'Val_Loss': history.get('val_loss', [0] * len(history['loss']))
                })
                
                fig_hist = px.line(
                    history_df,
                    x='Epoch',
                    y=['Loss', 'Val_Loss'],
                    title="AutoEncoder Training History",
                    labels={"value": "Loss", "variable": "Metric", "Epoch": "Epoch"}
                )
                
                fig_hist.update_layout(
                    plot_bgcolor='rgba(30, 39, 46, 0.8)',
                    paper_bgcolor='rgba(30, 39, 46, 0)',
                    font=dict(color='white'),
                    xaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'),
                    yaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'),
                    height=400
                )
                
                st.plotly_chart(fig_hist, use_container_width=True)
    
    elif algorithm == "K-Means":
        # Display distance to cluster center
        if 'distance_to_centroid' in results.columns:
            fig = px.histogram(
                results,
                x='distance_to_centroid',
                color='is_anomaly',
                marginal='box',
                nbins=50,
                title="K-Means Distance to Cluster Centroid Distribution",
                labels={"distance_to_centroid": "Distance to Centroid", "is_anomaly": "Is Anomaly"},
                color_discrete_map={0: "blue", 1: "red"}
            )
            
            # Add vertical line for threshold
            if 'threshold' in model_info:
                fig.add_vline(
                    x=model_info['threshold'],
                    line_dash="dash",
                    line_color="green",
                    annotation_text="Threshold",
                    annotation_position="top right"
                )
            
            fig.update_layout(
                plot_bgcolor='rgba(30, 39, 46, 0.8)',
                paper_bgcolor='rgba(30, 39, 46, 0)',
                font=dict(color='white'),
                xaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'),
                yaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'),
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Cluster distribution if available
            if 'cluster_distribution' in model_info:
                cluster_dist = model_info['cluster_distribution']
                cluster_df = pd.DataFrame({
                    'Cluster': list(cluster_dist.keys()),
                    'Count': list(cluster_dist.values())
                })
                
                fig_cluster = px.bar(
                    cluster_df,
                    x='Cluster',
                    y='Count',
                    title="K-Means Cluster Distribution",
                    labels={"Count": "Number of Points", "Cluster": "Cluster ID"}
                )
                
                fig_cluster.update_layout(
                    plot_bgcolor='rgba(30, 39, 46, 0.8)',
                    paper_bgcolor='rgba(30, 39, 46, 0)',
                    font=dict(color='white'),
                    xaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'),
                    yaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'),
                    height=400
                )
                
                st.plotly_chart(fig_cluster, use_container_width=True)
    
    # Cross-algorithm comparison if multiple algorithms have been run
    if 'prev_results' in st.session_state and st.session_state.prev_results:
        st.markdown("### Algorithm Comparison")
        
        # Create comparison metrics dataframe
        comparison_data = []
        
        for alg_name, alg_results in st.session_state.prev_results.items():
            anomaly_count = alg_results['is_anomaly'].sum()
            total_records = len(alg_results)
            anomaly_percent = (anomaly_count / total_records) * 100
            
            comparison_data.append({
                'Algorithm': alg_name,
                'Anomalies Detected': anomaly_count,
                'Anomaly Percentage': anomaly_percent,
                'Execution Time': alg_results.get('execution_time', 0)
            })
        
        comparison_df = pd.DataFrame(comparison_data)
        
        # Display comparison table
        st.dataframe(comparison_df, use_container_width=True)
        
        # Create comparison chart
        fig_comp = px.bar(
            comparison_df,
            x='Algorithm',
            y='Anomaly Percentage',
            title="Anomaly Detection Rate by Algorithm",
            labels={"Anomaly Percentage": "Anomaly %", "Algorithm": "Algorithm"}
        )
        
        fig_comp.update_layout(
            plot_bgcolor='rgba(30, 39, 46, 0.8)',
            paper_bgcolor='rgba(30, 39, 46, 0)',
            font=dict(color='white'),
            xaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'),
            yaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'),
            height=400
        )
        
        st.plotly_chart(fig_comp, use_container_width=True)
    
    # Performance evaluation section
    st.markdown("### Performance Evaluation")
    
    # For real systems, we'd show confusion matrix, ROC curve etc.
    # For demo, we'll show synthetic performance metrics
    
    if 'performance_metrics' in model_info:
        metrics = model_info['performance_metrics']
        perf_df = pd.DataFrame({
            'Metric': list(metrics.keys()),
            'Value': list(metrics.values())
        })
        
        st.dataframe(perf_df, use_container_width=True)
        
        # Display radar chart for multiple metrics
        if len(metrics) >= 3:
            categories = list(metrics.keys())
            values = list(metrics.values())
            
            # Create radar chart
            fig_radar = go.Figure()
            
            fig_radar.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name=algorithm
            ))
            
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 1]
                    )
                ),
                title=f"{algorithm} Performance Metrics",
                plot_bgcolor='rgba(30, 39, 46, 0)',
                paper_bgcolor='rgba(30, 39, 46, 0)',
                font=dict(color='white'),
                height=500
            )
            
            st.plotly_chart(fig_radar, use_container_width=True)
    else:
        st.info("Performance metrics are not available for this model run.")
    
    # Model explanation
    st.markdown("### Model Explanation")
    
    if algorithm == "Isolation Forest":
        st.markdown("""
        **How Isolation Forest Works**
        
        Isolation Forest works on the principle that anomalies are 'few and different', making them easier to isolate
        in feature space compared to normal points.
        
        1. **Isolation Process**: The algorithm randomly selects a feature and a split value to isolate data points.
        2. **Tree Structure**: Multiple isolation trees form a forest, where the path length to isolate a point is measured.
        3. **Anomaly Score**: Points with shorter average path lengths are considered anomalies.
        
        **Key Strengths**:
        - Fast execution even with high-dimensional data
        - Does not require distance or density measures
        - Highly effective at detecting true outliers
        
        **Limitations**:
        - May not perform well if anomalies are clustered
        - Requires tuning of the contamination parameter
        """)
    
    elif algorithm == "AutoEncoder":
        st.markdown("""
        **How AutoEncoder Works**
        
        AutoEncoder is a neural network that learns to compress and reconstruct data. Points that cannot be 
        reconstructed accurately are considered anomalies.
        
        1. **Encoding**: The network compresses the input data into a lower-dimensional space.
        2. **Decoding**: The network attempts to reconstruct the original input from the compressed representation.
        3. **Anomaly Detection**: Points with high reconstruction error are flagged as anomalies.
        
        **Key Strengths**:
        - Can capture complex non-linear patterns
        - Works well with temporal and sequential data
        - Can handle high-dimensional data effectively
        
        **Limitations**:
        - Requires training data with mostly normal instances
        - More computationally intensive
        - May require larger datasets for effective training
        """)
    
    elif algorithm == "K-Means":
        st.markdown("""
        **How K-Means Anomaly Detection Works**
        
        K-Means clustering identifies anomalies by measuring the distance to the nearest cluster center.
        Points far from any cluster center are considered anomalies.
        
        1. **Clustering**: The algorithm groups similar data points into K clusters.
        2. **Distance Calculation**: For each point, the distance to its nearest cluster center is calculated.
        3. **Threshold**: Points with distances exceeding a threshold are flagged as anomalies.
        
        **Key Strengths**:
        - Intuitive and easy to interpret
        - Computationally efficient
        - Works well when normal data forms distinct clusters
        
        **Limitations**:
        - Sensitive to the initial selection of cluster centers
        - Requires specifying the number of clusters in advance
        - May not work well with non-spherical clusters
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("© 2025 Opulent Chikwiramakomo. All rights reserved.")

if __name__ == "__main__":
    main()
