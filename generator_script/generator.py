import random
import pandas as pd
import os
from datetime import datetime

data_folder = "data"
if not os.path.exists(data_folder):
    os.makedirs(data_folder)

# Valid fault statuses
VALID_FAULT_STATUSES = ["None", "Overheat", "Under Voltage", "Over Voltage", "Frequency Error"]


def validate_inverter_data(data):
    errors = []
    # Validate PAC
    pac = data.get("PAC")
    if pac is None:
        errors.append("PAC sensor failure")
    elif not (1000 <= pac <= 5000):
        errors.append("PAC out of range (1000-5000)")

    # Validate energy_output
    energy_output = data.get("energy_output")
    if energy_output is None:
        errors.append("energy_output sensor failure")
    elif not (10000 <= energy_output <= 20000):
        errors.append("energy_output out of range (10000-20000)")

    # Validate energy_conversion_efficiency
    ece = data.get("energy_conversion_efficiency")
    if ece is None:
        errors.append("energy_conversion_efficiency sensor failure")
    elif not (90 <= ece <= 99):
        errors.append("energy_conversion_efficiency out of range (90-99)")

    # Validate performance_ratio
    pr = data.get("performance_ratio")
    if pr is None:
        errors.append("performance_ratio sensor failure")
    elif not (0.7 <= pr <= 0.95):
        errors.append("performance_ratio out of range (0.7-0.95)")

    # Validate system_uptime
    su = data.get("system_uptime")
    if su is None:
        errors.append("system_uptime sensor failure")
    elif not (98 <= su <= 100):
        errors.append("system_uptime out of range (98-100)")

    # Validate temperature
    temp = data.get("temperature")
    if temp is None:
        errors.append("temperature sensor failure")
    elif not (30 <= temp <= 60):
        errors.append("temperature out of range (30-60)")

    # Validate input_voltage
    iv = data.get("input_voltage")
    if iv is None:
        errors.append("input_voltage sensor failure")
    elif not (500 <= iv <= 700):
        errors.append("input_voltage out of range (500-700)")

    # Validate output_voltage
    ov = data.get("output_voltage")
    if ov is None:
        errors.append("output_voltage sensor failure")
    elif not (220 <= ov <= 240):
        errors.append("output_voltage out of range (220-240)")

    # Validate frequency
    freq = data.get("frequency")
    if freq is None:
        errors.append("frequency sensor failure")
    elif not (49 <= freq <= 51):
        errors.append("frequency out of range (49-51)")

    # Validate fault_status
    fs = data.get("fault_status")
    if fs is None:
        errors.append("fault_status missing")
    elif fs not in VALID_FAULT_STATUSES and fs != "Sensor Failure":
        errors.append("fault_status not valid")

    return errors

def generate_inverter_data(inverter_id):
    failure_rate = 0.01  # 3% chance for a sensor reading to fail

    def maybe_value(val, failure_rate=failure_rate):
        return val if random.random() > failure_rate else None

    # Generate key sensor readings
    temperature = maybe_value(round(random.uniform(30, 56), 2))
    input_voltage = maybe_value(round(random.uniform(515, 700), 2))
    frequency = maybe_value(round(random.uniform(49, 51), 2))

    #Determine fault status based on the other factors
    if temperature is None or input_voltage is None or frequency is None:
        fault_status = "Sensor Failure"
    else:
        if temperature > 55:
            fault_status = "Overheat"
        elif input_voltage < 520:
            fault_status = "Under Voltage"
        elif input_voltage > 680:
            fault_status = "Over Voltage"
        elif frequency < 49.5 or frequency > 50.5:
            fault_status = "Frequency Error"
        else:
            fault_status = "None"

    return {
        "id": f"Inverter_{inverter_id}",
        "PAC": maybe_value(round(random.uniform(1000, 5000), 2)),
        "energy_output": maybe_value(round(random.uniform(10000, 20000), 2)),
        "energy_conversion_efficiency": maybe_value(round(random.uniform(90, 100), 2)),
        "performance_ratio": maybe_value(round(random.uniform(0.7, 0.96), 2)),
        "system_uptime": maybe_value(round(random.uniform(98, 100), 2)),
        "temperature": temperature,
        "fault_status": fault_status,
        "input_voltage": input_voltage,
        "output_voltage": maybe_value(round(random.uniform(220, 241), 2)),
        "frequency": frequency,
    }


def save_data_to_file(data_frame, file_name, file_type="json"):

    file_path = os.path.join(data_folder, file_name)
    if file_type == "json":
        data_frame.to_json(file_path, orient="records", indent=4)
        
    print(f"Saved {len(data_frame)} records to {file_name}")

def generate_batch_inverter_data(inverters_num=60, num_files=4):
    valid_inverters = []
    #invalid_inverters = []

    for i in range(inverters_num):
        data = generate_inverter_data(i+1)
        errors = validate_inverter_data(data)
        if errors:
            # data["invalid_description"] = "; ".join(errors)
            # invalid_inverters.append(data)
            continue
        else:
            valid_inverters.append(data)

    valid_df = pd.DataFrame(valid_inverters)
    #invalid_df = pd.DataFrame(invalid_inverters)

    #Needed to generate more than 1 files
    batch_size = max(1, len(valid_inverters) // num_files) # -> I want to split the data into 4 files
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

    for file_index in range(num_files):
        start_index = file_index * batch_size
        end_index = min(start_index + batch_size, len(valid_df))

        batch_data = valid_df.iloc[start_index:end_index] #Using iloc for DataFrame slicing
        if not batch_data.empty:
            file_name = f"inverter-data-{file_index+1}_{timestamp}.json"
            save_data_to_file(batch_data, file_name)

    # if not invalid_df.empty:
    #     file_name = f"invalid_inverter_data_{timestamp}.json"
    #     save_data_to_file(invalid_df, file_name)
    #
    #print(f"Generated {len(valid_df)} valid and {len(invalid_df)} invalid records.")

    print(f"Generated {len(valid_df)} valid records.")
