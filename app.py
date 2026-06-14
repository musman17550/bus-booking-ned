import streamlit as st
import mysql.connector
import pandas as pd
from datetime import date


def get_connection():
    return mysql.connector.connect(
        host=st.secrets["mysql"]["host"],
        port=st.secrets["mysql"]["port"],
        user=st.secrets["mysql"]["user"],
        password=st.secrets["mysql"]["password"],
        database=st.secrets["mysql"]["database"]
    )


st.title("Pakistan Intercity Bus Booking System")


menu = st.sidebar.selectbox("Menu", [
    "Add Passenger",
    "View Passengers",
    "Search Passenger",
    "Update Passenger",
    "Delete Passenger",
    "View Bookings",
    "View Payments"
])


if menu == "Add Passenger":
    st.header("Register New Passenger")
    with st.form("passenger_form"):
        passenger_id = st.number_input("Passenger ID", min_value=1, step=1)
        passenger_name = st.text_input("Full Name")
        cnic = st.text_input("CNIC (e.g. 35201-1234567-1)")
        gender = st.selectbox("Gender", ["Male", "Female"])
        phone = st.text_input("Phone")
        city = st.selectbox("City", ["Lahore", "Karachi", "Islamabad", "Peshawar", "Multan", "Quetta", "Faisalabad", "Hyderabad"])
        registration_date = st.date_input("Registration Date", value=date.today())
        submitted = st.form_submit_button("Register Passenger")

        if submitted:
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    """INSERT INTO passengers 
                    (passenger_id, passenger_name, cnic, gender, phone, city, registration_date) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                    (passenger_id, passenger_name, cnic, gender, phone, city, registration_date)
                )
                conn.commit()
                cursor.close()
                conn.close()
                st.success("Passenger registered successfully!")
            except Exception as e:
                st.error(f"Error: {e}")


elif menu == "View Passengers":
    st.header("All Passengers")
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM passengers")
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        cursor.close()
        conn.close()
        df = pd.DataFrame(rows, columns=columns)
        st.dataframe(df)
    except Exception as e:
        st.error(f"Error: {e}")


elif menu == "Search Passenger":
    st.header("Search Passenger")
    search_term = st.text_input("Search by Name or CNIC")
    if search_term:
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """SELECT * FROM passengers 
                WHERE passenger_name LIKE %s OR cnic LIKE %s""",
                (f"%{search_term}%", f"%{search_term}%")
            )
            results = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            cursor.close()
            conn.close()
            df = pd.DataFrame(results, columns=columns)
            if not df.empty:
                st.dataframe(df)
            else:
                st.warning("No passenger found.")
        except Exception as e:
            st.error(f"Error: {e}")


elif menu == "Update Passenger":
    st.header("Update Passenger Record")
    passenger_id = st.number_input("Enter Passenger ID to update", min_value=1, step=1)

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM passengers WHERE passenger_id = %s", (passenger_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if result:
            with st.form("update_form"):
                passenger_name = st.text_input("Full Name", value=result[1])
                cnic = st.text_input("CNIC", value=result[2])
                gender = st.selectbox("Gender", ["Male", "Female"], index=0 if result[3] == "Male" else 1)
                phone = st.text_input("Phone", value=result[4])
                city = st.text_input("City", value=result[5])
                updated = st.form_submit_button("Update Passenger")

                if updated:
                    try:
                        conn = get_connection()
                        cursor = conn.cursor()
                        cursor.execute(
                            """UPDATE passengers 
                            SET passenger_name=%s, cnic=%s, gender=%s, phone=%s, city=%s 
                            WHERE passenger_id=%s""",
                            (passenger_name, cnic, gender, phone, city, passenger_id)
                        )
                        conn.commit()
                        cursor.close()
                        conn.close()
                        st.success("Passenger updated successfully!")
                    except Exception as e:
                        st.error(f"Error: {e}")
        else:
            st.warning("No passenger found with this ID.")
    except Exception as e:
        st.error(f"Error: {e}")


elif menu == "Delete Passenger":
    st.header("Delete Passenger Record")
    passenger_id = st.number_input("Enter Passenger ID to delete", min_value=1, step=1)

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM passengers WHERE passenger_id = %s", (passenger_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if result:
            st.write(f"Name: {result[1]}")
            st.write(f"CNIC: {result[2]}")
            st.write(f"City: {result[5]}")
            st.write(f"Phone: {result[4]}")

            if st.button("Confirm Delete"):
                try:
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM passengers WHERE passenger_id = %s", (passenger_id,))
                    conn.commit()
                    cursor.close()
                    conn.close()
                    st.success("Passenger deleted successfully!")
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("No passenger found with this ID.")
    except Exception as e:
        st.error(f"Error: {e}")


elif menu == "View Bookings":
    st.header("All Bookings with Details")
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                b.booking_id,
                p.passenger_name,
                p.cnic,
                bs.bus_number,
                bs.bus_type,
                r.origin_city,
                r.destination_city,
                b.travel_date,
                b.seat_number,
                b.booking_status
            FROM bookings b
            JOIN passengers p ON b.passenger_id = p.passenger_id
            JOIN buses bs ON b.bus_id = bs.bus_id
            JOIN routes r ON bs.route_id = r.route_id
        """)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        cursor.close()
        conn.close()
        df = pd.DataFrame(rows, columns=columns)
        st.dataframe(df)
    except Exception as e:
        st.error(f"Error: {e}")


elif menu == "View Payments":
    st.header("All Payments")
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                pay.payment_id,
                p.passenger_name,
                r.origin_city,
                r.destination_city,
                pay.ticket_fare,
                pay.service_charges,
                pay.total_amount,
                pay.payment_method,
                pay.payment_status
            FROM payments pay
            JOIN bookings b ON pay.booking_id = b.booking_id
            JOIN passengers p ON b.passenger_id = p.passenger_id
            JOIN buses bs ON b.bus_id = bs.bus_id
            JOIN routes r ON bs.route_id = r.route_id
        """)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        cursor.close()
        conn.close()
        df = pd.DataFrame(rows, columns=columns)
        st.dataframe(df)
    except Exception as e:
        st.error(f"Error: {e}")