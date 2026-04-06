# pages/blood_ai.py
# This file lives in the pages/ folder for multi-page navigation.
# It simply executes the main blood_ai logic.
# Your full blood_ai.py stays UNCHANGED in the root folder.
# This file just imports and runs everything from it.

import streamlit as st
import importlib.util, sys, os

# Load blood_ai.py from root directory
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("blood_ai", os.path.join(root, "blood_ai.py"))
mod  = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
