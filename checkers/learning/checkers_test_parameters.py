import json
import os
import subprocess
import sys

#Tests various weights on parameters. Results are stored in learning_weights.json
#Recognition for other parameters will be added next.

current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.realpath(os.path.join(current_dir, os.pardir))
run_dir = os.path.realpath(os.path.join(current_dir, os.pardir, os.pardir))
outfile = os.path.join(current_dir, "weights_temp.json")
checkers_path = os.path.realpath(os.path.join(current_dir, os.pardir, "heuristics.py"))

with open(os.path.join(current_dir,"learning_weights.json"),"r") as f:
    weight_tests = json.load(f)

def run_sp_game(weight_file=None):
    weight_file = weight_file or outfile

    # Note: python 3.6 is required to run
    return subprocess.check_output(
        "python3 -m checkers.heuristics -c 1 -w {}".format(outfile),
        # "python3.6 -m checkers.heuristics -c 1 -w {}".format(outfile),
        stderr=sys.stderr,  # subprocess.STDOUT,
        shell=True)

def perror(*args, **kwargs):
    kwargs["file"] = sys.stderr
    print(*args, **kwargs)

for parameter in weight_tests:
    for weight in weight_tests[parameter]:
        weight = int(weight)
        with open(os.path.join(parent_dir, "weights.json"), "r") as f:
            active_weights = json.load(f)
        if parameter in active_weights:
            active_weights[parameter]["weight"] = weight
        else:
            active_weights[parameter] = {"weight" : weight, "wins" : 0, "total" : 0}
        with open(outfile, "w") as f:
            json.dump(active_weights, f)

        #This is horrible code, but everything else that I can think of does not work due to memory leak.
        os.chdir(run_dir)
        try:
            result = run_sp_game()
        except subprocess.CalledProcessError as e:
            perror("Failed first attempt:")
            perror(e.output)
            try:
                result = run_sp_game()
            except subprocess.CalledProcessError as e:
                perror("Failed second attempt:")
                perror(e.output)
                break
        os.chdir(current_dir)
        for line in result.split(b'\n'):
            if line and line.split()[0] == b"Stats:":
                result_line =  line.split()[1]
                results = result_line.split(b':')
                wins = int(results[0][0]) - 48
                draws = int(results[1][0]) - 48
                losses = int(results[2][0]) - 48
        print("Finished '{}', weight {}: {}/{}".format(parameter, weight, wins, wins+draws+losses))
        weight_tests[parameter][str(weight)][0] += wins
        weight_tests[parameter][str(weight)][1] += wins + draws + losses

with open("learning_weights.json", "w") as f:
    json.dump(weight_tests, f)
