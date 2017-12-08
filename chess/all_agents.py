from chess import agents, value_network_agent, mcts

agent_list = {
    'PieceValueAgent': agents.SampleMinimaxAgent,
    'ValueNetworkAgent': value_network_agent.ValueNetworkAgent,
    'RandomAgent': mcts.RandomMoveAgent,
    'RandomPlayoutAgent': mcts.RandomPlayoutAgent
}
