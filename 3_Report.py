import streamlit as st
from Home import set_custom_page_config
from Home import face_rec
from Home import rolein

set_custom_page_config()
st.subheader('Reporting')

name = 'attendance:logs'

print(f"Rolein report = {rolein}")
if (rolein == 'Invigilator' or 'Administrator'):

    def load_logs(name, end=-1):
        logs_list = face_rec.r.lrange(name, start=0, end=end) 
        return logs_list

    tab1, tab2 = st.tabs(['Registered Data', 'Logs'])

    with tab1:
        if st.button('Refresh Data'):
            with st.spinner('Retrieving Data from Redis DB ...'):
                redis_face_db = face_rec.retrive_data(name='academy:register')
                if 'Name' in redis_face_db.columns and 'Token Number' in redis_face_db.columns:
                    st.dataframe(redis_face_db[['Name', 'Token Number']])
                else:
                    st.write("Columns 'Name' and 'Token Number' not found in the DataFrame.")

    with tab2:
        cp01, cp08, cp09, cp15 = st.tabs(['CP01', 'CP08', 'CP09', 'CP15'])

        if st.button('Refresh Logs'):
            logs = load_logs(name=name)
            roles = [log.decode().split('@')[1] for log in logs]

            for log, role in zip(logs, roles):
                if role.startswith('TTC01'):
                    with cp01:
                        st.write(log)

                if role.startswith('TTC08'):
                    with cp08:
                        st.write(log)

                if role.startswith('TTC09'):
                    with cp09:
                        st.write(log)

                if role.startswith('TTC15'):
                    with cp15:
                        st.write(log)

else:
    st.warning("You are not authorized to access this page !!!")

