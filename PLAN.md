**Role**

You are an expert AI Engineer specializing in Generative AI, AI coding agents, Kubernetes, cloud-native systems, and evaluation methodologies.

## Background

Every GitHub repository in this evaluation contains a baseline `CLAUDE.md` file that provides instructions and context for AI coding agents.

Developers have added **agentic documentation** (e.g., architecture guides, workflows, coding standards, operational runbooks, troubleshooting guides, task-specific documentation, and repository knowledge) to further improve agent performance.

The objective is **not** to compare repositories with and without `CLAUDE.md`. Instead, the goal is to measure the **incremental effectiveness** of the additional agentic documentation beyond the baseline `CLAUDE.md`.

## Available Tools

You have access to the following tools:

- **MLflow** for experiment tracking, metric logging, artifact management, and result comparison. Installed locally.
- **agent-eval-harness** [[https://github.com/opendatahub-io/agent-eval-harness]](https://github.com/opendatahub-io/agent-eval-harness]) for defining, executing, and automating benchmark tasks across repositories. 
- **Agentic Docs Generator Claude Plugin** [[https://github.com/openshift-eng/ai-helpers]](https://github.com/openshift-eng/ai-helpers]) for generating, organizing, and validating agentic documentation.

Leverage these tools wherever appropriate when designing the evaluation methodology.

## Available Repositories

You have access to the following repositories:

- **cert-manager-operator** [https://github.com/openshift/cert-manager-operator](https://github.com/openshift/cert-manager-operator)
- **multiarch-tuning-operator** [https://github.com/outrigger-project/multiarch-tuning-operator](https://github.com/outrigger-project/multiarch-tuning-operator)



## Objective

Design a rigorous, reproducible evaluation framework that measures whether the additional agentic documentation improves AI coding agent performance on real-world Kubernetes and cloud-native software engineering tasks.

The framework should isolate the impact of the added documentation while controlling for all other variables.

## Evaluation Questions

Your evaluation should answer questions including:

- Does the additional agentic documentation improve task success rates?
- Does it reduce the number of agent iterations?
- Does it reduce repository exploration and context discovery effort?
- Does it improve code correctness?
- Does it improve adherence to repository conventions?
- Does it reduce hallucinations and incorrect assumptions?
- Which categories of agentic documentation provide the greatest benefit?
- Under what repository characteristics does the documentation provide the largest gains?



## Experimental Design

For every repository, evaluate two conditions.

### Baseline

Agent has access to:

- Repository
- Default `CLAUDE.md`



### Treatment

Agent has access to:

- Repository
- Default `CLAUDE.md`
- All additional agentic documentation

All other variables must remain identical, including:

- AI model
- Prompt
- Tool access
- MCP servers
- Context window
- Temperature
- Agent configuration
- Evaluation tasks



## Design the Evaluation

Produce a complete evaluation plan covering:

### 1. Evaluation Objectives

Define measurable indicators of incremental improvement over the `CLAUDE.md` baseline.

### 2. Benchmark Task Suite

Include representative Kubernetes development tasks such as:

- Bug fixes
- Feature implementation
- Refactoring
- Writing tests
- Kubernetes manifest updates
- CI/CD changes
- Debugging failures
- Documentation updates
- Repository exploration
- Cross-package modifications
- Dependency upgrades

Design tasks with varying complexity and repository coverage.

### 3. Evaluation Metrics

Include quantitative and qualitative metrics such as:

- Task success rate
- Code correctness
- Build success
- Test pass rate
- Human review score
- Time to completion
- Number of agent iterations
- Token consumption
- Tool invocation efficiency
- Repository navigation efficiency
- Context retrieval accuracy
- Repository convention adherence
- Hallucination rate
- Recovery from failed attempts

Clearly justify why each metric is important.

### 4. Documentation Impact Analysis

Design methods to determine:

- Which documents the agent actually used
- Which documents influenced decisions
- Which documentation categories contributed most
- Whether some documentation was redundant
- Whether documentation reduced unnecessary code exploration
- Documentation ROI (benefit vs. maintenance cost)



### 5. Tool Integration

Describe how each available tool should be used.

#### MLflow

Define:

- Experiment structure
- Runs
- Parameters
- Metrics
- Logged artifacts
- Result dashboards
- Cross-repository comparisons



#### agent-eval-harness

Describe:

- Benchmark organization
- Task definitions
- Automated execution
- Repeated runs
- Regression testing
- Result collection



#### Agentic Docs Generator Claude Plugin

Describe:

- How to validate generated documentation
- How to generate documentation variants for ablation studies
- How to evaluate documentation quality
- How to compare generated documentation against manually authored documentation



### 6. Ablation Studies

Design experiments including:

- `CLAUDE.md` only
- `CLAUDE.md` + all agentic documentation
- `CLAUDE.md` + selected documentation categories
- Removal of individual documentation types
- Generated vs manually authored documentation



### 7. Statistical Analysis

Define:

- Sample sizes
- Number of repeated runs
- Confidence intervals
- Statistical significance tests
- Effect size calculations
- Cross-repository aggregation methodology



### 8. Scoring Framework

Develop an overall effectiveness score that quantifies the incremental value of the additional agentic documentation relative to the baseline.

The scoring framework should combine multiple metrics into a single reproducible score while preserving metric-level insights.

### 9. Threats to Validity

Discuss potential confounding factors, including:

- Repository complexity
- Documentation quality
- Model stochasticity
- Prompt sensitivity
- Task selection bias
- Overlap between `CLAUDE.md` and the additional documentation
- Repository familiarity
- Information leakage



## Deliverables

Produce:

1. A research-grade evaluation methodology.
2. A benchmark task specification.
3. An experiment execution plan using MLflow and agent-eval-harness.
4. A documentation impact analysis framework.
5. A scoring rubric.
6. A statistical analysis plan.
7. Recommendations for automating the evaluation across multiple Kubernetes repositories.
8. Recommendations for visualizing and reporting results.



## Output Requirements

- Structure the response as an engineering design document suitable for implementation.
- Emphasize reproducibility, fairness, automation, and statistical rigor.
- Focus on measuring the **incremental impact** of the additional agentic documentation beyond the default `CLAUDE.md`.
- Include concrete implementation guidance wherever possible, referencing the available tools (MLflow, agent-eval-harness, and the Agentic Docs Generator Claude Plugin) rather than providing only high-level recommendations.

