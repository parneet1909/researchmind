import streamlit as st
def render_results(results):

    if not results:
        return

    st.markdown("---")
    st.markdown(
        "## 📝 Final Results"
    )

    # SEARCH RESULTS

    if "search" in results:

        with st.expander(
            "🔍 Search Results"
        ):

            st.write(
                results["search"]
            )

    # READER OUTPUT

    if "reader" in results:

        with st.expander(
            "📄 Reader Output"
        ):

            st.write(
                results["reader"]
            )

    # FINAL REPORT

    if "writer" in results:

        st.markdown(
            "### 📝 Final Research Report"
        )

        st.markdown(
            results["writer"]
        )

        st.download_button(
            label="⬇ Download Report",
            data=results["writer"],
            file_name="research_report.md",
            mime="text/markdown"
        )

    # CRITIC FEEDBACK

    if "critic" in results:

        st.markdown(
            "### 🧐 Critic Feedback"
        )

        st.markdown(
            results["critic"]
        )