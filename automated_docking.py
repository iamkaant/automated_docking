import requests
import time
import os
import sys
import yaml

def submit_and_download(api_token, input_file_path, memo, download_dir, poll_interval=20):
    """
    Submits a job to the API, polls for its completion, and downloads the output files.

    Parameters:
        api_token (str): The API token.
        input_file_path (str): The path to the input.smi file.
        memo (str): A memo string to send along with the job submission.
        poll_interval (int, optional): Seconds to wait between status polls. Default is 20 seconds.
        poll_interval (int, optional): Seconds to wait between status polls. Default is 5 seconds.

    Returns:
        tuple: A tuple containing the job_id (int) and a list of downloaded file paths.
    """
    base_url = "https://tldr.docking.org/api"
    
    # 1. Submit the job using POST with multipart/form-data
    submit_url = f"{base_url}/modules/build3d37/submit?token={api_token}"
    with open(input_file_path, 'rb') as file_handle:
        files = {"input.smi": file_handle}
        data = {"memo": memo}
        print(f"Submitting job with input file: {input_file_path} ...")
        response = requests.post(submit_url, files=files, data=data)
        response.raise_for_status()
        job_info = response.json()
    
    job_id = job_info.get("job_id")
    if not job_id:
        raise ValueError("Job submission failed: No job_id returned.")
    print(f"Job submitted successfully with job_id: {job_id}")

    # 2. Poll for job completion
    status_url = f"{base_url}/results/download/{job_id}"
    job_completed = False
    while not job_completed:
        params = {"token": api_token}
        status_response = requests.get(status_url, params=params)
        status_response.raise_for_status()
        status_data = status_response.json()
        status = status_data.get("status")
        print(f"Current job status: {status}")
        if status == "Completed":
            job_completed = True
        elif status == "Running":
            time.sleep(poll_interval)
        elif status == "Submitted":
            time.sleep(poll_interval)
        elif status == "Invalid input":
            raise ValueError("Job failed: Invalid SMILES.")
        else:
            # Handle unexpected statuses if necessary
            print("Encountered unexpected job status; waiting...")
            time.sleep(poll_interval)

    # 3. Download the output files
    output_list = status_data.get("output_list", [])
    if not output_list:
        print("No output files found.")
        return job_id, []
    
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    
    downloaded_files = []
    for output_file in output_list:
        download_url = f"{base_url}/results/download/{job_id}/{output_file}"
        params = {"token": api_token}
        print(f"Downloading {output_file} ...")
        with requests.get(download_url, params=params, stream=True) as r:
            r.raise_for_status()
            local_path = os.path.join(download_dir, output_file)
            with open(local_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:  # Filter out keep-alive new chunks
                        f.write(chunk)
            downloaded_files.append(local_path)
            print(f"Downloaded file saved to: {local_path}")

    return job_id, downloaded_files

if __name__ == "__main__":

    
    # Read parameters from YAML file
    with open('config.yaml', 'r') as config_file:
        config = yaml.safe_load(config_file)

    input_smi = config['input_smi']
    working_dir = os.getcwd()
    API_TOKEN = config['API_TOKEN']
    dock_executable = config.get('dock_executable', "/nfs/soft/dock/versions/dock38/DOCK/ucsfdock/docking/DOCK/dock64")
    dockfiles_dir = config['dockfiles_dir']
    
    
    memo_text = "Building of CYP3A4 ligands"
    
    # Create the smi file
    input_file = os.path.join(working_dir, "input.smi")
    with open(input_file, "w") as f:
        f.write(f'{input_smi} ligand')
    
    
    download_directory = os.path.join(working_dir, "build3d")
        
    

    # Building the ligands
    try:
        job_id, files = submit_and_download(API_TOKEN, input_file, memo_text, download_directory)
        print(f"Job {job_id} completed. Files downloaded: {files}")
    except Exception as e:
        print(f"An error occurred: {e}")
        
    if len(files) == 0:
        print("Failed to build ligand for docking. Exiting.")
        sys.exit(1)
        
    # Ungzip the files and create a list of all files ending with *db2.gz
    os.chdir(download_directory)
    import tarfile
    for file in files:
        with tarfile.open(file, "r:") as tar:
            tar.extractall(path=download_directory)
    db2_files = []
    for root, dirs, filenames in os.walk(download_directory):
        for filename in filenames:
            if filename.endswith(".db2.gz"):
                db2_files.append(os.path.join(root, filename))

    print(f"Found {len(db2_files)} .db2.gz files.")
        
    # Docking the ligands
    docking_directory = os.path.join(working_dir, "dock")
    if not os.path.exists(docking_directory):
        os.mkdir(docking_directory)
    os.chdir(docking_directory)
    # Creating a link to the dockfiles directory
    os.symlink(dockfiles_dir, "dockfiles")
    if not os.path.exists("output"):
        os.mkdir("output")
    os.chdir("output")
    os.symlink(f'{dockfiles_dir}/INDOCK', "INDOCK")
    # save all file paths in the split_database_index file
    with open("split_database_index", "w") as f:
        for file in db2_files:
            f.write(file + "\n")
    
    # Run the docking
    import subprocess
    subprocess.run([dock_executable], check=True)
    
    
    # Move the output files to the working directory
    os.chdir(os.path.join(docking_directory, "output"))
    # Check if test.mol2.gz exists
    if not os.path.exists("test.mol2.gz"):
        print("Docking failed. See output in dock/output/OUTDOCK. Exiting.")
    # unzipping the output files
    import gzip
    import shutil

    with gzip.open("test.mol2.gz", 'rb') as f_in:
        with open("test.mol2", 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    
    shutil.copy("test.mol2", "../../output.mol2")
    print("Docking completed.")