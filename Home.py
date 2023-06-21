import hashlib
import streamlit as st
import face_rec
from face_rec import r
import numpy as np
from streamlit_webrtc import webrtc_streamer
import av


def set_custom_page_config():
    st.set_page_config(page_title='Attendance System', layout='wide')

set_custom_page_config()

st.header('Attendance System using Face Recognition')
col1, col2 = st.columns(2)

with col1:
    st.subheader('Sign In')
    rolein = st.radio('Role:', ('Administrator', 'Invigilator'))
    username = st.text_input('Username',key="username_input")
    password = st.text_input('Password', type='password',key="password_input")  
    sign_in_button = st.button('Sign In')

if sign_in_button:
    
        role = rolein if rolein == 'Administrator' else 'Invigilator'

        stored_hashed_password = r.hget(f'{role}:register', username)

        stored_password_string = stored_hashed_password.decode('utf-8')   

        if stored_password_string is not None:
            entered_hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
            if entered_hashed_password == stored_password_string.strip():
                st.success(f'Sign-in successful. Welcome, {role}!')
                st.session_state["role"] = role                                 #
                st.session_state["username"] = username                         #
            else:
                st.error('Incorrect password. Please try again.')
        else:
            st.error('Username not found. Please try again.')

        if "role" in st.session_state and "username" in st.session_state:
            if st.button("Logout"):
                del st.session_state["role"]
                del st.session_state["username"]
                rolein = None

        st.info("Logged out successfully.")
with col2:
    st.subheader('Sign Up')
    role = st.radio('Role:', ('Administrator', 'Student', 'Invigilator'))

    if role == 'Administrator':
        institution_name = st.text_input('Institution Name')
        new_username = st.text_input('Username')
        new_password = st.text_input('Password', type='password')

        if st.button('Sign Up'):
            hashed_password = hashlib.sha256(new_password.encode()).hexdigest()

            r.hset(f'{role}:register', new_username, hashed_password)
            st.success('Administrator registered successfully!')

    elif role == 'Invigilator':
        course_code = st.radio('Course Code:', ('CP01', 'CP08', 'CP09', 'CP15'))
        new_username = st.text_input('Username')
        new_password = st.text_input('Password', type='password')

        if st.button('Sign Up'):
            hashed_password = hashlib.sha256(new_password.encode()).hexdigest()

            r.hset(f'{role}:register', new_username, hashed_password)
            st.success('Invigilator registered successfully!')
    else:
        registration_form = face_rec.RegistrationForm()

        person_name = st.text_input(label='Name',placeholder='Full Name of Candidate')
        role = st.text_input(label='Token Number',placeholder='Token number of Candidate')
        course = st.radio("Select Course Code", ["CP01", "CP08", "CP09","CP15"])                 

        def video_callback_func(frame):
            img = frame.to_ndarray(format='bgr24') 
            reg_img, embedding = registration_form.get_embedding(img)
            if embedding is not None:
                with open('face_embedding.txt',mode='ab') as f:
                    np.savetxt(f,embedding)
            
            return av.VideoFrame.from_ndarray(reg_img,format='bgr24')

        webrtc_streamer(key='registration',video_frame_callback=video_callback_func)

        if st.button('Submit'):
            return_val = registration_form.save_data_in_redis_db(person_name,role)
            if return_val == True:
                st.success(f"{person_name} registered sucessfully")
            elif return_val == 'name_false':
                st.error('Please enter the name: Name cannot be empty or spaces')
                
            elif return_val == 'file_false':
                st.error('face_embedding.txt is not found. Please refresh the page and execute again.')
            
with st.spinner("Loading Models and Connecting to Redis db ..."):

    st.success('Model loaded successfully')
    st.success('Redis db successfully connected')