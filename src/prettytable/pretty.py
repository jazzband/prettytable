from prettytable import PrettyTable 
table1 = PrettyTable()
table1.field_names = ["City name", "Area", "Population", "Annual Rainfall"]
table1.add_row(["Adelaide", 1295, 1158259, 600.5])
table1.add_row(["Brisbane", 5905, 1857594, 1146.4])
table1.add_row(["Darwin", 112, 120900, 1714.7])
table1.add_row(["Hobart", 1357, 205556, 619.5])
table1.add_row(["Sydney", 2058, 4336374, 1214.8])
table1.add_row(["Melbourne", 1566, 3806092, 646.9])
table1.add_row(["Perth", 5386, 1554769, 869.4])
table1.align = "l"
table1.add_autoindex(align = "r")

print(table1)