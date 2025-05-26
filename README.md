# README for RadiantGraph take home

## README scope
This document is meant to answer all explicit questions
asked in the original take home test spec, the other README
(README-Docker.md) outlines specifics about running the project
through docker.

## Things of note
I largely used this opportunity to mess around with fastapi + sqlalchemy,
a combo I've been meaning to learn for some time. Despite mostly using
Django for these kinds of projects (or node) I'm fairly familiar with sqlalchemy
but not so much with fastapi. I know that you guys use it at radiantgraph
and was eager to learn the ins and outs of it here.

## Running the project
Just run `docker compose up --build` in a terminal. The
README-Docker.md outlines in much more detail how to run
this project + info about the docker setup

## Functional Examples

To see the logic here in action the ideal way would be 
to either run some of the unit tests or to use something
like curl or postman.

For example, you can do something like

`curl -X GET "http://localhost:8000/analytics/orders-by-billing-zip" \
       -H "accept: application/json"`

to hit the orders by billing zip endpoint, which would
return something like

` [
    {
      "zip_code": "12345",
      "order_count": 4
    },
    {
      "zip_code": "54321",
      "order_count": 1
    }
  ]`

## AI/LLM usage
Given how little-ish time I had to work on this (memorial day 
weekend visiting family, in a food coma, and other excuses
I can come up with) I leaned more into llm's than I usually do.
Specifically the following were mostly done through claude:
- docker related files
- most of the unit tests
- the initial boilerplate of fastapi + sqlalchemy

Besides those "tertiary" things, the main selling points of this,
namely the
- data model
- code layout, ie splitting between rest_api and services, etc
were done manually by me.

## If I had more time/what to add or improve
Ideally I like to lay out my code so that services act as a kind of interface
or coordinator that execute on business logic without defining the nitty gritty
of how to actually acheive that. I didn't have the time to do that here.

Oh also I realize a lot of this isn't async like fastapi wants, I'm still coming
from the django/flask world of spinning up a thread for each request. If I had more
time I'd go through and ensure async is achieved to make sure performance is optimal.
The biggest hurdle there would be to make sure the psql driver is properly async, something
I recall being an issue last time I tried something similar.


