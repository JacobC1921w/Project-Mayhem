import requests

# URL to retrieve data from
url = "https://raw.githubusercontent.com/frk1/hazedumper/master/csgo.cs"

try:
    # Retrieve data from URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Retrieve the data as text and do some cleanup
        data = response.text
        data = data.replace("        public const Int32 ", "    ")
        data = data.replace("    public const Int32 ", "")
        data = data.replace("    public static ", "")
        data = data.replace("class netvars\n", "class netvars:")
        data = data.replace("class signatures\n", "class signatures:")
        data = data.replace("namespace hazedumper", "")
        data = data.replace("using System", "")
        data = data.replace(" =", ":int =")
        data = data.replace('{', "")
        data = data.replace(';', "")
        data = data.replace('}', "")
        data = data.replace("//", "")
        data = '\n'.join(data.split('\n')[3:])
        data = data.strip()

        # Write the cleaned up data to a file
        with open("offsets.py", "w") as f:
            f.write(data)
        print("Data retrieved and saved to file.")
    else:
        print(f"Request failed with status code {response.status_code}")
except requests.exceptions.RequestException as e:
    print(f"Request failed with error: {e}")
except IOError as e:
    print(f"Error writing to file: {e}")
