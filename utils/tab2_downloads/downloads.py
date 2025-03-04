import streamlit as st
from utils.data_processing import process_datasets  # Import directly

def display_download_options():
    """Displays download options for complete and filtered datasets in Streamlit."""
    
    st.title("Download Options")
    
    if "df" in st.session_state and st.session_state.df is not None:
        # Process the datasets
        processed_dfs = process_datasets(st.session_state.df)
        
        # --- Complete Dataset Download ---
        st.header("Complete Dataset")
        st.download_button(
            "Download Complete Dataset (CSV)",
            st.session_state.df.to_csv(index=False),
            "complete_guidelines_dataset.csv",
            "text/csv"
        )
        st.markdown("---")  # Horizontal separator
        
        # --- Filtered Datasets Download ---
        for name, filtered_df in processed_dfs.items():
            # Count the number of guidelines that have a non-empty Citation Code for platform-specific guidelines.
            filtered_guidelines_count = len(filtered_df)
            
            st.subheader(name)
            st.caption(f"Contains {filtered_guidelines_count} guidelines")
            st.download_button(
                f"Download {name} (CSV)",
                filtered_df.to_csv(index=False),
                f"{name.lower().replace(' ', '_')}.csv",
                "text/csv"
            )
            st.markdown("---")  # Separator between each filtered dataset download option
    else:
        st.info("Please upload a CSV file first to enable downloads.")
