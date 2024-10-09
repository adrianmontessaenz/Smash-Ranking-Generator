# Import libraries
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
import json
import sys

# Function to fetch tournament data and store it in a JSON file
def fetch_and_store_tournament_data(slug):
    # Set up the GraphQL client
    transport = RequestsHTTPTransport(
        url="https://api.start.gg/gql/alpha",
        headers={"Authorization": "Bearer dc6a93f91afd04e48bb932193e03882e"},  # Replace with your actual API token
        use_json=True,
    )
    client = Client(transport=transport, fetch_schema_from_transport=True)

    # Query with entrants
    query = gql("""
    query getEventData($slug: String) {
      tournament(slug: $slug) {
        events(filter:{slug:"singles-bracket"})
        {
          id
        	entrants(query:{})
        	{
          	pageInfo {
            	total
          	}
        	}
        }
      }
    }
    """)

    # Get entrants to retrieve all placements
    entrants_data = client.execute(query, variable_values={"slug": slug})
    total_entrants = entrants_data['tournament']['events'][0]['entrants']['pageInfo']['total']
    event_id = entrants_data['tournament']['events'][0]['id']

    # Query to get standings
    standings_query = gql("""
    query getStandings($slug: String!, $perPage: Int!) {
      tournament(slug: $slug) {
        name
        events(filter: {slug: "singles-bracket"}) {
          entrants(query:{})  {
          	pageInfo {
            	total
          	}
        	}
          standings(query: { perPage: $perPage, page: 1 }) {
            nodes{
              placement
              entrant
              {
                id
                paginatedSets
                {
                	nodes
                  {
                    displayScore
                    winnerId
                  }
                }
              }
              player
              {
                gamerTag
              }
            }
          }
        }
      }
    }
    """)
    
    # Get placements and join jsons
    final_data = client.execute(standings_query, variable_values={"slug": slug, "perPage": total_entrants})

    # Save data to a JSON file
    with open('tournament_data.json', 'w') as json_file:
        json.dump(final_data, json_file, indent=4)

    print("Tournament data has been fetched and stored in tournament_data.json")

def fetch_tournament(slug):
    fetch_and_store_tournament_data(slug)

if __name__ == "__main__":
    # Check if a slug was provided as a command-line argument
    if len(sys.argv) != 2:
        print("Usage: python app.py <tournament_slug>")
        sys.exit(1)

    tournament_slug = sys.argv[1]
    fetch_and_store_tournament_data(tournament_slug)

