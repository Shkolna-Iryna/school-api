from openai_client import client

def moderate_text(text):
    response = client.moderations.create(
        model="omni-moderation-latest",
        input=text
    )

    return response.results[0].flagged


def moderate_image(image_url):
    response = client.moderations.create(
        model="omni-moderation-latest",
        input={
            "type": "input_image",
            "image_url": image_url
        }
    )

    return response.results[0].flagged