from agents import Agent
import pyCardDeck
import util
import random
class StateRepresentation:
    """
    Interface for making state representations

    Done so that states representations for QLearning Agents can be swapped in and out easily for comparing results

    Need to be able to:

    create_state_rep_from_state:
        take in a game class and create a tuple that can be used to represent the state in a Q table

    create_state_rep_from_state:
        use stored state information in order to create a state representation later
        needs to create an identical state that create state_rep_from_state uses
    save state:
        Take in a state, save the important details to be used later
    """

    def __init__(self, **kwargs):
        self.last_board = None
        self.last_action = None
        self.last_reward = 0

    def save_state(self, state):
        raise NotImplementedError

    def create_state_rep_from_self(self, action):
        raise NotImplementedError

    def create_state_rep_from_state(self, state, action):
        raise NotImplementedError

    """def get_lead_card(self, state):
        max_card = state.board[0]
        max_val = Agent.convert_card_rank_to_int(max_card)
        lead_suit = state.board[0]
        for card_index in state.board:
            card = state.board[card_index]
            if card.suit == lead_suit and Agent.convert_card_rank_to_int(card) > max_val:
                max_card = card
                max_val = Agent.convert_card_rank_to_int(card)
            elif card.suit == "Spades" and (lead_suit != "Spades" or card.rank > max_val):
                max_card = card
                max_val = Agent.convert_card_rank_to_int(card)
        return max_card"""

    def get_lead_card(self, board):
        max_card = board[0]
        max_val = Agent.convert_card_rank_to_int(max_card)
        lead_suit = board[0]
        for card_index in board:
            card = board[card_index]
            if card.suit == lead_suit and Agent.convert_card_rank_to_int(card) > max_val:
                max_card = card
                max_val = Agent.convert_card_rank_to_int(card)
            elif card.suit == "Spades" and (lead_suit != "Spades" or Agent.convert_card_rank_to_int(card) > max_val):
                max_card = card
                max_val = Agent.convert_card_rank_to_int(card)
        return max_card


    def create_board_rep(self, board):
        if not board:
            return ("EMPTY", )
        else:
            if len(board) == 1:
                result =(self.create_card_representation(list(board.values())[0]), )
                return result
            lead_card = self.get_lead_card(board)
            result = (self.create_card_representation(lead_card), )
        return result

    def create_card_representation(self, card: pyCardDeck.PokerCard):
        representation_dict = {"Spades":"S", "Clubs":"NS", "Diamonds":"NS", "Hearts":"NS"}
        rep = representation_dict[card.suit] + str(card.rank)
        return rep


class SRStandard(StateRepresentation):
    """
    This state representation will just store the lead card and the action taken.

    Lead card will be stored as either NS + rank, and action will be one of the possible actions

    If the top card is a ace of clubs and the action taken is LOWEST_SPADE it will be represented as such:

    (NSA, LOWEST_SPADE)
    """
    def __init__(self, **kwargs):
        StateRepresentation.__init__(self)
        self.last_board = None

    def save_state(self, state):
        self.last_board = state.board

    def create_state_rep_from_self(self, action):
        board = self.create_board_rep(self.last_board)
        state_action_rep = board + (action, )
        return state_action_rep

    def create_state_rep_from_state(self, state, action):
        board = self.create_board_rep(state.board)
        state_action_rep = board + (action, )
        return state_action_rep

class SRWithTurnsRemaining(StateRepresentation):
    """
    This state representation will record how many cards are left in hand so the agent can change strategy
    over the course of the game and can change stategy accordingly

    This increased the number of state action by ~13x in a two player game, and as such will require a lot more training
    most likely
    Example for a club of spades with 8 turns remaining

    (NSA, 5, LOWEST_SPADE)
    """
    def __init__(self, num_players =2, **kwargs):
        StateRepresentation.__init__(self)
        self.last_board = None
        self.turns_remaining = int(round(52/num_players))

    def save_state(self, state):
        self.last_board = state.board
        self.turns_remaining = len(state.players[0].hand)

    def create_state_rep_from_self(self, action):
        board = self.create_board_rep(self.last_board)
        state_action_rep = board + (self.turns_remaining, action, )
        return state_action_rep

    def create_state_rep_from_state(self, state, action):
        board = self.create_board_rep(state.board)
        state_action_rep = board + (self.turns_remaining, action, )
        return state_action_rep



