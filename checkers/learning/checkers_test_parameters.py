import json
import os
import subprocess
import sys
import time

#Tests various weights on parameters. Results are stored in learning_weights.json
#Recognition for other parameters will be added next.

current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.realpath(os.path.join(current_dir, os.pardir))
run_dir = os.path.realpath(os.path.join(current_dir, os.pardir, os.pardir))
outfile = os.path.join(current_dir, "weights_temp.json")
checkers_path = os.path.realpath(os.path.join(current_dir, os.pardir, "game_example.py"))

with open(os.path.join(current_dir,"learning_weights.json"),"r") as f:
    weight_tests = json.load(f)

def run_sp_game(weight_file=None):
    weight_file = weight_file or outfile

    # Note: python 3.6 is required to run
    return subprocess.check_output(
        "python3 -m checkers.game_example -w {}".format(outfile),
        stderr=sys.stderr,  # subprocess.STDOUT,
        shell=True)

def perror(*args, **kwargs):
    kwargs["file"] = sys.stderr
    print(*args, **kwargs)

start_time = time.time()
while time.time() < start_time + 25200:
    for parameter in weight_tests:
        for weight in weight_tests[parameter]:
            weight = int(weight)
            with open(os.path.join(parent_dir, "weights.json"), "r") as f:
                active_weights = json.load(f)
            active_weights[parameter] = weight
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
            draws = 0
            wins = 0
            losses = 0
            for line in result.split(b'\n'):
                if line:
                    rline = line.split(b':')
                    if rline[0] == b"Game result":
                        result_line =  rline[1].split()[0]
                        if result_line == b"Draw":
                            draws = 1
                            break;
                    if rline[0] == b"Client Win?":
                        result_line =  rline[1].split()[0]
                        if result_line == b"True":
                            wins = 1
                        if result_line == b"False":
                            losses = 1
            print("Finished '{}', weight {}: {}/{}".format(parameter, weight, wins, wins+draws+losses))
            weight_tests[parameter][str(weight)][0] += wins
            weight_tests[parameter][str(weight)][1] += wins + draws + losses
            with open("learning_weights.json", "w") as f:
                json.dump(weight_tests, f)
