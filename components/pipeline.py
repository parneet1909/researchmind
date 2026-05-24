import streamlit as st


def render_pipeline(
    pipeline_placeholder,
    active_step=None,
    completed_steps=None
):

    if completed_steps is None:

        completed_steps = []

    steps = [
        ("search", "🔍 Search Agent"),
        ("reader", "📄 Reader Agent"),
        ("writer", "✍️ Writer Chain"),
        ("critic", "🧐 Critic Chain")
    ]

    html = ""

    for key, label in steps:

        if key == active_step:

            status = "🟡 RUNNING"

            css = "running"

        elif key in completed_steps:

            status = "🟢 COMPLETED"

            css = "done"

        else:

            status = "⚪ WAITING"

            css = "waiting"

        html += f"""
        <div class="pipeline-card {css}">
            {label}
            <div style="float:right;">
                {status}
            </div>
        </div>
        """

    pipeline_placeholder.markdown(
        html,
        unsafe_allow_html=True
    )