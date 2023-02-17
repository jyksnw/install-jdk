# install-jdk

[WORK IN PROGRESS]
This client is currently being revamped for a v1.0 release. With added support for additional OpenJDK Build clients. Currently the updates support Adoptium and Corretto. The underlying library that drives this client is also being revamped to enable additional functionality down the road. The initial pre-release of v0.x methods and exposed API calls will be maintained for backwards compatibility.

A simple python utility that can be used to download and install a given Java JDK or JRE. Utilizes the [AdoptOpenJDK API](https://api.adoptopenjdk.net/swagger-ui/#/Binary).

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

jdk.install('17', vendor='Corretto')
# Installs a Corretto build of Java 17 JDK. Defualt vendor is Adoptium
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
