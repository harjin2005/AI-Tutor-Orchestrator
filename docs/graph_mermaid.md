# LangGraph StateGraph Visualization

## Architecture Diagram

```mermaid
%%{init: {'flowchart': {'curve': 'linear'}}}%%
graph TD;
	__start__([<p>__start__</p>]):::first
	__end__([<p>__end__</p>]):::last
	classifier(classifier)
	groq_agent(groq_agent)
	openrouter_agent(openrouter_agent)
	__start__ --> classifier;
	groq_agent --> __end__;
	openrouter_agent --> __end__;
	classifier -. &nbsp;academic&nbsp; .-> groq_agent;
	classifier -. &nbsp;coding&nbsp; .-> openrouter_agent;
	classDef default fill:#f2f0ff,line-height:1.2
	classDef first fill-opacity:0
	classDef last fill:#bfb6fc

```

## How to View

1. Copy the mermaid code above
2. Go to: https://mermaid.live
3. Paste and view the interactive diagram

## Graph Description

- START: Entry point for all queries
- Classifier Node: Analyzes query type
- Groq Agent Node: Processes academic queries
- OpenRouter Agent Node: Processes coding queries
- END: Exit point after processing
