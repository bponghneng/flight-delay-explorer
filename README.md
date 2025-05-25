# Flight Delay Explorer
A command-line tool that ingests airline on-time performance CSVs like the Bureau of Transportation Statistics (DOT) “On-Time Performance” dataset. It processes them and outputs summary reports, like average delays by airline or airport, monthly trends and histograms of delay distributions.

## Background

I started this as part of a series of personal projects to retool my software engineering skills for the agentic engineering age. Here's the prompt I fed into ChatGPT to get started:

> I'm a staff engineer who works at a scaling fintech company. I want to advance my professional skills in some specific areas with a personal programming project. Three skills areas are important for me to learn:
>
> - Python
> - CQRS and event sourcing
> - AI engineering
>
> Can you recommend simple projects I can build as a way to develop skills in these areas?

I got back a list of projects, with three focusing on one of the skills I was interested in and a final one that integrated all three. All of them were perfectly reasonable and well matched to my intention. But they were also perfectly predictable: an expense tracker, a bank microservice, a chatbot for a document collection. So I prompted for something more interesting.

> I like your idea of building one project for each area and then building one that integrates the three. As for a category of application, can you recommend similar projects but in the area of commercial aviation? One idea is using historic airport and airline arrival and departure data to build a point-to-point routing application.

ChatGPT came back with a similar list of projects that was just what I was looking for:

1. Python: Flight Delay Explorer CLI
2. CQRS & Event Sourcing: Flight Status Service
3. AI Engineering: Flight Route Recommendation Chatbot 
4. Capstone: Intelligent Flight Planner

## Work-in-Progress

This version of the README marks the beginning state of the project. My intention is to build all of the projects using techniques of agentic engineering I have studied in recent months. No doubt I _could_ one-shot vibe code all of the projects using Claude with only a couple more prompts to refine the specs for each. But I want skills that work for my day-to-day use among an enterprise-level codebase with legacy code, tech debt and high sensitivity to breaking changes.