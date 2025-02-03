from graphviz import Digraph
import matplotlib.pyplot as plt

plt.style.use('ggplot')
plt.grid(linestyle='--') 
# plt.style.use('dark_background')

def plot_goals_bar_chart(df):
    # Set up the figure and axis for the bar chart
    fig, ax = plt.subplots(figsize=(10, 6))

    # Set the positions of the bars on the x-axis
    x_pos = range(len(df))

    # Plotting the bars for each category (total_goals, gt_16, lt_16)
    bars_total_goals = ax.bar(x_pos, df['total_goals'], width=0.25, label='Total Goals', align='center')
    ax.bar([p + 0.25 for p in x_pos], df['gt_16'], width=0.25, label='Goals > 16m', align='center')
    ax.bar([p - 0.25 for p in x_pos], df['lt_16'], width=0.25, label='Goals <= 16m', align='center')


    for rect in ax.patches:
        rect.set_width(0.5) 
    
    # Add labels and title
    ax.set_xlabel('Players', fontsize=14)
    ax.set_ylabel('Number of Goals', fontsize=14)
    ax.set_title('Goals Scored by Players', fontsize=16)
    
    # Set the x-ticks with player names
    ax.set_xticks(x_pos)
    ax.set_xticklabels(df['Name'], rotation=45, ha='right', fontsize=12)
    ax.grid(True,color='black', linestyle='--', linewidth=1,alpha=0.2)


    # Add a legend to distinguish between the bars
    ax.legend()

    # Add numbers on top of the 'Total Goals' bars
    for bar in bars_total_goals:
        yval = bar.get_height()  # Get the height of the bar (which is the value)
        ax.text(bar.get_x() + bar.get_width() / 2, yval + 0.2,  # Position the text slightly above the bar
                f'{int(yval)}', ha='center', va='bottom', fontsize=12)

    # Display the plot
    plt.tight_layout()  # To make sure everything fits without overlap
    plt.show()



def generate_mongo_erd(collections_info, dpi=300):
    dot = Digraph(comment='MongoDB ERD', engine='dot')

    # Set graph background to dark blue and node box color to blue
    dot.attr(bgcolor='#001f3d', color='#FFFFFF')  # Dark blue background
    dot.attr('node', style='filled', fillcolor='#007acc', fontcolor='#000000', shape='box', width='1.2', fontsize='16', fontname='Helvetica')  # Increased fontsize
    dot.attr('edge', color='#FFFFFF', fontcolor='#FFFFFF')  # White cardinality labels

    # Set DPI for PNG rendering (300 DPI)
    dot.attr(dpi=str(dpi))

    # Iterate over the collections and add them to the ERD as nodes
    for collection_name, df in collections_info.items():
        # Create a formatted label with table name on top and columns listed below
        table_name_label = f"___{collection_name}___"  # Bold table name
        columns = "\n".join(df.columns)  # List the columns underneath
        label = f"{table_name_label}\n{columns}"
        
        # Add the node to the graph
        dot.node(collection_name, label=label)

    # Identify relationships (references) and add edges to ERD with cardinality and customized colors
    for collection_name, df in collections_info.items():
        references = find_references(collection_name, df)
        for ref in references:
            ref_collection = ref.split("_")[0]  # Assumes reference naming convention like `team_id`, `player_id`
            
            # Cardinality representation (adjust based on your logic)
            cardinality = '1..*'  # Default cardinality, you can change this depending on your data model
            if 'team' in ref_collection:
                cardinality = '1..*'  # One team can have many shots
                arrow_style = 'forked'  # One to many (forked)
            elif 'player' in ref_collection:
                cardinality = '1..1'  # One player is linked to exactly one match (one to one)
                arrow_style = '->'  # One to one (single directed arrow)
            else:
                cardinality = '*..*'  # Many to many relationship
                arrow_style = '--'  # Many to many (undirected)

            # Add edge with cardinality label, set direction and arrow style
            dot.edge(collection_name, ref_collection, label=f"{cardinality}", dir='both', arrowhead=arrow_style, arrowtail=arrow_style, len='2.5')

    return dot

# Helper function to identify references
def find_references(collection_name, df):
    references = []
    for column in df.columns:
        # Example logic for detecting references based on column name conventions
        if '_' in column:
            references.append(column)
    return references
