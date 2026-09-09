# Master It By Doing

An adaptive AI learning platform that turns learning goals into hands-on missions, evaluates real learner work, and dynamically adapts the learning path toward mastery.

## Core Loop

**GOAL → ASSESS → MISSION → DO → EVALUATE → ADAPT → MASTER**

## Vision

Master It By Doing is an action-first learning platform designed to move learners beyond passive instruction.

Instead of simply explaining concepts, the system gives learners practical missions, evaluates what learners actually build, identifies demonstrated and missing skills, and adapts the next challenge toward mastery.

## Technology

- Amazon Alexa+
- Model Context Protocol (MCP)
- Amazon Bedrock
- AWS Bedrock AgentCore
- Strands Agents
- Python
- React
- FastAPI

## Current Capabilities

- Goal-driven learning missions
- Adaptive mission progression
- Real learner code evaluation
- Deterministic Python validation
- AI-assisted assessment with Amazon Bedrock
- Ground Truth validation for objective criteria
- Evidence-based scoring
- Adaptive follow-up challenges
- Automated assessment tests

## Assessment Architecture

The evaluation pipeline separates AI reasoning from authoritative validation:

**Learner Submission → Python Validation → Bedrock Evaluation → Ground Truth → Score → Adaptation**

This prevents the AI evaluator from overriding deterministic evidence when objective validation is available.

## Example Learning Flow

A learner working through a Python mission can progress from:

**Build a Number Guessing Game**

to:

**Build a Command-Line Quiz**

based on demonstrated mastery.

The system evaluates the learner's actual submission rather than relying solely on self-reported completion.

## Project Status

Active development.

The current implementation includes a working adaptive learning vertical slice with automated assessment and regression testing.

## Testing

The current test suite passes:

**19 tests passed**

## Vision

**Learn by doing. Prove your skills. Adapt. Master.**
