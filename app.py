import streamlit as st
import requests

# 1. ENHANCED VALIDATION (UAE/GCC STANDARD)
def validate_chassis(vin):
    vin = vin.upper().strip()
    if len(vin) != 17:
        return False, "Chassis number must be exactly 17 characters."
    if any(c in vin for c in "IOQ"):
        return False, "Invalid characters: I, O, and Q are never used."

    # ISO 3779 Check Digit Math
    weights = [8, 7, 6, 5, 4, 3, 2, 10, 0, 9, 8, 7, 6, 5, 4, 3, 2]
    transliteration = {
        'A':1, 'B':2, 'C':3, 'D':4, 'E':5, 'F':6, 'G':7, 'H':8,
        'J':1, 'K':2, 'L':3, 'M':4, 'N':5, 'P':7, 'R':9, 'S':2,
        'T':3, 'U':4, 'V':5, 'W':6, 'X':7, 'Y':8, 'Z':9
    }
    
    total = 0
    for i, char in enumerate(vin):
        val = int(char) if char.isdigit() else transliteration.get(char, 0)
        total += val * weights[i]
    
    check_digit = total % 11
    expected = 'X' if check_digit == 10 else str(check_digit)
    
    if vin[8] != expected:
        return "WARN", f"Import Spec Detected (Expected '{expected}' at pos 9)."
    
    return True, "Valid GCC Standard Chassis Number"

# 2. ADVANCED EXTRACTION
def fetch_technical_specs(vin):
    url = f"https://vpic.nhtsa.dot.gov/api/vehicles/decodevin/{vin}?format=json"
    try:
        response = requests.get(url).json()
        # Convert the list of results into a clean dictionary
        data = {item['Variable']: item['Value'] for item in response['Results'] if item['Value']}
        return data
    except Exception:
        return None

# 3. STREAMLIT UI
st.set_page_config(page_title="UAE Vehicle VIN Decoder", page_icon="🇦🇪", layout="centered")
st.title("UAE Vehicle VIN Decoder")
st.write("Extracting detailed specs: Engine, Fuel, Body, and Region.")

chassis_input = st.text_input("Enter 17-digit Chassis Number:", placeholder="e.g. 5YJ3E1EBXJF...").upper().strip()

if st.button("Extract Full Details"):
    if not chassis_input:
        st.warning("Please enter a Chassis number.")
    else:
        status, msg = validate_chassis(chassis_input)
        
        if status == False:
            st.error(f"❌ {msg}")
        else:
            if status == "WARN":
                st.warning(f"⚠️ {msg}")
            else:
                st.success(f"✅ {msg}")
            
            with st.spinner('Decoding technical specifications...'):
                specs = fetch_technical_specs(chassis_input)
            
            if specs:
                # Layout for the details
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.header("🏢 Basic Info")
                    st.write(f"**Manufacturer:** {specs.get('Make', 'N/A')}")
                    st.write(f"**Model:** {specs.get('Model', 'N/A')}")
                    st.write(f"**Year:** {specs.get('Model Year', 'N/A')}")
                    st.write(f"**Body Type:** {specs.get('Body Class', 'N/A')}")

                with col2:
                    st.header("⚙️ Engine & Power")
                    st.write(f"**Fuel Type:** {specs.get('Fuel Type - Primary', 'N/A')}")
                    st.write(f"**Engine Size:** {specs.get('Displacement (L)', 'N/A')} Liters")
                    st.write(f"**Cylinders:** {specs.get('Engine Number of Cylinders', 'N/A')}")
                    st.write(f"**Engine Configuration:** {specs.get('Engine Configuration', 'N/A')}")

                with col3:
                    st.header("📐 Interior & Build")
                    st.write(f"**Doors:** {specs.get('Doors', 'N/A')}")
                    st.write(f"**Seat Number:** {specs.get('Number of Seats', 'N/A')}")
                    st.write(f"**Manufactured In:** {specs.get('Plant Country', 'N/A')}")
                    st.write(f"**Plant Location:** {specs.get('Plant City', 'N/A')}")

                # Display a special alert for UAE Spec vs US/Japan Spec
                st.divider()
                st.subheader("📍 Market Specification Hint")
                if "UNITED STATES" in str(specs.get('Plant Country')).upper():
                    st.info("This vehicle was manufactured in the USA. If found in UAE, it is likely a 'US Spec' import.")
                elif "JAPAN" in str(specs.get('Plant Country')).upper():
                    st.info("This vehicle was manufactured in Japan. It could be GCC or Japan spec.")
                else:
                    st.info(f"Manufactured in: {specs.get('Plant Country', 'Unknown Region')}")

            else:
                st.error("Could not retrieve data for this chassis number.")