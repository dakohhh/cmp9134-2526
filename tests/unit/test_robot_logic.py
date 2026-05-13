from app.robot.service import RobotService
from app.robot.schemas.get_robot_status_response_schema import Position
from app.robot.schemas.move_robot_request_schema import NavigationEnum


def test_move_right_mid_field() -> None:
    result = RobotService.calculate_new_position(Position(x=5, y=5), NavigationEnum.RIGHT)
    assert result == Position(x=6, y=5)

def test_move_right_at_boundary() -> None:
    result = RobotService.calculate_new_position(Position(x=20, y=5), NavigationEnum.RIGHT)
    assert result == Position(x=20, y=5)


def test_move_left_mid_field() -> None:
    result = RobotService.calculate_new_position(Position(x=5, y=5), NavigationEnum.LEFT)
    assert result == Position(x=4, y=5)

def test_move_left_at_boundary() -> None:
    result = RobotService.calculate_new_position(Position(x=0, y=5), NavigationEnum.LEFT)
    assert result == Position(x=0, y=5)


def test_move_up_mid_field() -> None:
    result = RobotService.calculate_new_position(Position(x=5, y=5), NavigationEnum.UP)
    assert result == Position(x=5, y=4)

def test_move_up_at_boundary() -> None:
    result = RobotService.calculate_new_position(Position(x=5, y=0), NavigationEnum.UP)
    assert result == Position(x=5, y=0)


def test_move_down_mid_field() -> None:
    result = RobotService.calculate_new_position(Position(x=5, y=5), NavigationEnum.DOWN)
    assert result == Position(x=5, y=6)

def test_move_down_at_boundary() -> None:
    result = RobotService.calculate_new_position(Position(x=5, y=20), NavigationEnum.DOWN)
    assert result == Position(x=5, y=20)
