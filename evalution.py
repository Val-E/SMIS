import plotly.graph_objects as go
import networkx as nx
import numpy as np

from database.models import User, Following, session

from collections import Counter

from settings import ROOT_PROFILES


# get user_handles of root profiles
root_profiles = [profile[0] for profile in ROOT_PROFILES]


def load_entries() -> tuple[set, set]:
    """load list with the users and who they follow"""
    # initialse datastructions
    nodes: set = {}
    edges: set = {}

    # search through database
    edges: set = set(session.query(Following.followed_user, Following.following_user).all())

    # set with user handles
    for edge in edges:
        nodes = set(nodes) | {edge[0], edge[1]}

    return nodes, edges


def create_edges(graph: nx.Graph) -> tuple[np.array, np.array, np.array, np.array]:
    """create array with positions of edges and nodes"""
    # initialse datastructions
    edge_x: np.array = np.array([])
    edge_y: np.array = np.array([])
    node_x: np.array = np.array([])
    node_y: np.array = np.array([])
    
    # distribute nodes using Fruchterman-Reingold force-directed algorithm
    positions = nx.spring_layout(graph)

    # collect edge positions
    for edge in graph.edges():
        x0, y0 = positions[edge[0]]
        x1, y1 = positions[edge[1]]

        edge_x = np.append(edge_x, x0)
        edge_x = np.append(edge_x, x1)
        edge_x = np.append(edge_x, None)
        edge_y = np.append(edge_y, y0)
        edge_y = np.append(edge_y, y1)
        edge_y = np.append(edge_y, None)

    # collect node positions
    for node in graph.nodes():
        x, y = positions[node]
        node_x = np.append(node_x, x)
        node_y = np.append(node_y, y)

    return node_x, node_y, edge_x, edge_y


def get_node_information(graph: nx.Graph) -> tuple[np.array, np.array, np.array]:
    """add node and user information from database to node text"""
    # initialse datastructions
    node_adjacencies: np.array = np.array([])
    node_text: np.array = np.array([])
    node_border: np.array = np.array([])

    # collect node information
    for node, adjacencies in enumerate(graph.adjacency()):
        border_color: str = "orange"

        # count connections
        node_adjacencies = np.append(node_adjacencies, len(adjacencies[1]))

        # search for user biography and jame
        user: User = session.query(User).filter(User.user_handle==adjacencies[0]).first()
        if user:
            profile: str = f"<b>Username:</b> <br />{user.username} <br /><br />" \
                            "<b>Biography:</b> <br />" + user.biography.replace("\n", "<br />") + "<br /><br />" \
                           f"<b>Age:</b> {user.age if user.age else 'no information'} <br />" \
                           f"<b>Sex:</b> {user.sex} <br />" \
                           f"<b>City:</b> {user.cities} <br />" \
                           f"<b>Nationalities:</b> {user.nationalities} <br />" \
                           f"<b>Sexual Orientations:</b> {user.sexual_orientations} <br />" \
                           f"<b>Political Classifications:</b> {user.political_classifications} <br />"

            # red border for root profiles
            if user.user_handle in root_profiles:
                border_color = "red"
            
        else:
            # black border for edge profiles
            border_color = "black"
            profile = "Edge of the bubble, no profile records <br /><br />"

        # create node description
        node_text = np.append(node_text, f"{profile}<b>Connections:</b> {len(adjacencies[1])}")
        node_border = np.append(node_border, border_color)

    return node_adjacencies, node_text, node_border


def get_stats() -> str:
    """calculate statistical information about users"""
    # initialse datastructions
    array: np.array = np.array([])
    array_size: int = 0
    stats: str = ""

    # load entries containing numeric information
    for numeric_attribut in ["age"]:
        array = np.array([])
        array = np.append(
            array, 
            [
                value for value in session
                    .query(getattr(User,numeric_attribut))
                    .filter(getattr(User, numeric_attribut)!=None)
                    .all()
            ]
        )
        stats += f"<b>{numeric_attribut.title()}:</b> <br />" \
            f"Mean: {round(np.mean(array), 3)}, " \
            f"Median: {np.median(array)}, " \
            f"Variance: {round(np.var(array), 3)}, " \
            f"Sample Size: {np.size(array)} <br />"

    # load entries containing text information
    for text_attribute in ["sex", "cities", "nationalities", "sexual_orientations", "political_classifications"]:
        array = np.array([], dtype=object)

        data: list = session \
            .query(getattr(User, text_attribute)) \
            .filter(getattr(User, text_attribute)!=None) \
            .all()
            
        # format data
        for value in data:
            subdata: list = str(*value).split(";")

            for subvalue in subdata:
                array = np.append(
                    array,
                    subvalue.strip().title()
                )

        array_size = np.size(array)
        stats += f"<b>{text_attribute.title()}:</b> <br />"

        for attribute, counter in Counter(array).items():
            stats += f"{attribute}: {round(counter/array_size * 100, 3)}% ({counter}), <br />"
        
        stats += f"Sample Size: {array_size} <br />"

    return stats


def main():
    """main function"""
    # initialse graph object
    G = nx.Graph()

    # add nodes and edges
    nodes, edges = load_entries()

    G.add_nodes_from(nodes)
    G.add_edges_from(edges)

    # get coordinates from graph
    node_x, node_y, edge_x, edge_y = create_edges(G)

    # draw nodes
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode="markers",
        hoverinfo="text",
        marker=dict(
            showscale=True,
            colorscale="YlGnBu",
            reversescale=True,
            size=11,
            colorbar=dict(
                thickness=20,
                title="Number of Connections",
                xanchor="left",
                titleside="right"
            ),
            line_width=3,
        )
    )

    # draw edges
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color="grey"),
        hoverinfo="none",
        mode="lines"
    )


    # add addition information
    node_trace["marker"]["color"], node_trace["text"], node_trace["marker"]["line"]["color"] = get_node_information(G)

    stats = get_stats()

    # generate figure
    fig = go.Figure(data=[edge_trace, node_trace],
        layout=go.Layout(
            title="Social Bubble of " + str(root_profiles)[1:-1],
            titlefont_size=16,
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20,l=5,r=5,t=40),
            annotations=[dict(
                text="<b>Statistics</b><br />" + 
                    stats + 
                    "<br /><br /><a href='https://github.com/Val-E/SMIS'>Download Project</a>" + 
                    "<br /><br />Provided by Val-E",
                showarrow=False,
                xref="paper", 
                yref="paper",
                x=0, y=0
            )],
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
    )

    fig.show()


if __name__ == "__main__":
    main()
    
