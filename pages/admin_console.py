# streamlit_app.py

# import streamlit as st
# from st_files_connection import FilesConnection
#
# # Create connection object and retrieve file contents.
# # Specify input format is a csv and to cache the result for 600 seconds.
# conn = st.experimental_connection('s3', type=FilesConnection)
# df = conn.read("abinveb-bucket/common.txt", input_format="text", ttl=600)
#
# # Print results.
#
# st.write(df)

import streamlit as st

from dotenv import load_dotenv

load_dotenv()

from connectors import DATA_SOURCE

from settings import logging_config
import logging.config

logging.config.dictConfig(logging_config)
logger = logging.getLogger(__name__)
from config import BACKGROUNDS_DIR, TITLE
from random import randint


def upload_background():
    with st.form("my-form", clear_on_submit=True):
        files = st.file_uploader(
            "Choose a file to upload as background",
            key=st.session_state["widget_background_key"],
            accept_multiple_files=False,
            kwargs={"clear_on_submit": True},
            type=["png", "jpg", "jpeg"],
        )
        submitted = st.form_submit_button("submit")
        if submitted:
            logger.debug(f"Setting background")
            if files is not None:
                # To read file as bytes:
                uploaded_file = files.read()
                with open(BACKGROUNDS_DIR, "wb") as f:
                    logger.debug(f"Writing background")
                    f.write(uploaded_file)
                    logger.debug(f"Writed background")
            st.write("Background set!")
        st.session_state["widget_key"] = str(randint(1000, 100000000))


def add_logo():
    with st.form("my-form", clear_on_submit=True):
        files = st.file_uploader(
            "Choose a file to upload as Logo",
            key=st.session_state["widget_logo_key"],
            accept_multiple_files=False,
            kwargs={"clear_on_submit": True},
            type=["png", "jpg", "jpeg"],
        )
        submitted = st.form_submit_button("submit")
        if submitted:
            logger.debug(f"Setting logo")
            if files is not None:
                # To read file as bytes:
                uploaded_file = files.read()
                with open(BACKGROUNDS_DIR, "wb") as f:
                    logger.debug(f"Writing logo")
                    f.write(uploaded_file)
                    logger.debug(f"Writed logo")


def change_title():
    global TITLE
    with st.form() as form:
        title = st.text_input("Title", key=st.session_state["widget_title_key"])
        submitted = st.form_submit_button("submit")
        if submitted:
            logger.debug(f"Setting title")
            if title is not None:
                st.session_state["widget_title_key"] = title
                TITLE = title
                logger.debug(f"Setted title")
                st.write("Title set!")


def admin_console(user):
    if "widget_background_key" not in st.session_state:
        st.session_state["widget_background_key"] = randint(0, 1000000)
    else:
        st.session_state["widget_background_key"] = st.session_state["widget_background_key"]
    if "widget_logo_key" not in st.session_state:
        st.session_state["widget_logo_key"] = randint(0, 1000000)
    else:
        st.session_state["widget_logo_key"] = st.session_state["widget_logo_key"]
    if user["su"] == 1:
        st.subheader("Welcome to the admin console.")
        upload_background()
        selected_datasource = st.selectbox("Select a Datasoruce", DATA_SOURCE.keys())
        obj = DATA_SOURCE[selected_datasource]
        obj().interface()
    else:
        st.write("You are not authorized to view this page.")
