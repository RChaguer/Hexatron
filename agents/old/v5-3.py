import numpy as np, random, time
from collections import deque

def rotation_to_position(rotation: int) -> np.ndarray:
    return [np.array(rotation) for rotation in [(0, -1), (1, -1), (1, 0), (0, 1), (-1, 1), (-1, 0)]][rotation % 6]

def calculate_new_position(position: np.ndarray, rotation: int, move: int) -> np.ndarray:
    return position + rotation_to_position(rotation + move)

def calculate_new_state(position: np.ndarray, rotation: int, move: int) -> np.ndarray:
    return position + rotation_to_position(rotation + move), (rotation + move) % 6

def is_inside_bounds(position: np.ndarray) -> bool:
    return (0 <= position[0] < 13 and 0 <= position[1] < 13 and
            13 // 2 <= position[0] + position[1] < 13 * 3 // 2)

def is_occupied(board: np.ndarray, position: np.ndarray) -> bool:
    return board[position[1], position[0]]

def is_playable(board: np.ndarray, position: np.ndarray) -> bool:
    return is_inside_bounds(position) and not is_occupied(board, position)

def calculate_distance_between(board: np.ndarray, position_a: np.ndarray, position_b: np.ndarray) -> int:
    new_board = board.copy()
    new_board[position_a[1], position_a[0]] = 1
    new_board[position_b[1], position_b[0]] = 0

    queue = deque([(position_a, 1)])
    while len(queue) > 0:
        position, distance = queue.popleft()

        if np.array_equal(position, position_b):
            return distance

        for i in range(-3, 3):
            new_position, _ = calculate_new_state(position, 0, i)

            if is_playable(new_board, new_position):
                new_board[new_position[1], new_position[0]] = 1
                queue.append((new_position, distance + 1))
    return None

def calculate_available_area(board: np.ndarray, position: np.ndarray) -> int:
    new_board = board.copy()
    
    count = 0
    queue = [position]
    while len(queue) > 0:
        position = queue.pop()

        for i in range(-3, 3):
            new_position, _ = calculate_new_state(position, 0, i)

            if is_playable(new_board, new_position):
                new_board[new_position[1], new_position[0]] = 1
                count += 1
                queue.append(new_position)
    return count

def get_best_move_with_ray_casting(board: np.ndarray, player_position: np.ndarray, player_rotation: int, opponent_position: np.ndarray, opponent_rotation: int, playable_moves: list) -> int:
    hit_max = []
    for move in playable_moves:
        new_board = board.copy()
        position, _ = calculate_new_state(player_position, player_rotation, move)
        difference = position - player_position
        ray_position = player_position + difference
        new_board[ray_position[1], ray_position[0]] = 1
        ray_length = 1
        while is_playable(new_board, ray_position + difference):
            ray_position += difference
            ray_length += 1
            new_board[ray_position[1], ray_position[0]] = 1
            
        distance_to_opponent = calculate_distance_between(new_board, position, opponent_position)
        best_area_with_opponent = calculate_available_area(new_board, opponent_position)
        best_area_without_opponent = 0
        if distance_to_opponent is None and calculate_available_area(new_board, position) >= best_area_with_opponent:
            return move
        for new_move in range(-2, 3):
            new_ray_position, _ = calculate_new_state(ray_position, player_rotation + move, new_move)
            if is_playable(new_board, new_ray_position):
                distance_to_opponent = calculate_distance_between(new_board, new_ray_position, opponent_position)

                if distance_to_opponent is None:
                    best_area_without_opponent = max(best_area_without_opponent, calculate_available_area(new_board, new_ray_position))
                else:
                    best_area_without_opponent = max(best_area_without_opponent, calculate_available_area(new_board, new_ray_position) / 2)
        hit_max += [(best_area_without_opponent / (best_area_with_opponent if best_area_with_opponent != 0 else 1e-3), move)]
    return max(hit_max)[1]

def get_best_move(board: np.ndarray, player_position: np.ndarray, player_rotation: int, opponent_position: np.ndarray, opponent_rotation: int) -> int:
    playable_moves = [move for move in range(-2, 3) if is_playable(board, calculate_new_state(player_position, player_rotation, move)[0])]
    if playable_moves == []: return 0

    return get_best_move_with_ray_casting(board, player_position, player_rotation, opponent_position, opponent_rotation, playable_moves)

def generate_move(board: np.ndarray, positions: list, rotations: list) -> int:
    board = board.sum(axis=2)
    player_position, player_rotation = np.array(positions[0]), rotations[0]
    opponent_position, opponent_rotation = np.array(positions[1]), rotations[1]

    t0 = time.time()

    move = get_best_move(board, player_position, player_rotation, opponent_position, opponent_rotation)

    t = time.time() - t0
    assert t <= 1, "Exceeded execution time with %.3f seconds" % t

    return move
