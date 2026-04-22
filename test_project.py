import pytest
from unittest.mock import patch
from datetime import datetime, timezone
from project import get_filename, get_date, create_gif


def test_get_filename():
    '''
    Tests the exact name: get_filename -> test_get_filename
    '''
    test_date = datetime(2026, 4, 22)
    
    assert get_filename(test_date, 'Madrid') == 'nightwindow_20260422_madrid.gif'
    assert get_filename(test_date, 'New York') == 'nightwindow_20260422_new_york.gif'
    assert get_filename(test_date, '  London  ') == 'nightwindow_20260422_london.gif'


def test_get_date():
    '''
    Tests the exact name: get_date -> test_get_date
    '''
    with patch('project.get_option', return_value='1'):
        result = get_date()
        assert isinstance(result, datetime)
        assert result.hour == 21
        assert result.minute == 0
        assert result.tzinfo == timezone.utc


def test_create_gif():
    '''
    Tests the exact name: create_gif -> test_create_gif
    '''
    with patch('os.listdir', return_value=[]):
        with pytest.raises(FileNotFoundError):
            create_gif(folder='empty_folder')

    with patch('os.listdir', return_value=['f1.png', 'f2.png']):
        with patch('project.Image.open'):
            with patch('project.Image.Image.save'):
                result = create_gif(output_name='test.gif')
                assert result == 'test.gif'