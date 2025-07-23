def parse_time(time_str):
    try:
        if "hour" in time_str:
            return int(float(time_str.split()[0]) * 60)
        elif "minute" in time_str:
            return int(time_str.split()[0])
        else:
            return None
    except:
        return None
    
    