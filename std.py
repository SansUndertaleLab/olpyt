(lambda args : [scope := [[{}, {}]], libs := {}, scope[-1][1].__setitem__("print", (lambda args : [scope.append([{}, {}]), print(*args, sep = ""), None, scope.pop()][-2])), scope[-1][1].__setitem__("input", (lambda args : [scope.append([{}]), scope[-1][0].__setitem__("inpt", input(args[0])), scope[-1][0]["inpt"], scope.pop()][-2]))])(__import__("sys").argv)