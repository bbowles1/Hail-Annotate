import subprocess

def ls_data():
    source_bucket = 'gs://hail-annotation-scripts/Hail-Annotate/'

    # Run gsutil cp command using subprocess
    subprocess.run(['gsutil', 'ls', source_bucket], check=True)
    subprocess.run(['ls'], check=True)
    subprocess.run(['pwd'], check=True)
    subprocess.run(['ls ~'], check=True)

if __name__ == "__main__":
    ls_data()
