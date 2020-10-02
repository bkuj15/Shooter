import sys
import json




targ_map = {}


def read_updates(filepath):

	print("checking for active updates in " + filepath)
	with open(filepath, "r") as a_file:

		for line in a_file:
			stripped_line = line.strip()
			if "changed from " in stripped_line:
				print(stripped_line)

				end_targ = stripped_line.split(" to ")[1]
				print("parse this hoe up: " + end_targ)

				targ_json = json.loads(end_targ)

				symbol = targ_json["symbol"]
				strike = targ_json["strike"]

				contract = symbol + "-" + str(strike)

				print("add this to some counter map: " + contract)

				targ_val = {
					"count": 1,
					"info": targ_json
				}

				if contract in targ_map:

					targ_map[contract]["count"] = targ_map[contract]["count"] + 1
				else:
					targ_map[contract] = targ_val




            	

            




def main(fp):
	print("checking update log for active bouncaz..")

	read_updates(fp)


	print("\n\ntarg map after read: " + json.dumps(targ_map))



if __name__ == "__main__":
	if len(sys.argv) == 2:
		fp = sys.argv[1]
		main(fp)
	else:
		print("sike wrong number of args: " )
	