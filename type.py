(lambda args: [(scope := [[{}, {}]]), (cond := []), (loops := []), (libs := {}), (wl := type("wl", (), {"__init__": (lambda self, func: ([setattr(self, "func", func), setattr(self, "broke", False), None][-1])), "__iter__": (lambda self: [self][0]), "__next__": (lambda self: ([next(iter("")) if self.broke else None, None if (self.func()) else next(iter(""))])), "stop": (lambda self: (setattr(self, "broke", True)))})), scope[-1][0].__setitem__("int", 0), scope[-1][0].__setitem__("bool", False), scope[-1][0].__setitem__("float", 0.1), scope[-1][0].__setitem__("str", ""), scope[0][1].__setitem__("get_type", (lambda args : [scope.append([{}]), scope[-1][0].__setitem__("type", scope[0][0][str(type(args[0]))[8:-2]]), scope[-1][0]["type"], scope.pop()][-2]))])(__import__("sys").argv)