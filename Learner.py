__author__ = 'philippe'
import World
import threading
import time

discount = 0.3
actions = World.actions
states = []
Q = {}
# 通过两个循环，生成了所有可能的状态，并将这些状态添加到states列表中。
for i in range(World.x):
    for j in range(World.y):
        states.append((i, j))

# 对于每个状态，创建了一个临时字典temp，并将每个动作的初始Q值设置为0.1。
# 然后，通过World模块的set_cell_score函数，将状态和对应动作的Q值存储在游戏环境中，并将temp字典存储在Q字典中。
for state in states:
    temp = {}
    for action in actions:
        temp[action] = 0.1
        World.set_cell_score(state, action, temp[action])
    Q[state] = temp

for (i, j, c, w) in World.specials:
    for action in actions:
        Q[(i, j)][action] = w
        World.set_cell_score((i, j), action, w)

# 定义了一个名为do_action的函数，用于执行给定的动作。
# 它首先获取当前的状态s和得分r。根据给定的动作，调用World模块的try_move函数来移动棋子。
# 然后，获取移动后的状态s2和更新后的得分r。最后，返回执行动作前后的状态、动作、奖励和下一个状态。
def do_action(action):
    s = World.player
    r = -World.score
    if action == actions[0]:
        World.try_move(0, -1)
    elif action == actions[1]:
        World.try_move(0, 1)
    elif action == actions[2]:
        World.try_move(-1, 0)
    elif action == actions[3]:
        World.try_move(1, 0)
    else:
        return
    s2 = World.player
    r += World.score
    return s, action, r, s2

# 定义了一个名为max_Q的函数，用于在给定状态s下找到具有最大Q值的动作。
# 它遍历状态s对应的Q值字典，并返回具有最大Q值的动作和对应的Q值。
def max_Q(s):
    val = None
    act = None
    for a, q in Q[s].items():
        if val is None or (q > val):
            val = q
            act = a
    return act, val

# 定义了一个名为inc_Q的函数，用于更新Q值。
# 它根据给定的状态s、动作a、学习率alpha和增量inc，更新Q值表中对应的Q值，并将更新后的Q值存储在游戏环境中。
def inc_Q(s, a, alpha, inc):
    Q[s][a] *= 1 - alpha
    Q[s][a] += alpha * inc
    World.set_cell_score(s, a, Q[s][a])


def run():
    global discount
    time.sleep(1)
    alpha = 1
    t = 1
    while True:
        # Pick the right action
        s = World.player
        max_act, max_val = max_Q(s)
        (s, a, r, s2) = do_action(max_act)

        # Update Q
        max_act, max_val = max_Q(s2)
        inc_Q(s, a, alpha, r + discount * max_val)

        # Check if the game has restarted
        t += 1.0
        if World.has_restarted():
            World.restart_game()
            time.sleep(0.01)
            t = 1.0

        # Update the learning rate
        alpha = pow(t, -0.1)

        # MODIFY THIS SLEEP IF THE GAME IS GOING TOO FAST.
        time.sleep(0.1)


t = threading.Thread(target=run)
t.daemon = True
t.start()
World.start_game()
