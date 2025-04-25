def print_hex_ascii( data,extra_msg=""):
    if extra_msg != "":
        extra_msg = f"({extra_msg})"
		
    print(f"In ASCII{extra_msg} : {data.decode(errors='replace')}")
    print(f"In HEX {extra_msg} : {' '.join(f'{b:02X}' for b in data)}")
    print("\n")

