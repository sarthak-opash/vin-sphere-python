import streamlit as st
import json
import os

st.set_page_config(
    page_title="VIN Decoder",
    page_icon="🚗",
    layout="centered"
)

# =====================================================
# MANUFACTURER FILES
# =====================================================

def get_manufacturer_file(vin):

    vin = vin.upper()

    if len(vin) < 3:
        return None

    wmi = vin[:3]

    # ==================
    # NISSAN
    # ==================

    if wmi[1] == "N":
        return "nissan.json"

    # ==================
    # TOYOTA
    # ==================

    if wmi[1] == "T":
        return "toyota.json"

    return None


# =====================================================
# LOAD JSON
# =====================================================

def load_rules(vin):

    json_file = get_manufacturer_file(vin)

    if not json_file:
        return None

    with open(json_file, "r", encoding="utf-8") as f:
        return json.load(f)


# =====================================================
# DECODE VIN
# =====================================================

def decode_vin(vin):

    rules = load_rules(vin)

    if not rules:
        return None

    wmi = vin[:3]

    pos4 = vin[3]
    pos5 = vin[4]
    pos6 = vin[5]
    pos7 = vin[6]
    pos8 = vin[7]

    year_code = vin[9]
    plant_code = vin[10]

    result = {}

    # -------------------------------------------------
    # WMI DETAILS
    # -------------------------------------------------

    wmi_info = rules.get("wmi", {}).get(wmi, {})

    result["Manufacturer"] = rules.get(
        "manufacturer",
        "Unknown"
    )

    result["Country"] = wmi_info.get(
        "country",
        "Unknown"
    )

    result["Vehicle Type"] = wmi_info.get(
        "vehicle_type",
        "Unknown"
    )

    # -------------------------------------------------
    # POSITION 4
    # -------------------------------------------------

    result["Series"] = rules.get(
        "position_4",
        {}
    ).get(
        pos4,
        "Unknown"
    )

    # -------------------------------------------------
    # POSITION 5
    # -------------------------------------------------

    body_info = rules.get(
        "position_5",
        {}
    ).get(
        pos5,
        {}
    )

    result["Body Type"] = body_info.get(
        "body_type",
        "Unknown"
    )

    result["Possible Models"] = body_info.get(
        "possible_models",
        []
    )

    # -------------------------------------------------
    # POSITION 6
    # -------------------------------------------------

    result["Engine"] = rules.get(
        "position_6",
        {}
    ).get(
        pos6,
        "Unknown"
    )

    # -------------------------------------------------
    # POSITION 7
    # -------------------------------------------------

    result["Trim / Safety"] = rules.get(
        "position_7",
        {}
    ).get(
        pos7,
        "Unknown"
    )

    # -------------------------------------------------
    # POSITION 8
    # -------------------------------------------------

    trans_info = rules.get(
        "position_8",
        {}
    ).get(
        pos8,
        {}
    )

    result["Drive Type"] = trans_info.get(
        "drive_type",
        "Unknown"
    )

    result["Transmission"] = trans_info.get(
        "transmission",
        "Unknown"
    )

    # -------------------------------------------------
    # YEAR
    # -------------------------------------------------

    result["Model Year"] = rules.get(
        "year_codes",
        {}
    ).get(
        year_code,
        "Unknown"
    )

    # -------------------------------------------------
    # PLANT
    # -------------------------------------------------

    result["Plant Code"] = plant_code

    # -------------------------------------------------
    # SERIAL NUMBER
    # -------------------------------------------------

    result["Serial Number"] = vin[11:]

    return result


# =====================================================
# UI
# =====================================================

st.title("🚗 VIN Decoder")

vin = st.text_input(
    "Enter 17 Digit VIN"
).strip().upper()

if st.button("Decode Vehicle"):

    if len(vin) != 17:

        st.error(
            "VIN must be exactly 17 characters."
        )

    else:
        

        result = decode_vin(vin)
        st.write("Detected WMI:", vin[:3])

        if result is None:

            st.error(
                "Manufacturer not supported."
            )

        else:

            st.success(
                "Vehicle Decoded Successfully"
            )

            st.subheader("Vehicle Details")

            col1, col2 = st.columns(2)

            with col1:

                st.write("### Manufacturer Information")

                st.write(
                    f"**Manufacturer:** {result['Manufacturer']}"
                )

                st.write(
                    f"**Country:** {result['Country']}"
                )

                st.write(
                    f"**Vehicle Type:** {result['Vehicle Type']}"
                )

                st.write(
                    f"**Model Year:** {result['Model Year']}"
                )

            with col2:

                st.write("### Vehicle Specification")

                st.write(
                    f"**Series:** {result['Series']}"
                )

                st.write(
                    f"**Body Type:** {result['Body Type']}"
                )

                st.write(
                    f"**Engine:** {result['Engine']}"
                )

                st.write(
                    f"**Transmission:** {result['Transmission']}"
                )

                st.write(
                    f"**Drive Type:** {result['Drive Type']}"
                )

                st.write(
                    f"**Trim / Safety:** {result['Trim / Safety']}"
                )

            st.write("### Possible Models")

            if result["Possible Models"]:
                for model in result["Possible Models"]:
                    st.write(f"• {model}")
            else:
                st.write("Unknown")

            st.write("### VIN Information")

            st.write(
                f"**Plant Code:** {result['Plant Code']}"
            )

            st.write(
                f"**Serial Number:** {result['Serial Number']}"
            )

            st.write("### Raw JSON")

            st.json(result)