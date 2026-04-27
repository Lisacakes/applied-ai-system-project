from services import PetService

def test_time():
    assert PetService.validate_and_normalize("Walk", "08:00", 30)[0]
    assert not PetService.validate_and_normalize("Walk", "25:00", 30)[0]

def test_title():
    _, _, t = PetService.validate_and_normalize("  FEED   DOG  ", "12:00", 30)
    assert t == "feed dog"

def test_duration():
    assert not PetService.validate_and_normalize("Walk", "08:00", 0)[0]