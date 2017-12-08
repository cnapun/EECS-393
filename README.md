# EECS-393
Class project for EECS 393

## About
Our chess game is a fully functional chess game that implements all the basic rules and features of chess. It has an HTML UI, meaning that this game can be started and played on your browser. It provides a platform for you to design your own AI agent and later play against.

### Tools: 
Javascript and HTML were used for the frontend. For the backend, we coded in Python and used both Flask (server) and Numpy (calculations). For version control and bug tracking, we used Github. 
 
### Future Improvements: 
We want to write the core movement functionality in C/C++. We can do this because we don't use many python libraries/tools and thus can translate it easier to C/C++ later on. Because of our bitboard representation, we can also use various bithacks to improve the speed of our software. In addition to this, we would like to improve our AI (minimax with alpha-beta pruning), which does not look many moves ahead or prioritize positional advantage. We would also like to support multi device gameplay, as the two users would currently have to be on the same computer to play chess against each other as well as being able to load a state based on an imported move list.   


## Usage
### Prerequisites
This has been most thoroughly tested on macOS 10.13.1 using Python 3.6.3. We used NumPy 1.13.3 for computations, but any recent version should work
### How to Run
Add the directories `EECS-393/` and `EECS-393/chess/` to the `PYTHONPATH` environment variable.
To start a server, run `python3 chess/server.py $AGENT_NAME`. 
If there are any arguments that must be passed to the agent in the constructor, they should be specified as --kwarg key=value, but value will be a str.
If the agent is a subclass of a SavingAgent, then the argument `--savefile $FILENAME` or `-f $FILENAME`, where `$FILENAME` is the value to be passed into the `from_file` function

To access the UI, run it using some server (for example, `python3 -m http.server`) and navigate to the appropriate address for `interface.html` in the browser.
We have not tested this without serving, but it is possible it would work anyways (i.e. just open the file `interface.html` in the browser at `file:///...`)
### Custom Agents
All custom agents must extend the `Agent` class. The only method that must be implemented is `select_move`. 
To add a custom agent to the list of agents, add it to `agent_list` in `all_agents.py`, with the name to be used when running `server.py`.
If the custom agent extends `SavingAgent`, then it must implement a `from_file` function. 
This could be used in the case of an agent where the policy is learned by a neural network, where the weights would be saved and loaded back when running `server.py`.
`LearningAgent` is a type of `SavingAgent`, but it adds some basic functionality for training RL agents using policy gradient methods.
The final major type of agent is a `MinimaxAgent`, which has a Minimax search with alpha-beta pruning implemented, and only requires a property of `max_depth`, the deepest the algorithm should search, and a method `heuristic`, which takes a state and returns the heuristic for the node.
Several sample agents include a random playout agent, which plays many random games, and chooses whichever maximizes the expected outcome, and a random move agent, which simply chooses a random move.
The last agents implemented are the `SampleMinimaxAgent`, which uses a heuristic based on piece value, and `ValueNetworkAgent`, which tries to learn the probability of winning from a given state
