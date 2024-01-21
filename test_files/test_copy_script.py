import subprocess

def copy_data():
    source_bucket = 'gs://hail-annotation-scripts/Hail-Annotate'
    destination_path = '/tmp/'

    # Run gsutil cp command using subprocess
    subprocess.run(['gsutil', '-m', 'cp', '-r', source_bucket, destination_path], check=True)
    subprocess.run(['ls', destination_path], check=True)
    
if __name__ == "__main__":
    copy_data()
