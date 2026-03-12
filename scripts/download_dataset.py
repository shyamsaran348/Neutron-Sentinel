import os
import subprocess
import zipfile

def download_and_extract(dataset="cicdataset/cicids2017", output_dir="data/raw"):
    os.makedirs(output_dir, exist_ok=True)
    
    # Check if files already exist
    if os.path.exists(os.path.join(output_dir, "MachineLearningCSV")):
        print(f"Dataset already exists in {output_dir}")
        return
        
    print(f"Downloading {dataset} to {output_dir} using Kaggle API...")
    try:
        subprocess.run([
            "kaggle", "datasets", "download", "-d", dataset, "-p", output_dir
        ], check=True)
        
        # Extract the zip file
        zip_path = os.path.join(output_dir, f"{dataset.split('/')[-1]}.zip")
        if os.path.exists(zip_path):
            print(f"Extracting {zip_path}...")
            if zipfile.is_zipfile(zip_path):
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(output_dir)
                print("Extraction complete. Cleaning up zip file.")
                os.remove(zip_path)
            else:
                print("Downloaded file is not a valid zip archive.")
        else:
            print("Zip file not found after download.")
            
    except subprocess.CalledProcessError as e:
        print(f"Error downloading dataset. Ensure Kaggle API is configured. {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    download_and_extract()
