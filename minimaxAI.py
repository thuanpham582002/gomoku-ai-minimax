import math

import pisqpipe
import util

score = {
    'ONE': 10,
    'TWO': 100,
    'THREE': 1000,
    'FOUR': 100000,
    'FIVE': 10000000,
    'BLOCKED_ONE': 1,
    'BLOCKED_TWO': 10,
    'BLOCKED_THREE': 100,
    'BLOCKED_FOUR': 10000
}

board = util.Board(sizex=20, sizey=20)

INF = float("inf")

nodes_cnt = 0
checkmate_node_cnt = 0

"""
Tạo một bảng mới với kích thước được chỉ định bởi tham số sizex và sizey.
"""


# set new size for board
def newBoard(sizex=20, sizey=20):
    global board
    board = util.Board(sizex=sizex, sizey=sizey)


"""
 Điều khiển chức năng của thuật toán Minimax. minimax_depth là độ sâu của thuật toán Minimax, 
 trong khi checkmate_depth là độ sâu của thuật toán Minimax trong trường hợp kiểm tra trạng thái chiến thắng.
"""


def minimax(minimax_depth=4, checkmate_depth=6):
    global nodes_num, checkmate_node
    '''
    Khởi tạo các biến toàn cục để đếm số nút được duyệt trong thuật toán Minimax
    '''
    nodes_num = 0
    checkmate_node = 0
    check_1 = checkmate(board, role=1, checkmate_depth=checkmate_depth)
    check_2 = checkmate(board, role=2, checkmate_depth=checkmate_depth)
    if check_1:
        return check_1
    # remove because it will stop BLOCKED_THREE form BLOCKED_FOUR (unnecessary)
    elif check_2:
        return check_2
    else:
        x, y = _minimax(minimax_depth=minimax_depth)
        return x, y


"""
Hàm giúp xác định nước đi tốt nhất cho AI thông qua thuật toán Minimax với độ sâu minimax_depth.
"""


def _minimax(minimax_depth):
    x, y = maxValue(board, 0, minimax_depth, -INF, INF, return_pattern=True)
    return x, y


"""
Hàm này thực hiện tìm kiếm trạng thái tốt nhất cho AI trong một số nước đi được đưa ra.
Nó sử dụng thuật toán Minimax với độ sâu max_depth, giới hạn tối đa và tối thiểu alpha và beta.
Nếu return_pattern là True, hàm sẽ trả về tất cả các điểm có thể cùng với điểm số của chúng.
"""


def maxValue(board, depth, max_depth, alpha, beta, return_pattern=False):
    global nodes_num
    nodes_num += 1
    if depth == max_depth:
        return board.evaluate()
    v = -INF
    point_scores = {}
    candidates = board.candidate()
    if len(candidates) > 3:
        candidates = candidates[:min(10, math.ceil(len(candidates) * (1 / 3 + 1 / (3 * depth + 3))))]
    if depth == 0 and len(candidates) == 1:
        x, y = candidates[0]
        return x, y
    for x, y in candidates:
        board[x, y] = 1
        check_2 = False
        if depth == 0:
            check_2 = checkmate(board, role=2, checkmate_depth=6)
        if check_2:
            v_new = -INF + 1
        else:
            v_new = minValue(board, depth + 1, max_depth, alpha, beta)
        v = max(v, v_new)
        if return_pattern:
            point_scores[(x, y)] = v_new
        board[x, y] = 0
        if v >= beta:
            return v
        alpha = max(alpha, v)
    if return_pattern:
        scores = sorted(list(point_scores.items()), key=lambda x: x[1], reverse=True)
        x, y = scores[0][0]
        return x, y
    else:
        return v


"""
 Hàm này giúp xác định nước đi tốt nhất cho người chơi khác. 
 Nó cũng sử dụng thuật toán Minimax, tuy nhiên, với nước đi của đối thủ và trả về giá trị tối thiểu.
"""


def minValue(board, depth, max_depth, alpha, beta):
    global nodes_num
    nodes_num += 1
    if depth == max_depth:
        return board.evaluate()
    v = INF
    candidates = board.candidate()
    if len(candidates) > 3:
        candidates = candidates[:min(10, math.ceil(len(candidates) * (1 / 3 + 1 / (3 * depth + 3))))]
    for x, y in candidates:
        board[x, y] = 2
        v_new = maxValue(board, depth + 1, max_depth, alpha, beta)
        v = min(v, v_new)
        board[x, y] = 0
        if v <= alpha:
            return v
        beta = min(beta, v)
    return v


"""
 Hàm này giúp kiểm tra xem một trong hai người chơi đã thắng. Nó sử dụng thuật toán Minimax với độ sâu checkmate_depth để kiểm tra.
 """


def checkmate(board, role, checkmate_depth=6):
    return maxNode_checkmate(board, role, 0, checkmate_depth)


"""
Hàm này giúp xác định liệu nếu tới lượt AI, 
nó có thể đánh thắng trong tối đa max_depth bước hay không. Nếu có, nó trả về True - x,y.
"""


def maxNode_checkmate(board, role, depth, max_depth):
    global checkmate_node
    checkmate_node += 1
    winner = board.get_winner()
    if winner == role:
        return True
    elif winner == 3 - role:
        return False
    if depth >= max_depth:
        return False

    for x, y in board.candidate():

        if role == 1:
            point_role_score = board.score_1[(x, y)]
        elif role == 2:
            point_role_score = board.score_2[(x, y)]

        if point_role_score >= 2 * score['THREE']:
            board[x, y] = role
            m = minNode_checkmate(board, role, depth + 1, max_depth)
            board[x, y] = 0
            if m:
                if depth == 0:
                    return x, y
                else:
                    return True
    return False


"""
Hàm này giúp xác định liệu nếu đến lượt người chơi khác, AI có thể ngăn chặn đối thủ đánh thắng trong tối đa max_depth bước hay không. Nếu có, nó trả về True.
"""


def minNode_checkmate(board, role, depth, max_depth):
    global checkmate_node
    checkmate_node += 1
    winner = board.get_winner()
    if winner == role:
        return True
    elif winner == 3 - role:
        return False
    if depth >= max_depth:
        return False
    candidate = []
    for x, y in board.candidate():
        if board.score_2[(x, y)] + board.score_1[(x, y)] >= score['BLOCKED_FOUR']:
            board[x, y] = 3 - role

            m = maxNode_checkmate(board, role, depth + 1, max_depth)
            board[x, y] = 0
            if m:
                candidate.append((x, y))
            else:
                return False
    if candidate == []:
        return False
    else:
        return True

# if __name__ == '__main__':
# board = util.Board(sizex=7, sizey=7)
# board[3, 3] = 1
# board[2, 3] = 2
# board[3, 2] = 1
# board[1, 2] = 2
# board[2, 2] = 1
# board[3, 4] = 2
# board.step_count = 6
# for i in range(board.size[1]):
#     for j in range(board.size[0]):
#         print(board.score_2[(j,i)],end=" ")
#     print("\n")

# print(board._get_point_score(x=4, y=5, role=2))
# print(board._get_point_score)
# for i in range(16):
#     flip = False
#     if board.step_count % 2 == 1:
#         flip = True
#     x, y = minimax(flip=flip)
#     print(x, y, flip)
#     if flip == False:
#         board[x, y] = 1
#     elif flip == True:
#         board[x, y] = 2
#     print(board)
# for i in range(board.size[1]):
#     for j in range(board.size[0]):
#         print(board.score_2[(j,i)],end=" ")
#     print("\n")
