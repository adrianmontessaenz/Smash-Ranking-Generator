# Smash-Ranking-Generator
[![Status](https://img.shields.io/badge/status-in%20progress-yellow)](#)
[![Language](https://img.shields.io/badge/language-Python-blue?logo=python)](https://www.python.org/)
[![Python](https://img.shields.io/badge/python-3.12-blue?logo=python)](https://www.python.org/)
[![GUI](https://img.shields.io/badge/GUI-CustomTkinter-green)](https://github.com/TomSchimansky/CustomTkinter)
[![API](https://img.shields.io/badge/API-start.gg-red)](https://www.start.gg/)

Start.gg Tournament Ranking Generator is a desktop application that automates the creation of competitive player rankings using tournament data retrieved directly from Start.gg. Tournament results are processed through a customizable scoring system that takes into account tournament size, tier, player placements and notable player attendance to generate accurate and transparent rankings.

The tool was created to eliminate manual spreadsheet work and provide tournament organizers with a flexible way to build ranking systems tailored to their local or regional competitive scenes.

## **Features**
* Retrieve tournament data directly from Start.gg using the GraphQL API.
* Generate player rankings automatically from tournament results.
* Support for custom tournament tier classifications.
* Configurable scoring system based on tournament size, placement and event tier.
* Additional tournament weighting based on the attendance of notable players.
* Interactive desktop interface built with CustomTkinter.
* Saving datasheets of the rankings on excel files using pandas.

## **Challenges of the project**
* Designing a ranking algorithm capable of rewarding both strong tournament performances and long-term consistency. Balancing tournament size, event tiers, player placements and notable player attendance required multiple iterations to avoid rankings that favored either excessive participation or isolated high-performing results.
* Determining the relative importance of each tournament taking into count factors such as entrant count, event tier and the presence of highly ranked players.
* Retrieving tournament information from Start.gg, handling different data structures, pagination and event-specific information to consistently extract the required ranking data.
* Supporting customizable tournament tiers, scoring parameters and player weighting systems without requiring code changes for every ranking update.
* Designing a desktop interface that remained intuitive while exposing a large number of configuration options