class SRWithTurnsAndWinning(StateRepresentation):
    """
    This state representation will track whether or not the learning agent is winning.

    My thought process is that it will seperate winning and losing cases more and as a result go more towards winning
    """
    def __init__(self, num_players =2, **kwargs):
        StateRepresentation.__init__(self)
        self.last_board = None
        self.turns_remaining = int(round(52/num_players))
        self.scores = None
        self.index = kwargs['player_index']

    def get_winning_losing(self, scores):
        if scores is None:
            return "TIED"
        player_score = self.scores[self.index]
        max_score = max(self.scores, key=self.scores.get)
        if player_score == max_score:
            return "WINNING"
        else:
            return "LOSING"

    def save_state(self, state):
        self.last_board = state.board
        self.turns_remaining = len(state.players[0].hand)
        self.scores = state.scores

    def create_state_rep_from_self(self, action):
        board = self.create_board_rep(self.last_board)
        winning_losing = self.get_winning_losing(self.scores)
        state_action_rep = board + (self.turns_remaining, action, winning_losing, )
        return state_action_rep

    def create_state_rep_from_state(self, state, action):
        board = self.create_board_rep(state.board)
        winning_losing = self.get_winning_losing(state.scores)
        state_action_rep = board + (self.turns_remaining, action, winning_losing, )
        return state_action_rep

class SRWithTurnsAndSpades(StateRepresentation):
    """
    This state representation will keep track of turns and the amount of spades you have left

    With this I'm hoping that it will capture the trade off between using a Spade to win a turn and

    For example, a state representation when you have 5 Spades left and there is an ace of clubs:
    (NSA, 12, LOWEST_SPADE, 6)
    """
    def __init__(self, num_players =2, **kwargs):
        StateRepresentation.__init__(self)
        self.last_board = None
        self.turns_remaining = int(round(52/num_players))
        self.index = kwargs['player_index']
        self.hand = None

    def save_state(self, state):
        self.last_board = state.board
        self.turns_remaining = len(state.players[0].hand)
        ql_player = None
        for player in state.players:
            if player.index == self.index:
                ql_player = player
        self.hand = ql_player.hand

    def get_spades_remaining(self, hand):
        if hand is None:
            return -1
        spades = list(filter(lambda card: card.suit == "Spades", hand))
        return len(spades)

    def create_state_rep_from_self(self, action):
        board = self.create_board_rep(self.last_board)
        hand = self.get_spades_remaining(self.hand)
        state_action_rep = board + (self.turns_remaining, action, hand )
        return state_action_rep

    def create_state_rep_from_state(self, state, action):
        board = self.create_board_rep(state.board)
        hand = None
        for player in state.players:
            if type(player) == QLearningAgentNew:
                index = player.index
        hand_rep = self.get_spades_remaining(hand)
        state_action_rep = board + (self.turns_remaining, action, hand_rep)
        return state_action_rep

