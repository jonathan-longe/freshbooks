import pytest
from config import Config
from toFreshbooks import main, round_duration_to_quarter_hour
import responses
import io
import json


@responses.activate
def test_watson_json_output_is_sent_freshbooks_api(monkeypatch):
    responses.add(responses.POST, Config.FRESHBOOK_TIME_ENTRY_URL, status=200)
    responses.add(responses.POST, Config.FRESHBOOK_TIME_ENTRY_URL, status=200)

    sample_watson_time_frames = [
        {
            "id": "05417f8126504289bd202817b8543273",
            "project": "review demo with Eric",
            "start": "2022-08-31T09:10:32-07:00",
            "stop": "2022-08-31T09:30:39-07:00",
            "tags": [
                "YK"
            ]
        },
        {
            "id": "0a968f5228f549dfb425f4dc15656e58",
            "project": "setup demo CCSD-111",
            "start": "2022-08-25T08:30:04-07:00",
            "stop": "2022-08-25T17:00:03-07:00",
            "tags": [
                "YK"
            ]
        }
    ]

    monkeypatch.setattr('sys.stdin', io.StringIO(json.dumps(sample_watson_time_frames)))
    main()
    first_payload = json.loads(responses.calls[0].request.body.decode())
    second_payload = json.loads(responses.calls[1].request.body.decode())
    assert type(first_payload) is dict
    assert "time_entry" in first_payload
    assert first_payload['time_entry']['duration'] == 1800
    assert type(second_payload) is dict
    assert "time_entry" in second_payload
    assert second_payload['time_entry']['duration'] == 30600


duration_examples = [
    (900, 900),
    (901, 900),
    (1207, 1800),
    (30599, 30600)
]


@pytest.mark.parametrize("duration", duration_examples)
def test_time_frame_duration_is_rounded_to_nearest_900_seconds(duration):
    inputted, expected = duration
    assert round_duration_to_quarter_hour(inputted) == expected
