#!/usr/bin/env python3
import os
import shutil
import subprocess
import tarfile
import urllib.request
import zipfile
from datetime import datetime
import requests
import plistlib

from colorama import Fore, Style, init
from tqdm import tqdm

init(autoreset=True)


def print_banner():
    banner = f"""
{Fore.MAGENTA}
  _____                _____ _
 / ____|              / ____| |
| (___  _ __ ___  ___| (___ | | ___
 \\___ \\| '__/ _ \\/ _ \\\\___ \\| |/ _ \\
 ____) | | |  __/  __/____) | |  __/
|_____/|_|  \\___|\\___|_____/|_|\\___|

{Fore.CYAN}
    .-.     .-.     .-.     .-.     .-.     .-.     .-.     .-.     .-.
   (_  )   (_  )   (_  )   (_  )   (_  )   (_  )   (_  )   (_  )   (_  )
     /       /       /       /       /       /       /       /       /
    (       (       (       (       (       (       (       (       (
     `-'     `-'     `-'     `-'     `-'     `-'     `-'     `-'     `-'
{Style.RESET_ALL}
"""
    print(banner)


class Helper:
    def add_execute_permissions(self, file_path):
        try:
            subprocess.run(["chmod", "+x", file_path], check=True)
            print(
                f"{Fore.GREEN}Added execute permissions to {file_path}{Style.RESET_ALL}"
            )
        except subprocess.CalledProcessError as e:
            print(
                f"{Fore.RED}Error adding execute permissions to {file_path}: {e}{Style.RESET_ALL}"
            )
            raise

    def cleanup_temp_dir(self, temp_dir, keep_files):
        try:
            print(f"{Fore.YELLOW}Cleaning up temporary directory...{Style.RESET_ALL}")
            abs_keep = {os.path.abspath(f) for f in keep_files}
            for item in os.listdir(temp_dir):
                item_path = os.path.join(temp_dir, item)
                if os.path.abspath(item_path) in abs_keep:
                    continue
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                else:
                    os.remove(item_path)
            print(f"{Fore.GREEN}Cleanup completed successfully{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Cleanup failed: {e}{Style.RESET_ALL}")
            raise

    def add_execute_permissions_app(self, file_path):
        try:
            subprocess.run(["chmod", "-R", "775", file_path], check=True)
            print(
                f"{Fore.GREEN}Added execute permissions to {file_path}{Style.RESET_ALL}"
            )
        except subprocess.CalledProcessError as e:
            print(
                f"{Fore.RED}Error adding execute permissions to {file_path}: {e}{Style.RESET_ALL}"
            )
            raise

    def download_file(self, url, dest):
        if os.path.exists(dest):
            print(
                f"{Fore.YELLOW}{dest} already exists, skipping download{Style.RESET_ALL}"
            )
            return
        try:
            print(f"{Fore.YELLOW}Downloading {url} to {dest}{Style.RESET_ALL}")
            with tqdm(
                unit="B", unit_scale=True, miniters=1, desc=url.split("/")[-1]
            ) as t:
                def reporthook(blocknum, blocksize, totalsize):
                    t.total = totalsize
                    t.update(blocknum * blocksize - t.n)

                urllib.request.urlretrieve(url, dest, reporthook)
        except Exception as e:
            print(f"{Fore.RED}Error downloading {url}: {e}{Style.RESET_ALL}")
            raise

    def extract_zip(self, file_path, dest_dir):
        try:
            print(f"{Fore.YELLOW}Extracting {file_path} to {dest_dir}{Style.RESET_ALL}")
            with zipfile.ZipFile(file_path, "r") as zip_ref:
                zip_ref.extractall(dest_dir)
        except Exception as e:
            print(f"{Fore.RED}Error extracting {file_path}: {e}{Style.RESET_ALL}")
            raise

    def extract_tar_gz(self, file_path, dest_dir):
        try:
            print(f"{Fore.YELLOW}Extracting {file_path} to {dest_dir}{Style.RESET_ALL}")
            with tarfile.open(file_path, "r:gz") as tar_ref:
                tar_ref.extractall(dest_dir)
        except Exception as e:
            print(f"{Fore.RED}Error extracting {file_path}: {e}{Style.RESET_ALL}")
            raise

    def set_app_icon(self, icon_source, icon_dest, plist_path):
        try:
            shutil.copy(icon_source, icon_dest)
            print(f"{Fore.GREEN}Icon copied to app bundle{Style.RESET_ALL}")
            with open(plist_path, "rb") as f:
                plist = plistlib.load(f)
            plist["CFBundleIconFile"] = "icon.icns"
            with open(plist_path, "wb") as f:
                plistlib.dump(plist, f)
            print(f"{Fore.GREEN}Info.plist updated with icon{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Error setting icon: {e}{Style.RESET_ALL}")
            raise