class SRWithWinningAndSpades(StateRepresentation):

    def __init__(self, num_players =2, **kwargs):
        StateRepresentation.__init__(self)
        self.last_board = None
        self.index = kwargs['player_index']
        self.hand = None

    def save_state(self, state):
        self.last_board = state.board
        self.scores = state.scores
        ql_player = None
        for player in state.players:
            if player.index == self.index:
                ql_player = player
        self.hand = ql_player.hand

    def create_state_rep_from_self(self, action):
        board = self.create_board_rep(self.last_board)
        winning_losing = self.get_winning_losing(self.scores)
        state_action_rep = board + (self.get_spades_remaining(self.hand), action, winning_losing, )
        return state_action_rep

    def create_state_rep_from_state(self, state, action):
        board = self.create_board_rep(state.board)
        winning_losing = self.get_winning_losing(state.scores)
        spades = self.get_spades_remaining(self.hand)
        for player in state.players:
            if type(player) == QLearningAgentNew:
                hand = player.hand
        state_action_rep = board + (self.get_spades_remaining(hand), action, winning_losing, )
        return state_action_rep

    def get_spades_remaining(self, hand):
        if hand is None:
            return -1
        spades = list(filter(lambda card: card.suit == "Spades", hand))
        return len(spades)

    def get_winning_losing(self, scores):
        if scores is None:
            return "TIED"
        player_score = self.scores[self.index]
        max_score = max(self.scores, key=self.scores.get)
        if player_score == max_score:
            return "WINNING"
        else:
            return "LOSING"

