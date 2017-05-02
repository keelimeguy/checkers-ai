import os
import json
import pdb

PRUNE_NUM = 6 #This number of best weights for each parameter will be kept (at most)
PRUNE_PERC = 0.54 #Conditional win percentages below this will be discarded as well

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

def get_win_probability(weights_dict_no_param, weight):
    weight_wins = int(weights_dict_no_param[weight][0])
    weight_total = int(weights_dict_no_param[weight][1])
    if weight_wins == 0 or weight_total == 0:
        return False
    else:
        return weight_wins/weight_total

def prune_test_weights(weight_test_results):
    new_weights_dict = {}
    for parameter in weight_test_results:
        worst_weight = None
        continued_weights = {}  # weights continued into output
        for weight in weight_test_results[parameter]:
            prob_weight_win = get_win_probability(weight_test_results[parameter], weight)
            if not prob_weight_win:
                print("Removing {}: {} empty".format(parameter, weight))
                continue
            elif prob_weight_win <= PRUNE_PERC:
                print("Removing {}: {} at {}".format(parameter, weight, prob_weight_win))
                continue
            continued_weights_entry = weight_test_results[parameter][weight]
            if worst_weight is not None:
                prob_worst_weight_win = get_win_probability(continued_weights, worst_weight)
            if len(continued_weights) >= PRUNE_NUM:
                if ((
                        prob_weight_win > prob_worst_weight_win)  # The new weight is considered better than the previous weight
                    or (prob_weight_win == prob_worst_weight_win
                        and continued_weights_entry[1] > continued_weights[worst_weight][1])):
                    print("Removing {0}: {1} at {2} in favor of {0}:{3} at {4}".format(
                        parameter, worst_weight, continued_weights[worst_weight], weight, continued_weights_entry))
                    del continued_weights[worst_weight]
                    continued_weights[weight] = continued_weights_entry
                    worst_weight = min(continued_weights, key=continued_weights.get)
                elif prob_weight_win == prob_worst_weight_win:  # this weight and current weight are equal, both kept
                    continued_weights[weight] = continued_weights_entry
                else:  # worst weight is better than current weight
                    print("Removing {}: {} at {}, parameter full".format(parameter, weight, continued_weights_entry))
                    continue
            elif worst_weight is None or prob_weight_win < prob_worst_weight_win:
                worst_weight = str(weight)
                continued_weights[weight] = continued_weights_entry
            else:
                continued_weights[weight] = continued_weights_entry
        if continued_weights != {}:
            new_weights_dict[parameter] = continued_weights
    return new_weights_dict

def generate_new_weightset_iter(weights_dict, dict_keys, product, output_dict):
    if len(dict_keys) == 0:
        return product
    parameter = dict_keys.pop()
    best_product = 0
    best_output = None
    for weight in weights_dict[parameter]:
        prob_win_given_weight = int(weights_dict[parameter][weight][0])/total_wins
        prob_weight = int(weights_dict[parameter][weight][1])/total_played
        product = product * (prob_win_given_weight / prob_weight) #statistics might be a bit skewed here, not really sure. Will be easier to tell when we don't win basically every game.
        output_dict[parameter] = weight
        if len(dict_keys) != 0:
            full_product, output = generate_new_weightset_iter(weights_dict, dict_keys, product, output_dict)
        else:
            full_product = product
            output = output_dict
        if full_product > best_product:
            best_product = full_product
            best_output = output
    return best_product, best_output

def generate_new_weightset(weights_dict):
    """Uses naive bayes algorithm to generate a new default set of weights

    p(win|weights) = p(win) * product from i=0 to n of p(weight_i | win)/p(weight_i)"""
    result_product, result_output = generate_new_weightset_iter(weights_dict, list(weights_dict.keys()), 1, {})
    final_product = prob_win_total * result_product
    result_output["Probability of Win"] = final_product
    return result_output, final_product

new_weights_dict = prune_test_weights(weight_test_results)
out_weights, final_product = generate_new_weightset(new_weights_dict)
print(final_product)

with open(os.path.join(current_dir,"learning_weights2.json"), "w") as f:
    json.dump(new_weights_dict, f)

with open(os.path.join(current_dir, "weights2.json"), "w") as f:
    json.dump(out_weights, f)
