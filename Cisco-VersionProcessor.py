import paramiko
import traceback
import csv

# SSH configuration
ssh_username = "xxx"
ssh_password = "xxx"
ssh_port = 22

# File paths
file_path = "C:\\Users\\x\\"
hosts_file_name = "..\\Hosts\HomeLab.txt"
error_file_name = "error_hostnames.txt"

device_info = {}
ssh_client = paramiko.SSHClient()

def execute_command(host):
    print('connecting to host:' + host)
    ssh_client.connect(hostname=host, username=ssh_username, password=ssh_password, port=ssh_port)
    stdin, stdout, stderr = ssh_client.exec_command("show version")
    return stdout.read().decode("utf-8")
    #temporary code to test without ssh
    #version_file = open(file_path + "/version.txt", "r")
    #version_output = version_file.read()
    #version_file.close()
    #return version_output


def parse_show_version_output(host, output):
    print('Parsing output of the show version command')

    lines = output.splitlines()
    index = 0
    for line in lines:
        if "SW Version" in line:
            index += 2
            break
        index += 1

    model = lines[index].split()[3]
    software_version = lines[index].split()[4]

    print('Model Number is: ' + model)
    print('Software version is: ' + software_version)

    # Add the device hostname to the device_info dictionary
    key = f"{model}_{software_version}"
    if key not in device_info:
        device_info[key] = []
    device_info[key].append(host)


def write_excel_files():
    # Write the CSV files for each device model and software version
    for key, hostnames in device_info.items():
        model, software_version = key.split("_")
        filename = f"{model}_{software_version}.csv"
        with open(filename, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Hostname"])
            for hostname in hostnames:
                writer.writerow([hostname])


def main():
    success_count = 0
    failed_count = 0

    print('Reading HostNames file\n')

    # Reading hostnames
    hosts_file = open(file_path + "/" + hosts_file_name, "r")
    hosts = hosts_file.readlines()
    hosts_file.close()

    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    for host in hosts:
        try:
            print('\nProcessing %d / %d ....\n' % (success_count + failed_count + 1, len(hosts)))

            host = host.strip()
            output = execute_command(host)
            parse_show_version_output(host, output)
            ssh_client.close()

            success_count += 1
        except Exception as e:
            failed_count += 1

            print('Got exception for host: ', host)
            with open(error_file_name, 'a') as f:
                f.write(host + ',' + str(e) + ',' + traceback.format_exc() + '\n')

    print('\nwriting excel file\n')
    write_excel_files()

    print('%d hosts processed successfully' % success_count)
    print('%d hosts failed processing' % failed_count)


if __name__ == "__main__":
    main()
