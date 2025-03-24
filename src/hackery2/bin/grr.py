#!/usr/bin/env python3
import subprocess
import re

def convert_ssh_to_https(url):
    # Match SSH URLs like: git@github.com:username/repo.git
    ssh_pattern = r'git@([^:]+):([^/]+)/(.+?)(?:\.git)?$'
    match = re.match(ssh_pattern, url)
    
    if match:
        host, username, repo = match.groups()
        return f"https://{host}/{username}/{repo}"
    
    # If it's already HTTPS or doesn't match the pattern, return as is
    return url

def main():
    try:
        # Run git remote -v
        result = subprocess.run(['git', 'remote', '-v'], 
                               capture_output=True, text=True, check=True)
        
        # Process each line
        for line in result.stdout.splitlines():
            parts = line.split()
            if len(parts) >= 2:
                remote_name = parts[0]
                remote_url = parts[1]
                
                # Convert URL and print result
                https_url = convert_ssh_to_https(remote_url)
                print(f"{remote_name}\t{https_url}")
    
    except subprocess.CalledProcessError:
        print("Error: Not a git repository or git command failed")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()