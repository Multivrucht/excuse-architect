import random

def mock_call_text():
    """ Mock API rsponse for testing/demo purpose. """

    random_answers = {  
        0: "Yeah, I wasn't able to do that due to a Windows update loop.",
        1: "I left too late because I didnt want to come",
        2: "My apologies for the missed deadline. I experienced an unexpected personal capacity constraint that impacted my ability to finalize the deliverable. I take full responsibility and will ensure prompt submission.",
        3: "My sincere apologies for the delayed response. I regrettably overlooked your email amidst a high volume of priority tasks this past week. Thank you for your patience.",
        4: "The timeline shifted due to incomplete initial requirements. While I adjusted, this naturally impacted deliverables, which, as experienced professionals, I assume we all understand."}
    
    randomnumber = random.randrange(0,4,1)
    answer = random_answers.get(randomnumber)

    return str(answer)