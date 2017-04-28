import os
import json

PRUNE_NUM = 4 #This number of best weights for each parameter will be kept (at most)
PRUNE_PERC = 0.5 #Conditional win percentages below this will be discarded as well

current_dir = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(current_dir,"learning_weights.json"),"r") as f:
    weight_test_results = json.load(f)

total_wins = 0
total_played = 0

for parameter in weight_test_results:
    for weight in weight_test_results[parameter]:
        total_wins += weight_test_results[parameter][weight][0]
        total_played += weight_test_results[parameter][weight][1]

prob_win_total = total_wins/total_played #total probability that a given game is won
new_weights_dict = {}

for parameter in weight_test_results:
    worst_weight = None
    continued_weights = {} # weights continued into output
    for weight in weight_test_results[parameter]:
        weight_wins = int(weight_test_results[parameter][weight][0])
        weight_total = int(weight_test_results[parameter][weight][1])
        if weight_wins == 0 or weight_total == 0:
            print ("Removing {}: {} empty".format(parameter, weight))
            continue
        prob_weight_win = weight_wins/weight_total
        if prob_weight_win <= PRUNE_PERC:
            print("Removing {}: {} at {}".format(parameter, weight, prob_weight_win))
            continue
        continued_weights_entry = [weight_wins, weight_total, prob_weight_win]
        if len(continued_weights) >= PRUNE_NUM:
            if (prob_weight_win > continued_weights[worst_weight][2] #The new weight is considered better than the previous weight
                or (prob_weight_win == continued_weights[worst_weight][2]
                    and weight_total > continued_weights[worst_weight][1])):
                print("Removing {0}: {1} at {2} in favor of {0}:{3} at {4}".format(
                    parameter, worst_weight, continued_weights[worst_weight], weight, continued_weights_entry))
                del continued_weights[worst_weight]
                continued_weights[weight] = continued_weights_entry
                worst_weight = min(continued_weights, key = continued_weights.get)
            elif prob_weight_win == continued_weights[worst_weight][2]: #this weight and current weight are equal, both kept
                continued_weights[weight] = continued_weights_entry
            else: #worst weight is better than current weight
                print("Removing {}: {} at {}, parameter full".format(parameter, weight, continued_weights_entry))
        elif worst_weight is None or prob_weight_win < continued_weights[worst_weight][2]:
            worst_weight = str(weight)
            continued_weights[weight] = continued_weights_entry
        else:
            continued_weights[weight] = continued_weights_entry
    if continued_weights != {}:
        new_weights_dict[parameter] = continued_weights

with open(os.path.join(current_dir,"learning_weights2.json"), "w") as f:
    json.dump(new_weights_dict, f)