class QLearningAgentNew(Agent):

    def __init__(self, state_rep: StateRepresentation, index=0, num_training=100, epsilon=.1, alpha=.4, gamma=1, **kwargs):
        Agent.__init__(self, index=index)
        self.episodes_so_far=0.0
        self.accum_train_rewards = 0.0
        self.accum_test_rewards = 0.0
        self.num_training = num_training
        self.epsilon = float(epsilon)
        self.alpha = float(alpha)
        self.discount = float(gamma)
        self.q_values_betting = {}
        self.q_values = {}
        self.reward_this_episode = 0
        self.episodes_rewards = {0:0}
        kwargs = {"player_index":index, "num_players":2}
        self.state_rep = state_rep(**kwargs)
        self.last_reward = 0
        self.last_action = None


    def start_episode(self):
        self.reward_this_episode = 0
        max_episodes = max(self.episodes_rewards)
        self.episodes_rewards[max_episodes+1] = 0

    def end_episode(self):
        cur_episode = max(self.episodes_rewards)
        self.episodes_rewards[cur_episode] = self.reward_this_episode

    def make_bet(self, state, num_players=2):
        return 13#RandomAgent.make_bet(self, state)

    def getLegalActions(self, state):
        """
        Will map a limited set of moves to all possible moves based on the state provided
        Actions:
            if no cards on board and not only spades in hand:
                place_highest_non_spade_card
                place_lowest_non_spade_card
            if no cards on board and only spades in hand:
                place_lowest_spade_card
                place_highest_spade_card
            if cards on board:
                if you have same suit:
                    place_highest_same_suit
                    place_lowest_same_suit_that_wins
                    place_lowest_same_suit
                    place_lowest_spade_to_win
                if you don't have same suit:
                    place_lowest_non_spade
                    if you have spades:
                        place_lowest_spade_to_win
                        place_highest_spade_to_win
        """
        possible_ql_moves = []
        if state.cards_on_board():
            lead_card = state.get_lead_card()
            cards_of_same_suit = self.filter_by_suit(lead_card.suit)
            lowest_spade_that_wins = self.lowest_spade_that_wins(lead_card)
            off_suit_non_spades = self.non_spade_off_suits(lead_card.suit)
            has_same_suit = bool(cards_of_same_suit)
            if has_same_suit and lead_card.suit:
                highest_same_suit = self.highest_card_by_suit(lead_card.suit)
                lowest_same_suit = self.lowest_card_by_suit(lead_card.suit)
                lowest_same_suit_that_wins = self.lowest_card_that_wins(lead_card)
                if highest_same_suit:
                    if Agent.convert_card_rank_to_int(highest_same_suit) > Agent.convert_card_rank_to_int(lead_card):
                        possible_ql_moves.append("HIGHEST_SAME_SUIT_WIN")
                    else:
                        possible_ql_moves.append("HIGHEST_SAME_SUIT_LOSS")
                if lowest_same_suit:
                    if Agent.convert_card_rank_to_int(lowest_same_suit) < Agent.convert_card_rank_to_int(lead_card):
                        possible_ql_moves.append("LOWEST_SAME_SUIT_LOSS")
                if lowest_same_suit_that_wins:
                    possible_ql_moves.append("LOWEST_SAME_SUIT_WIN")
            if lowest_spade_that_wins:
                possible_ql_moves.append("LOWEST_SPADE_WIN")
            if off_suit_non_spades:
                possible_ql_moves.append("LOWEST_OFF_SUIT")
        else:
            non_spades = self.filter_by_suit("Diamonds") + self.filter_by_suit("Hearts") + self.filter_by_suit("Clubs")
            spades = self.filter_by_suit("Spades")
            if non_spades:
                possible_ql_moves.append("HIGHEST_NON_SPADE")
                possible_ql_moves.append("LOWEST_NON_SPADE")
            elif spades:
                possible_ql_moves.append("HIGHEST_SPADE")
                possible_ql_moves.append("LOWEST_SPADE")
        return possible_ql_moves

    def map_legal_actions_to_action(self, legal_action, state):
        lead_card = state.get_lead_card()
        if legal_action == "HIGHEST_SPADE":
            return self.highest_card_by_suit("Spades")
        elif legal_action == "LOWEST_SPADE":
            return self.lowest_card_by_suit("Spades")
        elif legal_action == "HIGHEST_SAME_SUIT_WIN" or legal_action == "HIGHEST_SAME_SUIT_LOSS":
            return self.highest_card_by_suit(lead_card.suit)
        elif legal_action == "LOWEST_SAME_SUIT_LOSS":
            return self.lowest_card_by_suit(lead_card.suit)
        elif legal_action == "LOWEST_SAME_SUIT_WIN":
            return self.lowest_card_that_wins(lead_card)
        elif legal_action == "LOWEST_SPADE_WIN":
            return self.lowest_spade_that_wins(lead_card)
        elif legal_action == "HIGHEST_NON_SPADE":
            return self.highest_non_spade()
        elif legal_action == "LOWEST_NON_SPADE":
            return self.lowest_non_spade()
        elif legal_action == "LOWEST_OFF_SUIT":
            return self.lowest_off_suit(lead_card.suit)
        else:
            raise ValueError("Invalid legal action: " + str(legal_action))

    def get_multiplier_last_action(self):
        action = self.state_rep.last_action
        mult_dict = {"HIGHEST_SPADE": .5, "LOWEST_SPADE":.7, "HIGHEST_SAME_SUIT":1.5,"LOWEST_SAME_SUIT_LOSS":.5,
                     "LOWEST_SAME_SUIT_WIN": 4, "LOWEST_SPADE_WIN":.7, "HIGHEST_NON_SPADE":1, "LOWEST_NON_SPADE":1,
                     "LOWEST_OFF_SUIT":1, "HIGHEST_SAME_SUIT_LOSS":.5, "HIGHEST_SAME_SUIT_WIN":1.2}
        return mult_dict[action]

    def get_multiplier_last_action_lose(self):
        action = self.state_rep.last_action
        mult_dict = {"HIGHEST_SPADE": 4, "LOWEST_SPADE": 3, "HIGHEST_SAME_SUIT": 1.2, "LOWEST_SAME_SUIT_LOSS": .5,
                     "LOWEST_SAME_SUIT_WIN": 1, "LOWEST_SPADE_WIN": 3, "HIGHEST_NON_SPADE": 1.5, "LOWEST_NON_SPADE": .5,
                     "LOWEST_OFF_SUIT": .3, "HIGHEST_SAME_SUIT_LOSS": .75, "HIGHEST_SAME_SUIT_WIN": 1.2}
        return mult_dict[action]

    def get_multiplier_last_action_win(self):
        action = self.state_rep.last_action
        mult_dict = {"HIGHEST_SPADE": .3, "LOWEST_SPADE":.7, "HIGHEST_SAME_SUIT":1.2,"LOWEST_SAME_SUIT_LOSS":.5,
                     "LOWEST_SAME_SUIT_WIN": 3, "LOWEST_SPADE_WIN":.7, "HIGHEST_NON_SPADE":1, "LOWEST_NON_SPADE":.7,
                     "LOWEST_OFF_SUIT":.3, "HIGHEST_SAME_SUIT_LOSS":3, "HIGHEST_SAME_SUIT_WIN":1.2}
        return mult_dict[action]



    def getAction(self, state):
        # Pick Actions
        legalActions = self.getLegalActions(state)
        exploration = util.flipCoin(self.epsilon)
        if exploration:
            exploration_action = random.choice(legalActions)
            action = exploration_action
        else:
            exploitation_action = self.getPolicy(state)
            action = exploitation_action
        return action

    def computeValueFromQValues(self, state):
        """
          Returns max_action Q(state,action)
          where the max is over legal actions.  Note that if
          there are no legal actions, which is the case at the
          terminal state, you should return a value of 0.0.
        """
        actions = self.getLegalActions(state)
        if len(actions) == 0:
            return 0.0
        max_val = -9999999
        for action in actions:
            value = self.get_q_value(state, action)
            if value > max_val:
                max_val = value
        return max_val

    def computeActionFromQValues(self, state):
        """
          Compute the best action to take in a state.  Note that if there
          are no legal actions, which is the case at the terminal state,
          you should return None.
        """
        starting_value = self.computeValueFromQValues(state)
        actions = self.getLegalActions(state)
        possible_actions = []
        for action in actions:
            if self.get_q_value(state, action) >= starting_value:
                possible_actions.append(action)
        if len(possible_actions) == 0:
            return None
        return random.choice(possible_actions)

    def update(self, action, nextState, reward):
        """
          The parent class calls this to observe a
          state = action => nextState and reward transition.
          You should do your Q-Value update here
          NOTE: You should never call this function,
          it will be called on your behalf
        """
        "*** YOUR CODE HERE ***"
        # Formula for update from slide:
        # Q(s, a) <- q(s,a) + alpha * [R + discount * max_a Q(s'a,) - Q(s,a)]
        original_q_value = self.get_q_value(nextState, action, from_self=True)
        next_q_value = self.computeValueFromQValues(nextState)
        current_rep = self.create_state_action_rep_from_self(action)
        next_state_rep = self.create_state_action_rep(nextState, action)
        updated_q_value = original_q_value + self.alpha * (reward + self.discount * next_q_value - original_q_value)
        self.set_q_values(action, updated_q_value)
        self.reward_this_episode += reward

    def set_q_values(self, action, updated_q_value):
        state_action_rep = self.state_rep.create_state_rep_from_self(action)
        self.q_values[state_action_rep] = updated_q_value

    def getPolicy(self, state):
        return self.computeActionFromQValues(state)

    def getValue(self, state):
        return self.computeValueFromQValues(state)


    def get_q_value(self, state, action, from_self=False):
        """
        For the Q table the first item will be the leading card, followed by cards in the order they are placed.
        The second to last item will be turns remaining
        The last item in the lookup will be the the action i.e "HIGHEST_SPADE" etc.
        There is 6 turns left
        If the board is empty it will be ("EMPTY", 6, "HIGHEST_NON_SPADE") for example
        Cards will be represented as a string with representing with either NS or S indicating non_spade or spade
         + value
        for example a board with a seven of hearts will be "(H7, ACTION)"
        :param state:
        :param action:
        :return:
        """
        if state is None:
            return 0.0
        if from_self:
            state_action = self.create_state_action_rep_from_self(action)
        else:
            state_action = self.create_state_action_rep(state, action)
        if state_action in self.q_values:
            return self.q_values[state_action]
        else:
            return 0.0

    def create_state_action_rep(self, state, action):
        return self.state_rep.create_state_rep_from_state(state, action)

    def create_state_action_rep_from_self(self, action):
        return self.state_rep.create_state_rep_from_self(action)

    def save_state(self, state):
        self.state_rep.save_state(state)

    def set_last_action(self, action):
        self.state_rep.last_action = action

    def get_last_reward(self):
        return self.last_reward

    def get_last_action(self):
        return self.state_rep.last_action