def get_ghidra_download_url():
    url = "https://api.github.com/repos/NationalSecurityAgency/ghidra/releases/latest"
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        print(
            f"{Fore.RED}Error: Request to GitHub API timed out after 30 seconds. "
            f"Check your internet connection and try again.{Style.RESET_ALL}"
        )
        raise
    except requests.exceptions.ConnectionError:
        print(
            f"{Fore.RED}Error: Could not connect to the GitHub API. "
            f"Check your internet connection or whether GitHub is reachable.{Style.RESET_ALL}"
        )
        raise
    except requests.exceptions.HTTPError:
        if response.status_code == 403 and "0" == response.headers.get(
            "X-RateLimit-Remaining", ""
        ):
            reset_time = response.headers.get("X-RateLimit-Reset", "unknown")
            if reset_time.isdigit():
                reset_time_str = datetime.fromtimestamp(
                    int(reset_time)
                ).strftime("%Y-%m-%d %H:%M:%S")
            else:
                reset_time_str = reset_time
            print(
                f"{Fore.RED}Error: GitHub API rate limit exceeded. "
                f"Rate limit resets at: {reset_time_str}. "
                f"Wait and try again, or use a GitHub token for authenticated requests.{Style.RESET_ALL}"
            )
        else:
            print(
                f"{Fore.RED}Error: GitHub API returned HTTP {response.status_code} "
                f"for {url}{Style.RESET_ALL}"
            )
        raise
    except requests.exceptions.RequestException as e:
        print(
            f"{Fore.RED}Error: Failed to reach GitHub API: {e}{Style.RESET_ALL}"
        )
        raise

    try:
        data = response.json()
    except ValueError:
        print(
            f"{Fore.RED}Error: GitHub API returned an unexpected response "
            f"(not valid JSON). The API may be down or the response format changed.{Style.RESET_ALL}"
        )
        raise

    if "assets" not in data or not isinstance(data["assets"], list) or len(data["assets"]) == 0:
        print(
            f"{Fore.RED}Error: GitHub API response did not contain any release assets. "
            f"The Ghidra release structure may have changed.{Style.RESET_ALL}"
        )
        raise RuntimeError("No release assets found in GitHub API response")

    if "browser_download_url" not in data["assets"][0]:
        print(
            f"{Fore.RED}Error: GitHub API response is missing the expected "
            f"'browser_download_url' field. The API schema may have changed.{Style.RESET_ALL}"
        )
        raise RuntimeError("Missing browser_download_url in GitHub API response")

    return data["assets"][0]["browser_download_url"]


def main():
    java_url = "https://download.java.net/java/GA/jdk25.0.2/b1e0dfa218384cb9959bdcb897162d4e/10/GPL/openjdk-25.0.2_macos-aarch64_bin.tar.gz" #https://jdk.java.net/archive/

    print(f"{Fore.CYAN}Fetching latest Ghidra release info...{Style.RESET_ALL}")
    ghidra_url = get_ghidra_download_url()

    cwd = os.getcwd()
    temp_dir = os.path.join(cwd, "ghidra_install")
    applet_path = os.path.join(temp_dir, "Ghidra-OSX-Launcher-Script.scpt")
    app_dir = os.path.join(temp_dir, "Ghidra.app")
    jdk_dir = os.path.join(temp_dir, "jdk")
    ghidra_dir = os.path.join(temp_dir, "ghidra")
    icon_source = os.path.join(cwd, "icons", "icon.icns")
    icon_dest = os.path.join(app_dir, "Contents", "Resources", "icon.icns")
    info_plist_path = os.path.join(app_dir, "Contents", "Info.plist")
    launch_script_path = os.path.join(
        temp_dir, "Ghidra.app/Contents/Resources/ghidra/support/launch.sh"
    )
    ghidra_run_path = os.path.join(
        temp_dir, "Ghidra.app/Contents/Resources/ghidra/ghidraRun"
    )

    os.makedirs(temp_dir, exist_ok=True)

    helper = Helper()

    try:
        subprocess.run(["osacompile", "-o", app_dir, applet_path], check=True)
        print(f"{Fore.GREEN}Created Ghidra.app at {app_dir}{Style.RESET_ALL}")
        helper.set_app_icon(icon_source, icon_dest, info_plist_path)

        jdk_tar_path = os.path.join(temp_dir, "openjdk.tar.gz")
        helper.download_file(java_url, jdk_tar_path)
        helper.extract_tar_gz(jdk_tar_path, jdk_dir)
        jdk_extracted_dir = os.path.join(jdk_dir, os.listdir(jdk_dir)[0])
        jdk_final_app_dir = os.path.join(app_dir, "Contents", "Resources", "jdk")
        shutil.copytree(jdk_extracted_dir, jdk_final_app_dir)

        ghidra_zip_path = os.path.join(temp_dir, "ghidra.zip")
        helper.download_file(ghidra_url, ghidra_zip_path)
        helper.extract_zip(ghidra_zip_path, ghidra_dir)
        ghidra_extracted_dir = os.path.join(ghidra_dir, os.listdir(ghidra_dir)[0])
        ghidra_final_app_dir = os.path.join(app_dir, "Contents", "Resources", "ghidra")
        shutil.copytree(ghidra_extracted_dir, ghidra_final_app_dir)

        helper.add_execute_permissions(launch_script_path)
        helper.add_execute_permissions(ghidra_run_path)
        helper.add_execute_permissions_app(app_dir)

        print(
            f"{Fore.GREEN}Ghidra installation completed successfully!{Style.RESET_ALL}"
        )
        helper.cleanup_temp_dir(temp_dir, [app_dir, applet_path])

    except Exception as e:
        print(f"{Fore.RED}Installation failed: {e}{Style.RESET_ALL}")
        exit(1)


if __name__ == "__main__":
    print_banner()
    main()
