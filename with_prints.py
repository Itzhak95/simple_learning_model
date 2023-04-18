from random import choices, randint, seed
import timeit

start = timeit.default_timer()

# Set the number of simulations

s = 50

# Lists to collect the results

big_prices = []
big_trades = []
big_values = []
big_costs = []

for i in range(s):

    # Set the buyer valuations and seller costs

    input_values = [82, 77, 72, 67, 62]

    input_costs = [8, 38, 68, 98, 128]

    # Set the level of belief volatility

    d = 0.8

    # Set the number of rounds

    r = 10

    # Set the maximum length of every round

    l = 200

    # Set the replacement rule (0 = no replacement, 1 = perfect replacement, 2 = random replacement)

    replacement = 0

    # INITIAL BELIEFS AND DEFINITIONS

    # I set m equal to 3 times the average cost (this creates a kind of symmetry)

    m = int(3 * sum(input_costs) / len(input_costs))

    print(f'm: {m}')

    b_beliefs = [i / m for i in range(m + 1)]

    s_beliefs = [1 - j / m for j in range(m + 1)]

    n = len(input_values)

    # DATA LISTS

    bids = []

    asks = []


    # BELIEF REVISION

    def accepted_bid(bid):
        for number in range(m + 1):
            # Increase the chance that this bid and better (higher) bids will be accepted
            if number >= bid:
                b_beliefs[number] = d + (1 - d) * b_beliefs[number]


    def rejected_bid(bid):
        print('Punish low bids')
        for number in range(m + 1):
            # Decrease the chance that this bid and worse (lower) bids will be accepted
            if number <= bid:
                b_beliefs[number] = (1 - d) * b_beliefs[number]


    def accepted_ask(ask):
        for number in range(m + 1):
            # Increase the chance that this ask and better (lower) ones will be accepted
            if number <= ask:
                s_beliefs[number] = d + (1 - d) * s_beliefs[number]


    def rejected_ask(ask):
        print('Punish high asks')
        for number in range(m + 1):
            # Decrease the chance that this ask and worse (higher) ones will be accepted
            if number >= ask:
                s_beliefs[number] = (1 - d) * s_beliefs[number]


    # OPTIMISATION

    def buyer_payoff(value, bid):
        if bid >= market_ask:
            return value - market_ask
        else:
            return (value - bid) * b_beliefs[bid]


    def optimal_bid(value):
        possible_bids = list(range(market_bid + 1, market_ask + 1))
        payoffs = [buyer_payoff(value, bid) for bid in possible_bids]
        max_payoff = max(payoffs)
        best_bid = payoffs.index(max_payoff) + min(possible_bids)
        if max_payoff > 0:
            return [best_bid, max_payoff]
        else:
            return [0, 0]


    def seller_payoff(cost, ask):
        if ask <= market_bid:
            return market_bid - cost
        else:
            return (ask - cost) * s_beliefs[ask]


    def optimal_ask(cost):
        possible_asks = list(range(market_bid, market_ask))
        payoffs = [seller_payoff(cost, ask) for ask in possible_asks]
        max_payoff = max(payoffs)
        best_ask = payoffs.index(max_payoff) + min(possible_asks)
        if max_payoff > 0:
            return [best_ask, max_payoff]
        else:
            return [0, 0]


    # TIMING

    # This function calculates the chance that each player will move

    def p_move():
        buyer_payoffs = [optimal_bid(v)[1] for v in values]
        seller_payoffs = [optimal_ask(c)[1] for c in costs]
        if sum(buyer_payoffs) == 0 and sum(seller_payoffs) == 0:
            return None
        elif sum(buyer_payoffs) > 0 and sum(seller_payoffs) == 0:
            return [0] + [i / sum(buyer_payoffs) for i in buyer_payoffs]
        elif sum(buyer_payoffs) == 0 and sum(seller_payoffs) > 0:
            return [1] + [i / sum(seller_payoffs) for i in seller_payoffs]
        else:
            num = randint(0, 1)
            if num == 0:
                return [num] + [i / sum(buyer_payoffs) for i in buyer_payoffs]
            else:
                normalisation = sum(seller_payoffs)
                return [num] + [i / normalisation for i in seller_payoffs]

    # This function chooses a player to move

    def choose_player():
        output = p_move()
        if output is not None:
            type = output[0]
            weights = output[1:]
            print(f'Type: {type}')
            print(f'Probabilities: {weights}')
            if type == 0:
                return choices(buyers, weights)[0]
            elif type == 1:
                return choices(sellers, weights)[0]


    # SIMULATIONS

    # Define some lists that will be used to collect the results

    all_prices = []
    number_of_trades = []
    all_buyer_values = []
    all_seller_costs = []

    for i in range(r):
        # At the start of a round, refresh the buyer/seller valuations
        buyers = list(range(0, n))
        sellers = list(range(n, 2 * n))
        values = [element for element in input_values]
        costs = [element for element in input_costs]
        # Reset the spread
        market_bid = 0
        market_ask = m
        spread = list(range(market_bid + 1, market_ask))
        active_bidder = 100
        active_seller = 100
        # Reset the lists used for data collection
        prices = []
        buyer_values = []
        seller_costs = []
        trades = 0
        # The round now begins
        iteration = 0
        # # Print beliefs
        # print('Buyer beliefs')
        # for i in range(m + 1):
        #     print(round(b_beliefs[i], 10))
        # print('Seller beliefs')
        # for i in range(m + 1):
        #     print(round(s_beliefs[i], 10))
        while iteration <= l:
            iteration += 1
            print(f'Move: {iteration}')
            # First, choose a player
            player = choose_player()
            if player is None:
                print("End of round")
                break
            print(f'Player: {player}')
            # Suppose first they are a buyer
            if player in buyers:
                print('[Buyer]')
                index = buyers.index(player)
                valuation = values[index]
                print(f'Valuation {valuation}')
                bid = optimal_bid(valuation)[0]
                # They might choose to accept the market ask, leading to transaction
                if bid == market_ask:
                    # Belief update
                    b_beliefs = [i / m for i in range(m + 1)]
                    accepted_bid(bid)
                    rejected_bid(bid-1)
                    s_beliefs = [1 - j / m for j in range(m + 1)]
                    accepted_ask(market_ask)
                    rejected_ask(market_ask+1)
                    trades += 1
                    print(f'Trades {trades}')
                    prices.append(market_ask)
                    print(f'Prices {prices}')
                    buyer_values.append(valuation)
                    # Print beliefs
                    # print('Buyer beliefs')
                    # for i in range(m + 1):
                    #     print(round(b_beliefs[i], 10))
                    # print('Seller beliefs')
                    # for i in range(m + 1):
                    #     print(round(s_beliefs[i], 10))
                    # Following the transaction, we need to reset the bid/ask spread
                    market_bid = 0
                    print(f'Market bid {market_bid}')
                    market_ask = m
                    print(f'Market ask {market_ask}')
                    # We also remove the buyer/seller (and their value/cost) from the market
                    if replacement != 1:
                        buyers.remove(player)
                        values.remove(valuation)
                    # In the case of random replacement...
                    if replacement == 2:
                        new_buyer = randint(0, n - 1)
                        buyers.append(new_buyer)
                        print(f'New buyer: {new_buyer}')
                        values.append(input_values[new_buyer])
                        print(f'New value: {input_values[new_buyer]}')
                    print(f'Buyers {buyers}')
                    print(f'Values {values}')
                    print(f'Active seller {active_seller}')
                    index = sellers.index(active_seller)
                    cost = costs[index]
                    seller_costs.append(cost)
                    if replacement != 1:
                        costs.remove(cost)
                        sellers.remove(active_seller)
                    print(f'Costs {costs}')
                    print(f'Sellers {sellers}')
                    # In the case of random replacement...
                    if replacement == 2:
                        new_seller = randint(n, 2 * n - 1)
                        sellers.append(new_seller)
                        print(f'New seller: {new_seller}')
                        costs.append(input_costs[new_seller - n])
                        print(f'New value: {input_costs[new_seller - n]}')
                # Alternatively, they might just be making a (positive) bid
                elif market_ask > bid > 0:
                    active_bidder = player
                    print(f'Active bidder {active_bidder}')
                    bids.append(bid)
                    print(f'Bids {bids}')
                    market_bid = bid
                    print(f'Market bid: {market_bid}')
            # Instead, the player might be a seller
            elif player in sellers:
                print('[Seller]')
                index = sellers.index(player)
                cost = costs[index]
                print(f'Cost: {cost}')
                ask = optimal_ask(cost)[0]
                print(f'Ask: {ask}')
                # They might choose to accept the market bid, leading to a transaction
                if ask == market_bid:
                    # Belief update
                    b_beliefs = [i / m for i in range(m + 1)]
                    accepted_bid(ask)
                    rejected_bid(ask - 1)
                    s_beliefs = [1 - j / m for j in range(m + 1)]
                    accepted_ask(ask)
                    rejected_ask(ask + 1)
                    trades += 1
                    print(f'Trades {trades}')
                    prices.append(market_bid)
                    seller_costs.append(cost)
                    # # Print beliefs
                    # print('Buyer beliefs')
                    # for i in range(m + 1):
                    #     print(round(b_beliefs[i], 10))
                    # print('Seller beliefs')
                    # for i in range(m + 1):
                    #     print(round(s_beliefs[i], 10))
                    # Following the transaction, we need to reset the bid/ask spread
                    market_bid = 0
                    print(f' Market bid {market_bid}')
                    market_ask = m
                    print(f' Market ask {market_ask}')
                    # We also remove the seller/buyer (and their cost/value) from the market
                    if replacement != 1:
                        sellers.remove(player)
                        costs.remove(cost)
                    # In the case of random replacement...
                    if replacement == 2:
                        new_seller = randint(n, 2 * n - 1)
                        sellers.append(new_seller)
                        print(f'New seller: {new_seller}')
                        costs.append(input_costs[new_seller - n])
                        print(f'New value: {input_costs[new_seller - n]}')
                    print(f' Sellers {sellers}')
                    print(f' Costs {costs}')
                    index = buyers.index(active_bidder)
                    valuation = values[index]
                    buyer_values.append(valuation)
                    if replacement != 1:
                        values.remove(valuation)
                        buyers.remove(active_bidder)
                    print(f' Values {values}')
                    print(f' Buyers {buyers}')
                    # In the case of random replacement...
                    if replacement == 2:
                        new_buyer = randint(0, n - 1)
                        buyers.append(new_buyer)
                        print(f'New buyer: {new_buyer}')
                        values.append(input_values[new_buyer])
                        print(f'New value: {input_values[new_buyer]}')
                # They might instead be just making an ask (less than m)
                elif market_bid < ask < m:
                    active_seller = player
                    print(f'Active seller {active_seller}')
                    asks.append(ask)
                    print(f'Asks: {asks}')
                    market_ask = ask
                    print(f'Market ask: {market_ask}')
            # In either case, we should update the spread and union lists:
            spread = list(range(market_bid + 1, market_ask))
            print('------')
            # Also...
            if iteration == l + 1:
                print('Forced ending!')
        # Save the data from this round
        all_prices.append(prices)
        number_of_trades.append(trades)
        all_buyer_values.append(buyer_values)
        all_seller_costs.append(seller_costs)

    # Print the results
    print('RESULTS')
    print(f'Prices: {all_prices}')
    print(f'Trades: {number_of_trades}')
    print(f'Buyer values: {all_buyer_values}')
    print(f'Seller costs: {all_seller_costs}')

    # Save the data from this simulation
    big_prices.append(all_prices)
    big_trades.append(number_of_trades)
    big_values.append(all_buyer_values)
    big_costs.append(all_seller_costs)

# Calculate mean absolute deviation
print('----------------')

higher = 72
lower = 68

def ad(number):
    if number >= higher:
        return abs(number - higher)
    elif number < lower:
        return abs(number-lower)
    else:
        return 0

num_prices = 0
tad = 0
for simulation in big_prices:
    for round in simulation:
        for price in round:
            num_prices += 1
            tad += ad(price)

print('MAD')
print(tad/num_prices)

num_prices = 0
tad = 0
for simulation in big_prices:
    for round in simulation[1:]:
        for price in round:
            num_prices += 1
            tad += ad(price)

print('MAD (round >= 2)')
print(tad/num_prices)

# Finally, print the results
print('----------------')
print(big_prices)
print(big_trades)
print(big_values)
print(big_costs)

stop = timeit.default_timer()

print('Time: ', stop - start)
