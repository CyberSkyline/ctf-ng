from typing import Literal
from attrs import define


# # This is the container block for all of the information that you can specify
# # for use in challenge development
# x-challenge:
# 	# Name of challenge
# 	name: Text
# 	# The description presented to players
# 	description: Text
# 	# The name of a https://fontawesome.com/icons representative of the challenge
# 	icon: Text
# 	# The questions block allows you to specify each question and it's 
# 	# respective answer
# 	questions:
# 		- name: Text
# 			question: Text
# 			points: 10
# 			answer: Regex
# 			max_attempts: 20
# 	# The hints block allows you to specify a list of hints that players
# 	# can open
# 	hints:
# 		- hint: 
# 				type: text
# 				content: Text
# 			preview: Text
# 			deduction: 10
# 		- hint: 
# 				type: image
# 				source: image/path
# 			preview: Text
# 			deduction: 10
# 		- hint: Text
# 			preview: Text
# 			deduction: 10
# 	# Optional string
# 	summary: Text
# 	# This block allows you to define templates so you can reuse them elsewhere, 
# 	# however you can define the templates anywhere that you like as long as you have used 
# 	# the anchor and alias functionality of yaml. This is simply a convenient centralized 
# 	# location
# 	template:
# 		flag-tmpl: &flag_tmpl "fake.bothify('SKY-????-####', letters=string.ascii_uppercase)"
# 	# This block is where you define all variables that you are going to utilize
# 	# and that you want us to randomize. You will need to provide both a default value
# 	# and a template for generation. 
# 	variables:
# 		# You can name the variables whatever you'd like provided that it's a valid
# 		# yaml key
# 		variable1:
# 			# The template functionality is a fragment of python code that can utilize 
# 			# any of the functions built into the python faker library: 
# 			# https://faker.readthedocs.io/en/master/index.html
# 			# Here you can see that we are using the alias functionality to reuse the 
# 			# template from above
# 			template: *flag_tmpl
# 			# The default value that you define here must also have a anchor that you 
# 			# alias later in the file as we will replace any instance of an alias with the
# 			# generated value. The anchor name does not need to be the same as the block
# 			# key
# 			default: &var1 Some default value
# 	tags:
# 		- Category
# 		- Category
# 		- Other
# services:
# 	service1:
# 		image: image
# 		# You will need to use the mapping form of the environment variables rather than 
# 		# the list form
# 		environment:
# 			VARIABLE1: *var1
@define
class Question:
    name: str
    question: str
    points: int
    answer: str
    max_attempts: int

@define
class TextHint:
    type: Literal['text']
    content: str

@define
class ImageHint:
    type: Literal['image']
    source: str

@define
class Hint:
    hint: TextHint | ImageHint | str
    preview: str
    deduction: int

@define
class Variable:
    template: str
    default: str

@define
class ChallengeInfo:
    name: str
    description: str
    questions: list[Question]
    icon: str | None = None
    hints: list[Hint] | None = None
    summary: str | None = None
    template: dict[str, str] | None = None
    variables: dict[str, Variable] | None = None
    tags: list[str] | None = None