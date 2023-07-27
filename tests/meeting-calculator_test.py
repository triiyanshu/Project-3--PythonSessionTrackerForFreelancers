import meeting_calculator

def test_calculate_meeting_duration():
    assert meeting_calculator.calculate_meeting_duration(30, 2) == 60
    assert meeting_calculator.calculate_meeting_duration(45, 3) == 135
    assert meeting_calculator.calculate_meeting_duration(60, 4) == 240