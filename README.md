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

## **Current Ranking Formula**

### **Tournament Value**

* Each tournament starts with a base value of **5 points per entrant**.
* Additional value is granted for the presence of ranked players. The sum of all ranked-player bonuses is scaled using a **0.6 exponent** to provide diminishing returns, preventing stacked tournaments from becoming disproportionately valuable.
* The resulting tournament value is multiplied by the manually assigned **tier multiplier** (A, B, C, etc.).

### **Tournament Performance**

* A player's tournament score is determined by their placement using a placement curve with exponent **k = 1.7**, rewarding higher placements more heavily.
* Additional placement bonuses are awarded to podium finishes (1st, 2nd and 3rd place).

### **Season Score**

* For each player, only their **four best tournament performances** are considered.
* These performances are weighted using **[0.4, 0.3, 0.2, 0.1]**.
* If a player has fewer than four tournaments, the weights are normalized so that the available results receive proportionally higher weight.

### **Head-to-Head Bonus**

* Every win contributes additional value based on the final score of the defeated player.
* The total head-to-head score is accumulated across the season and added as a bonus to the player's overall score.

### **Final Ranking**

* The final ranking score is obtained by combining:

  * Tournament performance score
  * Head-to-head bonus
* Results are exported to an Excel workbook containing the final ranking and several debug sheets with tournament placements and head-to-head data.

### **Design Goals**

The ranking aims to reward:

* Strong placements at valuable tournaments.
* Consistency across the season.
* Wins against high-performing players.
* Participation without turning the ranking into an attendance contest.


## **Development Environment**
A Docker image is provided to ensure the project can be developed and tested against a consistent Python 3.12 environment regardless of the host operating system.
To use it, run the following commands:

```bash
docker build -t smash-ranking-generator .
docker run --rm smash-ranking-generator
```
