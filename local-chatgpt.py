import chainlit as cl
import ollama

cl.config.timeout = 300

@cl.on_chat_start
async def start_chat():
    cl.user_session.set(
        "interaction",
        [
            {
                "role": "system",
                "content": "You are a helpful assistant.",
            }
        ],
    )

    msg = cl.Message(content="")
    start_message = "Hello, I'm your 100% local alternative to ChatGPT running on DeepSeek-R1. How can I help you today?"
    
    for token in start_message:
        await msg.stream_token(token)
    
    await msg.send()

@cl.step(type="tool")
async def tool(input_message):
    interaction = cl.user_session.get("interaction")

    if not interaction:
        cl.user_session.set(
            "interaction",
            [{"role": "system", "content": "You are a helpful assistant."}]
        )
        interaction = cl.user_session.get("interaction")

    interaction.append({"role": "user", "content": input_message})

    response = await cl.make_async(ollama.chat)(
        model="deepseek-r1", messages=interaction
    )

    content = response['message']['content']
    cleaned_content = content.split('</think>\n\n')[-1].strip()

    interaction.append({"role": "assistant", "content": cleaned_content})

    return {"message": {"content": cleaned_content}}


@cl.on_message
async def main(message: cl.Message):
    tool_res = await tool(message.content)

    print("Cleaned Response:", tool_res['message']['content'])

    msg = cl.Message(content="")
    for token in tool_res['message']['content']:
        await msg.stream_token(token)
    
    await msg.send()


if __name__ == "__main__":
    cl.run("local-chatgpt.py")
