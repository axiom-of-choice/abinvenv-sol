import streamlit as st
from streamlit_chat import message
from streamlit_extras.colored_header import colored_header

############ DATA CONNECTORS ############
from connectors import DATA_SOURCE


############# AUTH #############
import streamlit as st

from autentication import streamlit_debug

streamlit_debug.set(flag=False, wait_for_client=True, host="localhost", port=8765)

from autentication import env

env.verify()

from autentication.authlib.auth import auth

########### Vector DB AND MODEL ############
import os
from dotenv import load_dotenv
from langchain.vectorstores import Pinecone
from config.config import *
from src.data.cohere_parser import parse
from src.utils import connect_index
from langchain.chains import RetrievalQAWithSourcesChain

# from langchain.chat_models import ChatOpenAI
# from langchain.llms.openai import BaseOpenAI
from langchain.embeddings import CohereEmbeddings
import glob
import traceback
from random import randint


import logging
from settings import logging_config
import logging.config

logging.config.dictConfig(logging_config)
logger = logging.getLogger(__name__)

load_dotenv()
# from config.config import AVAILABLE_LLMS


def main_page(user):
    username = user.get("username", "unknown")
    # st.success(f'`{username}` is authenticated')
    cf = user.get("cf", [1, 2, 3, 4, 5])
    logger.info(f"User: {username}, cf: {cf}")
    index = connect_index(PINECONE_INDEX_NAME, PINECONE_API_KEY, PINECONE_ENV)
    embeddings = CohereEmbeddings(
        cohere_api_key=COHERE_API_KEY, model=COHERE_MODEL_NAME
    )
    # vectorstore = Pinecone(index, embeddings.embed_query, 'text')
    vectorstore = Pinecone.from_existing_index(PINECONE_INDEX_NAME, embeddings, "text")
    temp_data = os.path.join(DATA_DIR, "tmp/")
    selected_model = st.sidebar.selectbox(
        "Select a Model to use", AVAILABLE_LLMS.keys()
    )
    # completion llm
    # llm = BaseOpenAI(
    #     openai_api_key=OPENAI_API_KEY,
    #     model_name='gpt-3.5-turbo',
    #     temperature=0.0
    # )
    llm = AVAILABLE_LLMS[selected_model]
    qa_with_sources = RetrievalQAWithSourcesChain.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(kwargs={"filter": {"cf": {"$in": cf}}}),
    )
    ########### Vector DB AND MODEL ############
    ###SESSION STATE###
    if "widget_key" not in st.session_state:
        st.session_state["widget_key"] = randint(0, 1000000)
    else:
        st.session_state["widget_key"] = st.session_state["widget_key"]
    if "generated" not in st.session_state:
        st.session_state["generated"] = [
            "I'm a ChatBot that only can answers questions, ask me anything!"
        ]
    else:
        st.session_state["generated"] = st.session_state["generated"]
    if "past" not in st.session_state:
        st.session_state["past"] = ["Hi!"]
    else:
        st.session_state["past"] = st.session_state["past"]
    with st.form("my-form", clear_on_submit=True):
        submitted = st.form_submit_button("submit")
        files = st.file_uploader(
            "Choose a file to upload and ask a question about it:",
            key=st.session_state["widget_key"],
            accept_multiple_files=True,
            kwargs={"clear_on_submit": True},
        )
        if len(files) > 0:
            for uploaded_file in files:
                if uploaded_file is not None:
                    # To read file as bytes:
                    bytes_data = uploaded_file.read()
                    # st.write("filename:", uploaded_file.name)
                    logger.info(f"Writing: {uploaded_file.name}")
                    with open(f"{temp_data}/{uploaded_file.name}", "wb") as f:
                        f.write(bytes_data)
            logger.info(f"Parsing files {files}")
        if submitted:
            st.session_state["widget_key"] = str(randint(1000, 100000000))
            try:
                parse(
                    temp_data,
                    output_filepath=None,
                    index_name=PINECONE_INDEX_NAME,
                    embeddings_model_name=COHERE_MODEL_NAME,
                    glob=GLOB,
                )
            except:
                logger.error("Error parsing files")
                logger.error(traceback.format_exc())
            files = []
            files = glob.glob(f"{temp_data}/*")
            for f in files:
                os.remove(f)
            logger.info(f"Files removed from {temp_data}")
    input_container = st.container()
    colored_header(label="", description="", color_name="blue-30")
    response_container = st.container()
    # User input
    ## Function for taking user provided prompt as input
    def get_text():
        input_text = st.text_input("You: ", "", key="input")
        return input_text

    ## Applying the user input box
    with input_container:
        user_input = get_text()
    # Response output
    ## Function for taking user prompt as input followed by producing AI generated responses
    def generate_response(prompt):
        chatbot = qa_with_sources
        response = chatbot(prompt)
        logger.debug(f"Response: {response}")
        return (
            response["answer"]
            + "\n (Source: "
            + response["sources"]
            + ")"
            + f" \n Generated by: {selected_model}"
        )

    ## Conditional display of AI generated responses as a function of user provided prompts
    with response_container:
        # clear = st.button("Clear chat")
        if user_input:
            response = generate_response(user_input)
            st.session_state.past.append(user_input)
            st.session_state.generated.append(response)
        if st.session_state["generated"]:
            for i in range(len(st.session_state["generated"])):
                message(st.session_state["past"][i], is_user=True, key=str(i) + "_user")
                message(st.session_state["generated"][i], key=str(i))
        # if clear:
        #     try:
        #         st.session_state['past'] = []
        #         st.session_state['generated'] = []
        #     except:
        #         pass
        # else:
        #     pass