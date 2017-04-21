import json
import os
import subprocess

#Tests various weights on parameters. Results are stored in learning_weights.json
#Recognition for other parameters will be added next.

current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.realpath(os.path.join(current_dir, os.pardir))
run_dir = os.path.realpath(os.path.join(current_dir, os.pardir, os.pardir))
outfile = os.path.join(current_dir, "weights_temp.json")
checkers_path = os.path.realpath(os.path.join(current_dir, os.pardir, "checkers_player.py"))

weight_tests = json.load(open(os.path.join(current_dir,"learning_weights.json"),"r"))

for parameter in weight_tests:
    for weight in weight_tests[parameter]:
        weight = int(weight)
        active_weights = json.load(open(os.path.join(parent_dir, "weights_example.json"), "r"))
        if parameter in active_weights:
            active_weights[parameter]["weight"] = weight
        else:
            active_weights[parameter] = {"weight" : weight, "wins" : 0, "total" : 0}
        json.dump(active_weights, open(outfile,"w"))

        #This is horrible code, but everything else that I can think of does not work due to memory leak.
        os.chdir(run_dir)
        try:
            result = subprocess.check_output("python3 -m checkers.checkers_player -c 1 -w {}".format(outfile),
                                             stderr=subprocess.STDOUT, shell=True)
        except subprocess.CalledProcessError as e:
            print("Failed first attempt:")
            print(e.output)
            try:
                result = subprocess.check_output("python3 -m checkers.checkers_player -c 1 -w {}".format(outfile),
                                                stderr=subprocess.STDOUT, shell=True)
            except subprocess.CalledProcessError as e:
                print("Failed")
                print(e.output)
                break
        os.chdir(current_dir)
        for line in result.split('\n'):
            if line and line.split()[0] == "Stats:":
                result_line =  line.split()[1]
                results = result_line.split(':')
                wins = int(results[0][0])
                draws = int(results[1][0])
                losses = int(results[2][0])
        print("Finished '{}', weight {}: {}/{}".format(parameter, weight, wins, wins+draws+losses))
        weight_tests[parameter][str(weight)][0] += wins
        weight_tests[parameter][str(weight)][1] += wins + draws + losses
json.dump(weight_tests, open("learning_weights.json","w"))
