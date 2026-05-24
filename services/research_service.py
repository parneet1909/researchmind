from concurrent.futures import (
    ThreadPoolExecutor
)

from agents import (
    build_reader_agent,
    build_search_agent,
    writer_chain,
    critic_chain
)


def run_research_pipeline(
    topic,
    render_pipeline
):

    results = {}

    # SEARCH + READER

    render_pipeline(
        active_step="search",
        completed_steps=[]
    )

    search_agent = build_search_agent()

    reader_agent = build_reader_agent()

    with ThreadPoolExecutor() as executor:

        future_search = executor.submit(
            search_agent.invoke,
            {
                "input":
                f"Find recent detailed information about {topic}"
            }
        )

        future_reader = executor.submit(
            reader_agent.invoke,
            {
                "input": f"""
                Analyze recent trends, insights,
                developments and statistics about:

                {topic}
                """
            }
        )

        search_response = future_search.result()

        render_pipeline(
            active_step="reader",
            completed_steps=["search"]
        )

        reader_response = (
            future_reader.result()
        )

    search_result = str(search_response)
    reader_result = str(reader_response)

    results["search"] = search_result

    results["reader"] = reader_result

    render_pipeline(
        active_step=None,
        completed_steps=["search", "reader"]
    )

    # WRITER

    render_pipeline(
        active_step="writer",
        completed_steps=["search", "reader"]
    )

    combined_research = f"""
    SEARCH RESULTS:
    {search_result}

    SCRAPED CONTENT:
    {reader_result}
    """

    writer_result = writer_chain.invoke({
        "topic": topic,
        "research": combined_research
    })

    results["writer"] = writer_result

    render_pipeline(
        active_step=None,
        completed_steps=[
            "search",
            "reader",
            "writer"
        ]
    )

    # CRITIC

    render_pipeline(
        active_step="critic",
        completed_steps=[
            "search",
            "reader",
            "writer"
        ]
    )

    critic_result = critic_chain.invoke({
        "report": writer_result
    })

    results["critic"] = critic_result

    render_pipeline(
        active_step=None,
        completed_steps=[
            "search",
            "reader",
            "writer",
            "critic"
        ]
    )

    return results