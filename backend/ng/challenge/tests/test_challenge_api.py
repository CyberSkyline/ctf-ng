# import pytest
# import base64
# from ..models.Challenge import Challenge

# pytestmark = pytest.mark.db

# def test_challenge_import_endpoint(logged_in_client):
#     yaml = base64.urlsafe_b64encode(b'''
# x-challenge:
#   name: Basic Challenge
#   description: A simple challenge to test parsing
#   summary: A simple challenge to test parsing
#   icon: TbPuzzle
#   questions:
#     - name: flag
#       body: What is the flag?
#       points: 100
#       answer: CTF{test_flag}
#       max_attempts: 3
#   hints:
#     - body: Check the logs
#       preview: Log hint
#       deduction: 10
#   tags:
#     - test
#     - beginner
# services:
#   web:
#     image: nginx:latest
#     hostname: web-server
#     networks:
#       - boop
# networks:
#   boop:
#     internal: true
# ''')

#     response = logged_in_client.post('/ng/challenge/import', json={'yaml': yaml.decode('utf-8')})

#     challenge = Challenge.query.filter_by(name='Basic Challenge').first()

#     assert response.status_code == 200
#     assert len(challenge.hints) == 1
#     assert len(challenge.questions) == 1


# def test_challenge_import_endpoint_bad_yaml(logged_in_client):
#     yaml = base64.urlsafe_b64encode(b'''
# x-challenge:
#   description: A simple challenge to test parsing
#   icon: TbPuzzle
#   questions:
#     - name: flag
#       question: What is the flag?
#       points: 100
#       answer: CTF{test_flag}
#       max_attempts: 3
#   hints:
#     - hint: Check the logs
#       preview: Log hint
#       deduction: 10
#   tags:
#     - test
#     - beginner
# services:
#   web:
#     image: nginx:latest
#     hostname: web-server
#     networks:
#       - boop
# networks:
#   boop:
#     internal: true
# ''')

#     response = logged_in_client.post('/ng/challenge/import', json={'yaml': yaml.decode('utf-8')})
#     assert response.status_code == 400
