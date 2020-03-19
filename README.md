# install-jdk

A simple python utility that can be used to download and install a give Java JDK or JRE. Utilizes the [AdoptOpenJDK API](https://api.adoptopenjdk.net/swagger-ui/#/Binary).

This is a port of from the GitHub Action [`installjdk`](https://github.com/AdoptOpenJDK/install-jdk)

Currently supports 32-bit and 64-bit versions of Windows, Linux, and macOS.

## Install

```bash
pip install install-jdk
```

## Usage

```python
import jdk

jdk.install('11')
# Platform dependent install of Java JDK 11 into $HOME/.jdk/<VERSION>

jdk.install('11', impl=jdk.Implementation.OPENJ9)
# Platform dependent install of Java JDK 11 with OpenJ9 into $HOME/.jdk/<VERSION>

jdk.install('11', jre=True)
# Platform dependent install of Java JRE 11 into $HOME/.jre/<VERSION>

print(jdk.OS)       # Detected platform operating system
print(jdk.ARCH)     # Detected platform CPU architecture

download_url = jdk.get_download_url('11')
print(download_url)
# Obtains the platform dependent JDK download url

download_url = jdk.get_download_url('11', jre=True)
print(download_url)
# Obtains the platform dependent JRE download url

jdk.uninstall('11')
# Removes the Java 11 JDK if installed

jdk.uninstall('11', jre=True)
# Removes the Java 11 JRE if installed
```

## Development

Targets Python3.6 and newer.

```bash
git clone https://github.com/jyksnw/install-jdk
cd install-jdk
python3 -m venv .env
source .env/bin/activate

pip install -r dev_requirements.txt
```