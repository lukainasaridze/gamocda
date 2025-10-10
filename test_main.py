import pytest
from main import is_valid 

def test_valid_plate():
    assert is_valid("AB-123-CD") == True

def test_invalid_length():
    assert is_valid("AB-12-CD") == False